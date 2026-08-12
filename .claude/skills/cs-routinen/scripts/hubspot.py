"""Gemeinsamer HubSpot-Zugriff für alle CS-Routinen.

Zwei Betriebsmodi, in dieser Reihenfolge:

1. **API-Modus** (bevorzugt für automatisierte Läufe): Wenn ``HUBSPOT_ACCESS_TOKEN``
   gesetzt ist, wird die CRM-Search-API direkt aufgerufen, inkl. Paging und Retry.
2. **MCP-Cache-Modus** (Standard in einer Claude-Code-Session): Ohne Token liest
   das Modul die JSON-Dumps aus ``cs-routinen/data/``. Claude führt dazu die in
   ``references/queries.md`` benannten Queries per ``mcp__HubSpot__query_crm_data``
   aus und legt die Tool-Antwort unverändert als ``data/<query_name>.json`` ab.
   ``parse_mcp_results`` versteht sowohl die rohe MCP-Antwort als auch eine
   einfache Liste von Property-Dicts.

Beide Modi liefern identisch normalisierte Zeilen, damit die Routinen-Skripte
nichts über die Herkunft der Daten wissen müssen.
"""

from __future__ import annotations

import html
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

# --------------------------------------------------------------------------
# Konstanten
# --------------------------------------------------------------------------

#: Support-Pipeline für Routine 2 (Tickets). Harte Konstante, keine Ableitung.
SUPPORT_PIPELINE = "0"

#: Standard-Kündigungsfrist in Monaten zum Laufzeitende. Sobald die
#: vertragliche Standardfrist verbindlich geklärt ist, hier anpassen -- alle
#: Fristenrechnungen der Renewal-Routine hängen an diesem Wert.
NOTICE_PERIOD_MONTHS = 3

#: Ab diesem MRR-Anteil an der Gesamtbasis gilt ein Kunde als Einzelrisiko.
TOP_RISK_MRR_SHARE = 0.05

#: Schwellen (Tage seit letzter Sales-Aktivität) für die Ampel.
ACTIVITY_WARN_DAYS = 60
ACTIVITY_CRITICAL_DAYS = 180

API_BASE = "https://api.hubapi.com"
COMPANY_SEARCH_PATH = "/crm/v3/objects/companies/search"

#: Alle Properties, die die Routinen auf COMPANY brauchen.
COMPANY_PROPERTIES = [
    "hs_object_id",
    "name",
    "domain",
    "lifecyclestage",
    "churn_date",
    "contract_start_date",
    "contract_end_date",
    "contract_duration_months_",
    "company_mrr",
    "contracted_users",
    "hubspot_owner_id",
    "hs_last_sales_activity_timestamp",
]

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

MAX_RETRIES = 4
BACKOFF_BASE_SECONDS = 2


class HubSpotError(RuntimeError):
    """Fehler beim Datenzugriff, mit Hinweis auf den fehlenden Modus."""


# --------------------------------------------------------------------------
# Konvertierung und Normalisierung
# --------------------------------------------------------------------------


def to_float(value: Any) -> float | None:
    """HubSpot liefert Zahlen als String und leere Felder als ''."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def to_int(value: Any) -> int | None:
    number = to_float(value)
    return None if number is None else int(number)


def to_ms(value: Any) -> int | None:
    """Millisekunden-Timestamp aus einem HubSpot-Datumsfeld."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    # ISO-Varianten ('2026-09-01T00:00:00Z', '2026-09-01')
    iso = text.replace("Z", "+00:00")
    for parser in (datetime.fromisoformat,):
        try:
            parsed = parser(iso)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)
    return None


def ms_to_datetime(value: Any) -> datetime | None:
    ms = to_ms(value)
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def ms_to_date(value: Any) -> date | None:
    moment = ms_to_datetime(value)
    return None if moment is None else moment.date()


def ms_to_days(value: Any) -> float | None:
    """Millisekunden-Dauer in Tage. Für Alter/Durchlaufzeiten."""
    ms = to_ms(value)
    return None if ms is None else ms / 86_400_000


def ms_to_hours(value: Any) -> float | None:
    """Millisekunden-Dauer in Stunden. Für Reaktionszeiten in Routine 2."""
    ms = to_ms(value)
    return None if ms is None else ms / 3_600_000


def norm_name(value: Any) -> str:
    """Firmenname für den Cross-Object-Join vereinheitlichen.

    HubSpot liefert Namen HTML-escaped ('Lanes &amp; Planes'), teils mit
    doppelten Leerzeichen. Reihenfolge: unescape, Whitespace normalisieren,
    strip, lower.
    """
    if value is None:
        return ""
    text = html.unescape(str(value))
    return re.sub(r"\s+", " ", text).strip().lower()


LEGAL_SUFFIXES = (
    "gmbh & co. kg",
    "gmbh & co kg",
    "se & co. kg",
    "se & co kg",
    "gmbh",
    "ag",
    "se",
    "kg",
    "ohg",
    "e.k.",
    "ug",
    "inc.",
    "inc",
    "ltd.",
    "ltd",
    "b.v.",
    "bv",
    "oy",
    "gruppe",
    "group",
)


def dedupe_key(value: Any) -> str:
    """Aggressivere Normalisierung -- nur für die Dubletten-Erkennung.

    Nicht für Joins verwenden: 'igus GmbH' und 'igus SE & Co. KG.' fallen hier
    absichtlich auf denselben Schlüssel.
    """
    text = norm_name(value).rstrip(".")
    changed = True
    while changed:
        changed = False
        for suffix in LEGAL_SUFFIXES:
            if text.endswith(" " + suffix):
                text = text[: -len(suffix) - 1].rstrip(" .,")
                changed = True
    return re.sub(r"[^a-z0-9]", "", text)


def add_months(anchor: date, months: int) -> date:
    """Monatsarithmetik ohne externe Abhängigkeit, Monatsende-sicher."""
    total = anchor.month - 1 + months
    year = anchor.year + total // 12
    month = total % 12 + 1
    day = min(anchor.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - timedelta(days=1)).day


def days_between(start: date, end: date) -> int:
    return (end - start).days


def fmt_eur(value: float | None, dash: str = "-") -> str:
    """Deutsche Zahlenformatierung: 1.110,84."""
    if value is None:
        return dash
    formatted = f"{value:,.2f}"
    return formatted.replace(",", "#").replace(".", ",").replace("#", ".")


def fmt_date(value: date | None, dash: str = "-") -> str:
    return dash if value is None else value.strftime("%d.%m.%Y")


def fmt_pct(share: float | None, dash: str = "-") -> str:
    if share is None:
        return dash
    return f"{share * 100:.1f}".replace(".", ",") + " %"


# --------------------------------------------------------------------------
# API-Modus
# --------------------------------------------------------------------------


#: Erste gesetzte Variable gewinnt.
TOKEN_ENV_VARS = ("HUBSPOT_PRIVATE_APP_TOKEN", "HUBSPOT_ACCESS_TOKEN")


def _access_token() -> str | None:
    for name in TOKEN_ENV_VARS:
        token = os.environ.get(name, "").strip()
        if token:
            return token
    return None


def _post_json(path: str, payload: dict[str, Any], token: str) -> dict[str, Any]:
    """POST mit Retry: 4 Versuche, Backoff 2s/4s/8s/16s, Retry-After beachtet."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_BASE + path,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in (429, 500, 502, 503, 504):
                detail = error.read().decode("utf-8", "replace")[:500]
                raise HubSpotError(f"HubSpot {error.code}: {detail}") from error
            wait = float(error.headers.get("Retry-After") or 0) or (
                BACKOFF_BASE_SECONDS * (2**attempt)
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            wait = BACKOFF_BASE_SECONDS * (2**attempt)
        if attempt < MAX_RETRIES - 1:
            time.sleep(wait)
    raise HubSpotError(f"HubSpot nach {MAX_RETRIES} Versuchen nicht erreichbar: {last_error}")


def _get_json(path: str, token: str) -> dict[str, Any]:
    """GET mit derselben Retry-Logik wie ``_post_json``."""
    request = urllib.request.Request(
        API_BASE + path,
        method="GET",
        headers={"Authorization": f"Bearer {token}"},
    )
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in (429, 500, 502, 503, 504):
                detail = error.read().decode("utf-8", "replace")[:500]
                raise HubSpotError(f"HubSpot {error.code}: {detail}") from error
            wait = float(error.headers.get("Retry-After") or 0) or (
                BACKOFF_BASE_SECONDS * (2**attempt)
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            wait = BACKOFF_BASE_SECONDS * (2**attempt)
        if attempt < MAX_RETRIES - 1:
            time.sleep(wait)
    raise HubSpotError(f"HubSpot nach {MAX_RETRIES} Versuchen nicht erreichbar: {last_error}")


def search_companies(
    filter_groups: list[dict[str, Any]],
    properties: Iterable[str] = COMPANY_PROPERTIES,
    page_size: int = 100,
) -> list[dict[str, Any]]:
    """Gepaginierte COMPANY-Suche. Gibt rohe Property-Dicts zurück."""
    token = _access_token()
    if token is None:
        raise HubSpotError("HUBSPOT_ACCESS_TOKEN nicht gesetzt")
    rows: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        payload: dict[str, Any] = {
            "filterGroups": filter_groups,
            "properties": list(properties),
            "limit": page_size,
        }
        if after:
            payload["after"] = after
        response = _post_json(COMPANY_SEARCH_PATH, payload, token)
        for record in response.get("results", []):
            props = dict(record.get("properties") or {})
            props.setdefault("hs_object_id", record.get("id"))
            rows.append(props)
        after = (response.get("paging") or {}).get("next", {}).get("after")
        if not after:
            return rows


# --------------------------------------------------------------------------
# MCP-Cache-Modus
# --------------------------------------------------------------------------


def parse_mcp_results(payload: Any) -> list[dict[str, Any]]:
    """Property-Dicts aus einer MCP-Antwort oder einer einfachen Liste lesen.

    Akzeptiert:
      * ``{"results": [{"content": "{\\"properties\\": {...}}"}]}`` (MCP roh)
      * ``{"results": [{"properties": {...}}]}``
      * ``[{...}, {...}]`` (bereits flach)
    """
    if isinstance(payload, dict):
        records = payload.get("results", [])
    elif isinstance(payload, list):
        records = payload
    else:
        raise HubSpotError(f"Unerwartetes Cache-Format: {type(payload).__name__}")

    rows: list[dict[str, Any]] = []
    for record in records:
        if isinstance(record, str):
            record = json.loads(record)
        if not isinstance(record, dict):
            continue
        content = record.get("content")
        if isinstance(content, str):
            stripped = content.strip()
            if not stripped.startswith("{"):
                # Aggregat-Antworten der MCP kommen als TSV-Text, nicht als Zeilen.
                raise HubSpotError(
                    "Cache enthält eine Aggregat-Antwort (TSV) statt Datensätzen. "
                    "Für die Routinen bitte die Detail-Query cachen."
                )
            record = json.loads(stripped)
        props = record.get("properties")
        rows.append(dict(props) if isinstance(props, dict) else dict(record))
    return rows


def load_cache(query_name: str) -> list[dict[str, Any]]:
    path = DATA_DIR / f"{query_name}.json"
    if not path.exists():
        raise HubSpotError(
            f"Kein Token und kein Cache: {path} fehlt.\n"
            f"Entweder {' oder '.join(TOKEN_ENV_VARS)} setzen oder die Query "
            f"'{query_name}' aus references/queries.md per MCP ausführen und die "
            f"Antwort nach {path} schreiben."
        )
    return parse_mcp_results(json.loads(path.read_text(encoding="utf-8")))


def save_cache(query_name: str, payload: Any) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{query_name}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_sql(sql: str, cache_key: str) -> list[dict[str, Any]]:
    """Query ausführen -- API wenn möglich, sonst MCP-Cache.

    ``sql`` ist die dokumentierte Fassung aus ``references/queries.md``. Im
    API-Modus wird sie nicht interpretiert; dort greift die registrierte
    Search-API-Übersetzung zu ``cache_key``. Damit bleibt genau eine Definition
    pro Query, und der Cache-Modus funktioniert ohne Token.
    """
    if _access_token() is not None and cache_key in SEARCH_TRANSLATIONS:
        return search_companies(SEARCH_TRANSLATIONS[cache_key]())
    return load_cache(cache_key)


# --------------------------------------------------------------------------
# Basisabfrage
# --------------------------------------------------------------------------

ACTIVE_CUSTOMERS_SQL = """
SELECT hs_object_id, name, domain, contract_start_date, contract_end_date,
       contract_duration_months_, company_mrr, contracted_users,
       hubspot_owner_id, hs_last_sales_activity_timestamp
FROM COMPANY
WHERE lifecyclestage = 'customer'
  AND churn_date IS NULL
""".strip()


def _active_customers_filters() -> list[dict[str, Any]]:
    return [
        {
            "filters": [
                {
                    "propertyName": "lifecyclestage",
                    "operator": "EQ",
                    "value": "customer",
                },
                {"propertyName": "churn_date", "operator": "NOT_HAS_PROPERTY"},
            ]
        }
    ]


#: Query-Name -> Filter-Builder für den API-Modus.
SEARCH_TRANSLATIONS: dict[str, Any] = {
    "active_customers": _active_customers_filters,
}

_ACTIVE_CACHE: list[dict[str, Any]] | None = None


def active_customers(refresh: bool = False) -> list[dict[str, Any]]:
    """Die eine Basisabfrage: aktive Kunden, normalisiert.

    Alle Routinen bauen darauf auf. Bewusst *ohne* Zeitfenster-Filter -- die
    Fenster werden in Python gebildet, damit dieselbe Abfrage auch die Kunden
    ohne oder mit abgelaufenem Vertragsdatum sichtbar macht. Genau die fehlen,
    wenn man das Fenster in SQL filtert.
    """
    global _ACTIVE_CACHE
    if _ACTIVE_CACHE is not None and not refresh:
        return _ACTIVE_CACHE
    rows = run_sql(ACTIVE_CUSTOMERS_SQL, "active_customers")
    _ACTIVE_CACHE = [normalize_company(row) for row in rows]
    return _ACTIVE_CACHE


def normalize_company(row: dict[str, Any]) -> dict[str, Any]:
    """Rohe Properties in typisierte, einheitliche Felder überführen."""
    name = html.unescape(str(row.get("name") or "")).strip()
    return {
        "id": str(row.get("hs_object_id") or "").strip(),
        "name": name,
        "name_key": norm_name(name),
        "dedupe_key": dedupe_key(name),
        "domain": (str(row.get("domain") or "").strip() or None),
        "owner_id": (str(row.get("hubspot_owner_id") or "").strip() or None),
        "mrr": to_float(row.get("company_mrr")),
        "contracted_users": to_int(row.get("contracted_users")),
        "contract_start": ms_to_date(row.get("contract_start_date")),
        "contract_end": ms_to_date(row.get("contract_end_date")),
        "duration_months": to_int(row.get("contract_duration_months_")),
        "last_activity": ms_to_date(row.get("hs_last_sales_activity_timestamp")),
        "raw": row,
    }


def total_mrr(customers: Iterable[dict[str, Any]] | None = None) -> float:
    rows = active_customers() if customers is None else customers
    return sum(row["mrr"] or 0.0 for row in rows)


def owner_info() -> dict[str, dict[str, Any]]:
    """Owner-ID -> ``{"name": str, "active": bool}``.

    Im API-Modus werden aktive *und* archivierte Owner geladen -- letztere sind
    genau die ausgeschiedenen Kollegen, auf deren Namen noch Kunden laufen.
    Ohne Token dient ``data/owners.json`` als Quelle; akzeptiert die rohe
    Antwort von ``mcp__HubSpot__search_owners`` oder ein flaches Mapping.
    """
    token = _access_token()
    if token is not None:
        owners: dict[str, dict[str, Any]] = {}
        for archived in ("false", "true"):
            response = _get_json(f"/crm/v3/owners?limit=100&archived={archived}", token)
            for owner in response.get("results", []):
                name = " ".join(
                    part
                    for part in (owner.get("firstName"), owner.get("lastName"))
                    if part
                ).strip()
                owners[str(owner.get("id"))] = {
                    "name": name or owner.get("email") or str(owner.get("id")),
                    "active": archived == "false" and not owner.get("archived"),
                }
        return owners

    path = DATA_DIR / "owners.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "owners" in payload:
        return {
            str(owner["ownerId"]): {
                "name": owner.get("name") or str(owner["ownerId"]),
                "active": bool(owner.get("isActive", True)),
            }
            for owner in payload["owners"]
        }
    return {
        str(key): {"name": str(value), "active": True}
        for key, value in dict(payload).items()
    }


def today(as_of: str | None = None) -> date:
    """Stichtag der Routine. ``as_of`` (YYYY-MM-DD) macht Läufe reproduzierbar."""
    if as_of:
        return date.fromisoformat(as_of)
    return datetime.now(timezone.utc).date()
