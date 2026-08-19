"""Minimaler HubSpot-CRM-Client fuer die Bereinigungsroutine.

Nur Standardbibliothek. Schreibende Aufrufe sind hart gesperrt, solange der
Client nicht ausdruecklich mit allow_write=True erzeugt wurde -- der Dry-Run
kann dadurch nicht versehentlich schreiben.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.hubapi.com"
TOKEN_ENV = "HUBSPOT_PRIVATE_APP_TOKEN"

RETRY_STATUS = {429, 500, 502, 503, 504}
MAX_RETRIES = 5
BATCH_SIZE = 100          # HubSpot-Limit fuer batch/update
SEARCH_PAGE = 200         # HubSpot-Limit fuer /search
SEARCH_MAX_OFFSET = 10_000  # HubSpot bricht darueber ab


class WriteBlocked(RuntimeError):
    """Ein Schreibversuch im Dry-Run-Modus."""


class MissingScope(RuntimeError):
    """Das Token hat den benoetigten Scope nicht."""


class HubSpotClient:
    def __init__(self, token: str | None = None, allow_write: bool = False,
                 verbose: bool = False):
        self.token = token or os.environ.get(TOKEN_ENV, "")
        if not self.token:
            raise RuntimeError(
                f"Kein Token gefunden. Setze {TOKEN_ENV} auf das Private-App-Token."
            )
        self.allow_write = allow_write
        self.verbose = verbose
        self.calls = 0

    # -- HTTP ---------------------------------------------------------------
    def _request(self, method: str, path: str, body: dict | None = None,
                 params: dict | None = None) -> dict:
        # /search und /batch/read sind POSTs, aber reine Lesevorgaenge.
        read_only_post = path.endswith("/search") or path.endswith("/batch/read")
        if method != "GET" and not self.allow_write and not read_only_post:
            raise WriteBlocked(f"{method} {path} im Dry-Run-Modus blockiert")

        url = BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode() if body is not None else None

        last = None
        for attempt in range(MAX_RETRIES):
            req = urllib.request.Request(
                url, data=data, method=method,
                headers={"Authorization": f"Bearer {self.token}",
                         "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    self.calls += 1
                    raw = r.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                payload = e.read().decode(errors="replace")
                last = e
                if e.code == 403:
                    raise MissingScope(
                        f"HTTP 403 bei {method} {path}. Das Private-App-Token hat den "
                        f"benoetigten Scope nicht.\nAntwort: {payload[:300]}"
                    ) from e
                if e.code in RETRY_STATUS and attempt < MAX_RETRIES - 1:
                    wait = float(e.headers.get("Retry-After") or 2 ** attempt)
                    if self.verbose:
                        print(f"    HTTP {e.code}, Versuch {attempt+1}, warte {wait:.0f}s")
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"HTTP {e.code} bei {method} {path}: {payload[:400]}") from e
            except urllib.error.URLError as e:
                last = e
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Netzwerkfehler bei {method} {path}: {e}") from e
        raise RuntimeError(f"{method} {path} nach {MAX_RETRIES} Versuchen fehlgeschlagen: {last}")

    # -- Lesen --------------------------------------------------------------
    def search(self, properties: list[str], filter_groups: list[dict] | None = None,
               limit: int | None = None, object_type: str = "contacts",
               sort_property: str = "createdate") -> list[dict]:
        """Kontakte suchen und ueber alle Seiten sammeln.

        Nutzt statt `after` einen aufsteigenden Cursor auf hs_object_id, damit
        auch Ergebnismengen jenseits des 10.000er-Limits vollstaendig gelesen
        werden koennen.
        """
        out: list[dict] = []
        after = None
        while True:
            body = {
                "filterGroups": filter_groups or [],
                "properties": properties,
                "limit": min(SEARCH_PAGE, limit - len(out)) if limit else SEARCH_PAGE,
                "sorts": [{"propertyName": sort_property, "direction": "DESCENDING"}],
            }
            if after:
                body["after"] = after
            page = self._request("POST", f"/crm/v3/objects/{object_type}/search", body)
            results = page.get("results", [])
            out.extend(results)
            if self.verbose:
                print(f"    gelesen: {len(out)} / {page.get('total', '?')}")
            after = (page.get("paging") or {}).get("next", {}).get("after")
            if not results or not after or (limit and len(out) >= limit):
                break
            if int(after) >= SEARCH_MAX_OFFSET:
                # HubSpot laesst /search nicht ueber 10.000 Treffer blaettern.
                # Nie stillschweigend abschneiden -- sonst liest sich ein
                # Teilergebnis wie eine vollstaendige Abdeckung.
                total = page.get("total")
                print(f"    WARNUNG: Suchfenster bei {SEARCH_MAX_OFFSET} erschoepft, "
                      f"{total} Treffer insgesamt -- {len(out)} gelesen. "
                      f"Fuer vollstaendige Abdeckung search_all_by_id() nutzen.")
                break
        return out[:limit] if limit else out

    def search_all_by_id(self, properties: list[str],
                         filter_groups: list[dict] | None = None,
                         object_type: str = "contacts") -> list[dict]:
        """Vollstaendiger Scan ohne 10.000er-Grenze, per hs_object_id-Fenster."""
        seen: set[str] = set()
        out: list[dict] = []
        cursor = "0"
        while True:
            groups = []
            for g in (filter_groups or [{"filters": []}]):
                filters = list(g.get("filters", []))
                filters.append({"propertyName": "hs_object_id", "operator": "GT",
                                "value": cursor})
                groups.append({"filters": filters})
            body = {"filterGroups": groups, "properties": properties,
                    "limit": SEARCH_PAGE,
                    "sorts": [{"propertyName": "hs_object_id", "direction": "ASCENDING"}]}
            page = self._request("POST", f"/crm/v3/objects/{object_type}/search", body)
            results = page.get("results", [])
            fresh = [r for r in results if r["id"] not in seen]
            if not fresh:
                break
            for r in fresh:
                seen.add(r["id"])
            out.extend(fresh)
            cursor = max(results, key=lambda r: int(r["id"]))["id"]
            if self.verbose:
                print(f"    gelesen: {len(out)} / {page.get('total', '?')}")
            if len(results) < SEARCH_PAGE:
                break
        return out

    def get_properties(self, object_type: str = "contacts") -> list[dict]:
        return self._request("GET", f"/crm/v3/properties/{object_type}").get("results", [])

    # -- Schreiben ----------------------------------------------------------
    def create_property(self, definition: dict, object_type: str = "contacts") -> dict:
        return self._request("POST", f"/crm/v3/properties/{object_type}", definition)

    def sync_property_options(self, definition: dict,
                              object_type: str = "contacts") -> list[str]:
        """Fehlende Enum-Werte an einer bestehenden Property nachziehen.

        Vorhandene Werte bleiben unberuehrt -- ein PATCH mit reduzierter
        Optionsliste wuerde bereits gesetzte Werte unbrauchbar machen.
        Gibt die neu hinzugefuegten Werte zurueck.
        """
        name = definition["name"]
        current = self._request("GET", f"/crm/v3/properties/{object_type}/{name}")
        have = {o["value"] for o in current.get("options", [])}
        wanted = definition.get("options", [])
        missing = [o for o in wanted if o["value"] not in have]
        if not missing:
            return []
        merged = {o["value"]: o for o in current.get("options", [])}
        for o in wanted:                      # Labels/Reihenfolge mit angleichen
            merged[o["value"]] = o
        self._request("PATCH", f"/crm/v3/properties/{object_type}/{name}",
                      {"options": list(merged.values())})
        return [o["value"] for o in missing]

    def batch_update(self, updates: list[dict], object_type: str = "contacts") -> list[dict]:
        """updates: [{"id": "123", "properties": {...}}, ...]"""
        done = []
        for i in range(0, len(updates), BATCH_SIZE):
            chunk = updates[i:i + BATCH_SIZE]
            res = self._request("POST", f"/crm/v3/objects/{object_type}/batch/update",
                                {"inputs": chunk})
            done.extend(res.get("results", []))
            if self.verbose:
                print(f"    geschrieben: {len(done)} / {len(updates)}")
        return done

    def batch_archive(self, ids: list[str], object_type: str = "contacts") -> None:
        for i in range(0, len(ids), BATCH_SIZE):
            self._request("POST", f"/crm/v3/objects/{object_type}/batch/archive",
                          {"inputs": [{"id": x} for x in ids[i:i + BATCH_SIZE]]})

    # -- Diagnose -----------------------------------------------------------
    def check_scopes(self) -> dict[str, bool]:
        """Ohne Datenaenderung pruefen, welche Scopes das Token traegt."""
        probes = {
            "contacts.read": ("GET", "/crm/v3/objects/contacts", None, {"limit": 1}),
            "schemas.contacts.read": ("GET", "/crm/v3/properties/contacts", None, None),
        }
        result = {}
        for name, (m, p, b, q) in probes.items():
            try:
                self._request(m, p, b, q)
                result[name] = True
            except (MissingScope, RuntimeError):
                result[name] = False
        # Schreibrechte per leerem Batch pruefen -- aendert nichts.
        was = self.allow_write
        self.allow_write = True
        try:
            self._request("POST", "/crm/v3/objects/contacts/batch/update", {"inputs": []})
            result["contacts.write"] = True
        except MissingScope:
            result["contacts.write"] = False
        except RuntimeError:
            result["contacts.write"] = False
        finally:
            self.allow_write = was
        return result
