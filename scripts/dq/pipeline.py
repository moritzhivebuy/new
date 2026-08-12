"""Phasen der Bereinigungsroutine.

Jede Phase liest Kontakte, wendet die Regeln aus rules.py an und erzeugt
Change-Objekte. Geschrieben wird hier nichts -- das macht run.py, und nur
gegen eine freigegebene CSV.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import rules
from .client import HubSpotClient
from .rules import HIGH, LOW, MEDIUM

# Properties, die die Routine anlegt (Phase 00).
DQ_PROPERTIES = [
    {"name": "dq_status", "label": "Datenqualität Status", "type": "enumeration",
     "fieldType": "select", "groupName": "contactinformation",
     "description": "Ergebnis des letzten Datenqualitätslaufs.",
     "options": [{"label": "OK", "value": "ok", "displayOrder": 0},
                 {"label": "Automatisch bereinigt", "value": "auto_bereinigt", "displayOrder": 1},
                 {"label": "Prüfen", "value": "pruefen", "displayOrder": 2},
                 {"label": "Funktionspostfach", "value": "funktionspostfach", "displayOrder": 3},
                 {"label": "Unbrauchbar", "value": "unbrauchbar", "displayOrder": 4}]},
    {"name": "kontakt_typ", "label": "Kontakt Typ", "type": "enumeration",
     "fieldType": "select", "groupName": "contactinformation",
     "description": "Echte Person oder Sammel-/Funktionspostfach.",
     "options": [{"label": "Person", "value": "Person", "displayOrder": 0},
                 {"label": "Funktionspostfach", "value": "Funktionspostfach", "displayOrder": 1}]},
    {"name": "name_quelle", "label": "Namensquelle", "type": "enumeration",
     "fieldType": "select", "groupName": "contactinformation",
     "description": "Woher Vor- und Nachname stammen. 'manuell' wird von der "
                    "Routine nie überschrieben.",
     "options": [{"label": "Manuell", "value": "manuell", "displayOrder": 0},
                 {"label": "Aus E-Mail abgeleitet", "value": "aus_email_abgeleitet",
                  "displayOrder": 1},
                 {"label": "Enrichment", "value": "enrichment", "displayOrder": 2}]},
    {"name": "dq_befund", "label": "Datenqualität Befund", "type": "string",
     "fieldType": "textarea", "groupName": "contactinformation",
     "description": "Welche Regel griff und welche Werte vorher drinstanden. "
                    "Grundlage für den Rollback."},
    {"name": "dq_letzte_pruefung", "label": "Datenqualität letzte Prüfung", "type": "date",
     "fieldType": "date", "groupName": "contactinformation",
     "description": "Datum des letzten Datenqualitätslaufs."},
]

# Properties, die jede Phase mindestens braucht.
READ_PROPS = ["firstname", "lastname", "email", "salutation", "phone", "mobilephone",
              "company", "jobtitle", "country", "city", "zip", "lifecyclestage",
              "hs_analytics_source", "hs_object_source_label", "hs_language",
              "createdate", "num_associated_deals", "dq_status", "kontakt_typ",
              "name_quelle", "contact_typ__channel_"]


@dataclass
class Change:
    contact_id: str
    phase: str
    field: str
    old: str
    new: str
    confidence: str
    reason: str
    email: str = ""

    @property
    def auto(self) -> bool:
        """Nur HIGH-Konfidenz darf ohne Menschen geschrieben werden."""
        return self.confidence == HIGH


@dataclass
class PhaseResult:
    phase: str
    title: str
    changes: list[Change] = field(default_factory=list)
    flags: list[Change] = field(default_factory=list)   # nur dq_status=pruefen
    deletes: list[tuple[str, str]] = field(default_factory=list)
    scanned: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def auto_count(self) -> int:
        return len({c.contact_id for c in self.changes if c.auto})

    @property
    def review_count(self) -> int:
        return len({c.contact_id for c in self.flags})


# Von der Routine selbst angelegte Properties. Vor Phase 00 existieren sie
# nicht -- dann darf weder darauf gefiltert noch danach gelesen werden, sonst
# antwortet die Search-API mit HTTP 400.
OPTIONAL_PROPS = {"dq_status", "kontakt_typ", "name_quelle", "dq_befund",
                  "dq_letzte_pruefung", "contact_typ__channel_"}

_available: set[str] | None = None


def available_props(client: HubSpotClient) -> set[str]:
    """Einmal ermitteln, welche Properties das Portal tatsächlich kennt."""
    global _available
    if _available is None:
        _available = {p["name"] for p in client.get_properties()}
    return _available


def _props(client: HubSpotClient) -> list[str]:
    """READ_PROPS auf die im Portal vorhandenen Properties eindampfen."""
    have = available_props(client)
    return [p for p in READ_PROPS if p not in OPTIONAL_PROPS or p in have]


def _filters(client: HubSpotClient, filters: list[dict]) -> list[dict]:
    """Filter auf noch nicht existierende Properties verwerfen."""
    have = available_props(client)
    keep, dropped = [], []
    for f in filters:
        name = f["propertyName"]
        if name in OPTIONAL_PROPS and name not in have:
            dropped.append(name)
            continue
        keep.append(f)
    if dropped:
        print(f"    Hinweis: Property fehlt noch, Filter übersprungen: "
              f"{', '.join(dropped)} (Phase 00 anlegen)")
    return keep


def _p(contact: dict, key: str) -> str:
    v = contact.get("properties", {}).get(key)
    return "" if v is None else str(v).strip()


def _protected(contact: dict) -> bool:
    """Manuell gepflegte Namen nicht anfassen (Leitplanke 05)."""
    return _p(contact, "name_quelle") == "manuell"


# ===========================================================================
# Phase 00 -- fehlende Properties melden
# ===========================================================================
def phase00_properties(client: HubSpotClient) -> PhaseResult:
    r = PhaseResult("00", "Properties für Nachvollziehbarkeit")
    existing = {p["name"] for p in client.get_properties()}
    for definition in DQ_PROPERTIES:
        if definition["name"] in existing:
            r.notes.append(f"vorhanden: {definition['name']}")
        else:
            r.notes.append(f"FEHLT: {definition['name']} ({definition['label']})")
    return r


# ===========================================================================
# Domain-Konventionen lernen
# ===========================================================================
def learn(client: HubSpotClient, sample: int = 4000) -> dict[str, rules.Convention]:
    """Konventionstabelle aus Kontakten mit vollstaendigem Namen lernen."""
    contacts = client.search(
        ["firstname", "lastname", "email"],
        [{"filters": [{"propertyName": "firstname", "operator": "HAS_PROPERTY"},
                      {"propertyName": "lastname", "operator": "HAS_PROPERTY"},
                      {"propertyName": "email", "operator": "HAS_PROPERTY"}]}],
        limit=sample)
    return rules.learn_conventions(contacts)


# ===========================================================================
# Phase 01 -- Geisterdatensaetze
# ===========================================================================
def phase01_ghosts(client: HubSpotClient) -> PhaseResult:
    r = PhaseResult("01", "Leere Geisterdatensätze")
    contacts = client.search(
        list(rules.GHOST_FIELDS) + ["num_associated_deals", "lifecyclestage",
                                    "hs_object_source_label", "createdate"],
        [{"filters": [{"propertyName": "email", "operator": "NOT_HAS_PROPERTY"},
                      {"propertyName": "firstname", "operator": "NOT_HAS_PROPERTY"},
                      {"propertyName": "lastname", "operator": "NOT_HAS_PROPERTY"}]}])
    r.scanned = len(contacts)
    for c in contacts:
        ghost, why = rules.is_ghost(c.get("properties", {}))
        if ghost:
            r.deletes.append((c["id"], why))
    r.notes.append(f"{len(r.deletes)} Löschkandidaten von {r.scanned} namenlosen ohne E-Mail")
    return r


# ===========================================================================
# Phase 02 -- Funktionspostfaecher
# ===========================================================================
def phase02_mailboxes(client: HubSpotClient) -> PhaseResult:
    r = PhaseResult("02", "Funktionspostfächer trennen")
    contacts = client.search_all_by_id(
        _props(client),
        [{"filters": _filters(client, [
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
            {"propertyName": "kontakt_typ", "operator": "NOT_HAS_PROPERTY"}])}])
    r.scanned = len(contacts)
    for c in contacts:
        email = _p(c, "email")
        v = rules.classify_mailbox(email)
        if not v.is_role:
            continue
        target = r.changes if v.confidence == HIGH else r.flags
        target.append(Change(c["id"], "02", "kontakt_typ", _p(c, "kontakt_typ"),
                             "Funktionspostfach", v.confidence, v.reason, email))
        target.append(Change(c["id"], "02", "dq_status", _p(c, "dq_status"),
                             "funktionspostfach" if v.confidence == HIGH else "pruefen",
                             v.confidence, v.reason, email))
    r.notes.append(f"{r.auto_count} eindeutige Funktionspostfächer, "
                   f"{r.review_count} zur Prüfung")
    return r


# ===========================================================================
# Phase 03 -- Namen aus E-Mail ableiten
# ===========================================================================
def phase03_derive(client: HubSpotClient,
                   conventions: dict[str, rules.Convention]) -> PhaseResult:
    r = PhaseResult("03", "Namen aus E-Mail ableiten")
    contacts = client.search_all_by_id(
        _props(client),
        [{"filters": _filters(client, [
            {"propertyName": "firstname", "operator": "NOT_HAS_PROPERTY"},
            {"propertyName": "email", "operator": "HAS_PROPERTY"}])}])
    r.scanned = len(contacts)
    skipped_role = 0
    for c in contacts:
        if _protected(c):
            continue
        email = _p(c, "email")

        # Funktionspostfaecher bekommen NIE einen Personennamen (Leitplanke 02).
        if _p(c, "kontakt_typ") == "Funktionspostfach" or rules.classify_mailbox(email).is_role:
            skipped_role += 1
            continue

        g = rules.derive_name(email, conventions)
        if not (g.firstname or g.lastname):
            r.flags.append(Change(c["id"], "03", "dq_status", _p(c, "dq_status"), "pruefen",
                                  LOW, g.reason or "Name nicht ableitbar", email))
            continue

        target = r.changes if g.confidence == HIGH else r.flags
        if g.firstname:
            target.append(Change(c["id"], "03", "firstname", _p(c, "firstname"),
                                 g.firstname, g.confidence, g.reason, email))
        if g.lastname and g.lastname != _p(c, "lastname"):
            target.append(Change(c["id"], "03", "lastname", _p(c, "lastname"),
                                 g.lastname, g.confidence, g.reason, email))
        target.append(Change(c["id"], "03", "name_quelle", _p(c, "name_quelle"),
                             "aus_email_abgeleitet", g.confidence, g.reason, email))
        target.append(Change(c["id"], "03", "dq_status", _p(c, "dq_status"),
                             "auto_bereinigt" if g.confidence == HIGH else "pruefen",
                             g.confidence, g.reason, email))

    r.notes.append(f"{r.auto_count} automatisch befüllbar, {r.review_count} zur Prüfung, "
                   f"{skipped_role} Funktionspostfächer übersprungen")
    return r


# ===========================================================================
# Phase 04 -- vertauschte Namen
# ===========================================================================
def phase04_swaps(client: HubSpotClient, conventions: dict[str, rules.Convention],
                  source: str | None = None) -> PhaseResult:
    r = PhaseResult("04", "Vertauschte Vor-/Nachnamen")
    filters = [{"propertyName": "firstname", "operator": "HAS_PROPERTY"},
               {"propertyName": "lastname", "operator": "HAS_PROPERTY"},
               {"propertyName": "email", "operator": "HAS_PROPERTY"}]
    if source:
        filters.append({"propertyName": "hs_object_source_label",
                        "operator": "EQ", "value": source})
    contacts = client.search_all_by_id(_props(client),
                                       [{"filters": _filters(client, filters)}])
    r.scanned = len(contacts)
    for c in contacts:
        if _protected(c):
            continue
        fn, ln = _p(c, "firstname"), _p(c, "lastname")
        email, sal = _p(c, "email"), _p(c, "salutation")
        v = rules.detect_swap(fn, ln, email, sal, conventions)
        if not v.swapped:
            continue
        why = v.reason + " | " + " / ".join(v.signals)
        target = r.changes if v.confidence == HIGH else r.flags
        target.append(Change(c["id"], "04", "firstname", fn, ln, v.confidence, why, email))
        target.append(Change(c["id"], "04", "lastname", ln, fn, v.confidence, why, email))
        target.append(Change(c["id"], "04", "dq_status", _p(c, "dq_status"),
                             "auto_bereinigt" if v.confidence == HIGH else "pruefen",
                             v.confidence, why, email))
    r.notes.append(f"{r.auto_count} eindeutige Swaps, {r.review_count} zur Prüfung, "
                   f"{r.scanned} Kontakte geprüft")
    return r


# ===========================================================================
# Phase 05 -- Normalisieren
# ===========================================================================
def phase05_normalise(client: HubSpotClient) -> PhaseResult:
    r = PhaseResult("05", "Namen, Anrede und Telefon normalisieren")
    contacts = client.search_all_by_id(
        _props(client),
        [{"filters": [{"propertyName": "email", "operator": "HAS_PROPERTY"}]}])
    r.scanned = len(contacts)
    for c in contacts:
        email = _p(c, "email")
        cid = c["id"]

        if not _protected(c):
            for fld in ("firstname", "lastname"):
                cur = _p(c, fld)
                fix = rules.clean_name_field(cur)
                if fix and fix.value != cur:
                    (r.changes if fix.confidence == HIGH else r.flags).append(
                        Change(cid, "05", fld, cur, fix.value, fix.confidence,
                               fix.reason, email))

        sal = _p(c, "salutation")
        fix = rules.clean_salutation(sal, _p(c, "firstname"))
        if fix and (fix.value != sal or fix.confidence == LOW):
            if fix.confidence == HIGH:
                r.changes.append(Change(cid, "05", "salutation", sal, fix.value,
                                        HIGH, fix.reason, email))
            else:
                r.flags.append(Change(cid, "05", "dq_status", _p(c, "dq_status"), "pruefen",
                                      LOW, fix.reason, email))

        for fld in ("phone", "mobilephone"):
            cur = _p(c, fld)
            fix = rules.to_e164(cur, _p(c, "country"), email)
            if fix and fix.value != cur:
                (r.changes if fix.confidence == HIGH else r.flags).append(
                    Change(cid, "05", fld, cur, fix.value, fix.confidence, fix.reason, email))

    r.notes.append(f"{r.auto_count} Kontakte mit eindeutigen Formatfixes, "
                   f"{r.review_count} zur Prüfung")
    return r


# ===========================================================================
# Phase 06 -- Land, Sprache, Kanal
# ===========================================================================
def phase06_enrich(client: HubSpotClient) -> PhaseResult:
    r = PhaseResult("06", "Land, Sprache und Kanal ableiten")
    contacts = client.search_all_by_id(
        _props(client),
        [{"filters": [{"propertyName": "email", "operator": "HAS_PROPERTY"}]}])
    r.scanned = len(contacts)
    for c in contacts:
        cid, email = c["id"], _p(c, "email")

        def add(field: str, fix) -> None:
            """Phase 06 fuellt nur Luecken. Routing nach Konfidenz, damit die
            Zaehlung 'zur Pruefung' nicht faelschlich 0 anzeigt."""
            target = r.changes if fix.confidence == HIGH else r.flags
            target.append(Change(cid, "06", field, "", fix.value, fix.confidence,
                                 fix.reason, email))

        cf, lf = rules.derive_country_language(email, _p(c, "phone") or _p(c, "mobilephone"))
        if cf and not _p(c, "country"):
            add("country", cf)
        if lf and not _p(c, "hs_language"):
            add("hs_language", lf)
        chf = rules.derive_channel(_p(c, "hs_object_source_label"),
                                   _p(c, "hs_analytics_source"))
        if chf and not _p(c, "contact_typ__channel_"):
            add("contact_typ__channel_", chf)

    r.notes.append(f"{len(r.changes)} Feldwerte automatisch ableitbar, "
                   f"{len(r.flags)} zur fachlichen Entscheidung")
    return r
