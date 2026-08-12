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
import urllib.parse
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

#: Companies mit ``lifecyclestage = 'customer'``, die fachlich keine Kunden sind.
#: Sie fliegen aus der Basisabfrage und damit aus allen Routinen und
#: MRR-Anteilen. Jeder Eintrag ist eine Umgehung falscher CRM-Daten, keine
#: Dauerlösung: solange hier etwas steht, gehört es im CRM korrigiert. Die
#: Routine weist die Liste im Block *Datenqualität* aus, damit sie nicht in
#: Vergessenheit gerät.
NON_CUSTOMERS: dict[str, str] = {
    "401316842690": "d.velop -- kein Kunde (Angabe Moritz, 12.08.2026); "
    "lifecyclestage im CRM noch 'customer'",
}

#: Schwellen (Tage seit letzter Sales-Aktivität) für die Ampel.
ACTIVITY_WARN_DAYS = 60
ACTIVITY_CRITICAL_DAYS = 180

API_BASE = "https://api.hubapi.com"
COMPANY_SEARCH_PATH = "/crm/v3/objects/companies/search"

#: Für Record-Links. Der Account liegt in der EU-Region, deshalb ``app-eu1``
#: und nicht ``app`` -- ein Link auf die falsche Region landet auf einer
#: Fehlerseite. Beides über ``GET /account-info/v3/details`` verifiziert.
PORTAL_ID = "145132698"
UI_DOMAIN = "app-eu1.hubspot.com"

#: Deal-Pipelines. IDs sind stabil, Labels dienen nur der Ausgabe.
SALES_PIPELINE = "default"
UPSELL_PIPELINE = "853703913"
ONBOARDING_PIPELINE = "873293029"

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

#: Alle Properties, die die Routinen auf DEAL brauchen.
DEAL_PROPERTIES = [
    "dealname",
    "dealstage",
    "pipeline",
    "amount",
    "closedate",
    "createdate",
    "hs_is_closed",
    "hs_is_closed_won",
    "hubspot_owner_id",
    "hs_lastmodifieddate",
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


def company_url(company_id: str) -> str:
    return f"https://{UI_DOMAIN}/contacts/{PORTAL_ID}/record/0-2/{company_id}"


def deal_url(deal_id: str) -> str:
    return f"https://{UI_DOMAIN}/contacts/{PORTAL_ID}/record/0-3/{deal_id}"


def md_link(label: str, url: str) -> str:
    """Markdown-Link mit escapten Klammern im Label.

    Notion und Markdown stolpern beide über eckige Klammern im Linktext;
    Firmennamen wie ``igus SE & Co. KG.`` sind unkritisch, aber der Escape
    kostet nichts.
    """
    safe = label.replace("[", "\\[").replace("]", "\\]")
    return f"[{safe}]({url})"


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
_EXCLUDED_CACHE: list[dict[str, Any]] = []


def active_customers(refresh: bool = False) -> list[dict[str, Any]]:
    """Die eine Basisabfrage: aktive Kunden, normalisiert.

    Alle Routinen bauen darauf auf. Bewusst *ohne* Zeitfenster-Filter -- die
    Fenster werden in Python gebildet, damit dieselbe Abfrage auch die Kunden
    ohne oder mit abgelaufenem Vertragsdatum sichtbar macht. Genau die fehlen,
    wenn man das Fenster in SQL filtert.

    Companies aus ``NON_CUSTOMERS`` werden hier entfernt -- vor jeder
    MRR-Summe, damit Anteile nicht gegen eine falsche Basis laufen.
    """
    global _ACTIVE_CACHE, _EXCLUDED_CACHE
    if _ACTIVE_CACHE is not None and not refresh:
        return _ACTIVE_CACHE
    rows = [normalize_company(row) for row in run_sql(ACTIVE_CUSTOMERS_SQL, "active_customers")]
    _EXCLUDED_CACHE = [row for row in rows if row["id"] in NON_CUSTOMERS]
    _ACTIVE_CACHE = [row for row in rows if row["id"] not in NON_CUSTOMERS]
    return _ACTIVE_CACHE


def excluded_non_customers() -> list[dict[str, Any]]:
    """Die per ``NON_CUSTOMERS`` entfernten Companies, mit Begründung."""
    active_customers()
    return [{**row, "reason": NON_CUSTOMERS[row["id"]]} for row in _EXCLUDED_CACHE]


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


# --------------------------------------------------------------------------
# Deals
# --------------------------------------------------------------------------

_DEALS_CACHE: list[dict[str, Any]] | None = None
_PIPELINES_CACHE: dict[str, dict[str, str]] | None = None

DEALS_SQL = """
SELECT hs_object_id, dealname, dealstage, pipeline, amount, closedate,
       createdate, hs_is_closed, hs_is_closed_won, hubspot_owner_id,
       COMPANY.name
FROM DEAL
""".strip()


def association_company_ids(record: dict[str, Any]) -> list[str]:
    """Company-IDs eines Deals, dedupliziert.

    Die Associations-API liefert dieselbe Company mehrfach, einmal je
    Association-Typ (``deal_to_company`` und ``deal_to_company_unlabeled``).
    Ohne Deduplizierung zählt fast jeder Deal doppelt: 367 von 413 Deals sehen
    dann wie Mehrfachverknüpfungen aus, tatsächlich sind es drei.
    """
    results = ((record.get("associations") or {}).get("companies") or {}).get("results") or []
    seen: dict[str, None] = {}
    for entry in results:
        identifier = str(entry.get("id") or "").strip()
        if identifier:
            seen.setdefault(identifier, None)
    return list(seen)


def deals(refresh: bool = False) -> list[dict[str, Any]]:
    """Alle Deals mit Company-Verknüpfung, normalisiert.

    Nur im API-Modus verfügbar: die Verknüpfung kommt aus der Associations-API,
    die MCP-SQL liefert stattdessen ``COMPANY.name`` -- über Namen zu joinen
    wäre bei den vorhandenen Dubletten unzuverlässig. Ohne Token gibt die
    Funktion eine leere Liste zurück, und die Routinen lassen den Deal-Teil
    weg statt falsch zu rechnen.
    """
    global _DEALS_CACHE
    if _DEALS_CACHE is not None and not refresh:
        return _DEALS_CACHE
    token = _access_token()
    if token is None:
        _DEALS_CACHE = []
        return _DEALS_CACHE

    rows: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        query = {
            "limit": "100",
            "properties": ",".join(DEAL_PROPERTIES),
            "associations": "companies",
        }
        if after:
            query["after"] = after
        response = _get_json("/crm/v3/objects/deals?" + urllib.parse.urlencode(query), token)
        for record in response.get("results", []):
            rows.append(normalize_deal(record))
        after = (response.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
    _DEALS_CACHE = rows
    return rows


def normalize_deal(record: dict[str, Any]) -> dict[str, Any]:
    props = record.get("properties") or {}
    identifier = str(record.get("id") or props.get("hs_object_id") or "").strip()
    return {
        "id": identifier,
        "name": html.unescape(str(props.get("dealname") or "")).strip() or "(ohne Namen)",
        "pipeline": str(props.get("pipeline") or "").strip(),
        "stage": str(props.get("dealstage") or "").strip(),
        "amount": to_float(props.get("amount")),
        "close_date": ms_to_date(props.get("closedate")),
        "create_date": ms_to_date(props.get("createdate")),
        "is_closed": str(props.get("hs_is_closed") or "").lower() == "true",
        "is_won": str(props.get("hs_is_closed_won") or "").lower() == "true",
        "owner_id": (str(props.get("hubspot_owner_id") or "").strip() or None),
        "company_ids": association_company_ids(record),
        "url": deal_url(identifier),
    }


def deals_by_company(refresh: bool = False) -> dict[str, list[dict[str, Any]]]:
    """Company-ID -> Deals. Ein Deal kann bei mehreren Companies auftauchen."""
    mapping: dict[str, list[dict[str, Any]]] = {}
    for deal in deals(refresh=refresh):
        for company_id in deal["company_ids"]:
            mapping.setdefault(company_id, []).append(deal)
    return mapping


def pipeline_labels() -> dict[str, dict[str, str]]:
    """Stage-ID -> ``{"pipeline": Label, "stage": Label}``.

    IDs sind in den Rohdaten nicht lesbar (``1238245574``), im Brief soll
    "Onboarding / Setup in Progress" stehen.
    """
    global _PIPELINES_CACHE
    if _PIPELINES_CACHE is not None:
        return _PIPELINES_CACHE
    token = _access_token()
    if token is None:
        _PIPELINES_CACHE = {}
        return _PIPELINES_CACHE
    labels: dict[str, dict[str, str]] = {}
    response = _get_json("/crm/v3/pipelines/deals", token)
    for pipeline in response.get("results", []):
        for stage in pipeline.get("stages", []):
            labels[str(stage.get("id"))] = {
                "pipeline": pipeline.get("label") or str(pipeline.get("id")),
                "stage": stage.get("label") or str(stage.get("id")),
            }
    _PIPELINES_CACHE = labels
    return labels


def stage_label(deal: dict[str, Any]) -> str:
    labels = pipeline_labels().get(deal["stage"])
    if not labels:
        return f"{deal['pipeline']}/{deal['stage']}"
    return f"{labels['pipeline']} / {labels['stage']}"


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
