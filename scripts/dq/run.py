"""CLI der HubSpot-Bereinigungsroutine (Variante b).

Dry-Run ist der Default und lässt sich nicht abschalten, ohne eine
freigegebene CSV zu übergeben:

    # 1. Analysieren, CSV-Diff schreiben (schreibt NICHTS nach HubSpot)
    python3 -m scripts.dq.run --phases 0,1,2,3,4,5,6 --out befund/

    # 2. befund/aenderungen.csv prüfen, unerwünschte Zeilen entfernen
    #    oder Spalte "freigabe" auf nein setzen

    # 3. Nur die freigegebenen Zeilen schreiben
    python3 -m scripts.dq.run --apply befund/aenderungen.csv

    # Properties aus Phase 00 anlegen (einmalig)
    python3 -m scripts.dq.run --create-properties

    # Token-Scopes prüfen
    python3 -m scripts.dq.run --check-scopes
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import sys
from collections import Counter, defaultdict

from .client import HubSpotClient, MissingScope
from .pipeline import (DQ_PROPERTIES, Change, learn, phase00_properties, phase01_ghosts,
                       phase02_mailboxes, phase03_derive, phase04_swaps, phase05_normalise,
                       phase06_enrich)
from .rules import HIGH

CSV_FIELDS = ["freigabe", "contact_id", "phase", "feld", "alt", "neu", "konfidenz",
              "email", "begruendung", "hubspot_url"]
PORTAL_URL = "https://app.hubspot.com/contacts/{portal}/record/0-1/{cid}"


def _url(cid: str, portal: str) -> str:
    return PORTAL_URL.format(portal=portal or "PORTAL", cid=cid)


def write_csv(path: str, changes: list[Change], portal: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS, delimiter=";")
        w.writeheader()
        for c in changes:
            w.writerow({
                "freigabe": "ja" if c.auto else "nein",
                "contact_id": c.contact_id, "phase": c.phase, "feld": c.field,
                "alt": c.old, "neu": c.new, "konfidenz": c.confidence,
                "email": c.email, "begruendung": c.reason,
                "hubspot_url": _url(c.contact_id, portal),
            })


def write_deletes(path: str, deletes: list[tuple[str, str]], portal: str) -> None:
    if not deletes:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["freigabe", "contact_id", "begruendung", "hubspot_url"])
        for cid, why in deletes:
            w.writerow(["nein", cid, why, _url(cid, portal)])


# ---------------------------------------------------------------------------
def cmd_analyse(args, client: HubSpotClient) -> int:
    portal = args.portal or os.environ.get("HUBSPOT_PORTAL_ID", "")
    phases = {p.strip() for p in args.phases.split(",") if p.strip()}
    results, conventions = [], {}

    if phases & {"3", "4"}:
        print("Domain-Konventionen lernen …")
        conventions = learn(client, sample=args.convention_sample)
        strong = {d: c for d, c in conventions.items() if c.confidence == HIGH}
        reversed_ = {d: c for d, c in strong.items() if c.order == "ln_first"}
        print(f"  {len(conventions)} Domains, {len(strong)} mit hoher Konfidenz, "
              f"davon {len(reversed_)} mit nachname.vorname")
        for d, c in sorted(reversed_.items(), key=lambda x: -x[1].support)[:10]:
            print(f"    {d}: {c.fn_first}:{c.ln_first}")

    runners = {
        "0": lambda: phase00_properties(client),
        "1": lambda: phase01_ghosts(client),
        "2": lambda: phase02_mailboxes(client),
        "3": lambda: phase03_derive(client, conventions),
        "4": lambda: phase04_swaps(client, conventions, args.source),
        "5": lambda: phase05_normalise(client),
        "6": lambda: phase06_enrich(client),
    }
    for key in sorted(phases):
        if key not in runners:
            print(f"unbekannte Phase: {key}", file=sys.stderr)
            return 2
        print(f"\nPhase {key} …")
        res = runners[key]()
        results.append(res)
        for n in res.notes:
            print(f"  {n}")

    all_changes = [c for r in results for c in (r.changes + r.flags)]
    all_deletes = [d for r in results for d in r.deletes]

    print("\n" + "=" * 68)
    print(f"BEFUND  ({dt.date.today().isoformat()})")
    print("=" * 68)
    for r in results:
        if r.changes or r.flags or r.deletes:
            print(f"  Phase {r.phase} {r.title}")
            print(f"      geprüft {r.scanned:>6}  automatisch {r.auto_count:>5}  "
                  f"zur Prüfung {r.review_count:>5}"
                  + (f"  löschen {len(r.deletes)}" if r.deletes else ""))
    auto_ids = {c.contact_id for c in all_changes if c.auto}
    rev_ids = {c.contact_id for c in all_changes if not c.auto}
    print(f"\n  Kontakte mit automatischen Änderungen : {len(auto_ids)}")
    print(f"  Kontakte zur manuellen Prüfung        : {len(rev_ids - auto_ids)}")
    print(f"  Löschkandidaten                       : {len(all_deletes)}")
    print(f"  API-Aufrufe                           : {client.calls}")

    by_field = Counter(f"{c.phase}/{c.field}" for c in all_changes if c.auto)
    if by_field:
        print("\n  Automatische Änderungen je Feld:")
        for k, v in by_field.most_common():
            print(f"      {k:32s} {v:5d}")

    if all_changes:
        path = os.path.join(args.out, "aenderungen.csv")
        write_csv(path, all_changes, portal)
        print(f"\n  Diff geschrieben: {path}")
        print("  Spalte 'freigabe' prüfen, dann:")
        print(f"      python3 -m scripts.dq.run --apply {path}")
    if all_deletes:
        path = os.path.join(args.out, "loeschkandidaten.csv")
        write_deletes(path, all_deletes, portal)
        print(f"  Löschkandidaten:  {path}  (Freigabe-Spalte steht auf 'nein')")

    print("\n  Es wurde nichts in HubSpot geschrieben.")
    return 0


def cmd_apply(args, client: HubSpotClient) -> int:
    """Nur Zeilen mit freigabe=ja schreiben."""
    with open(args.apply, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))
    approved = [r for r in rows if (r.get("freigabe") or "").strip().lower()
                in ("ja", "j", "yes", "y", "true", "1")]
    if not approved:
        print("Keine Zeile mit freigabe=ja gefunden -- nichts zu tun.")
        return 0

    stamp = dt.date.today().isoformat()
    grouped: dict[str, dict[str, str]] = defaultdict(dict)
    trail: dict[str, list[str]] = defaultdict(list)
    for r in approved:
        cid = r["contact_id"].strip()
        grouped[cid][r["feld"].strip()] = r["neu"]
        trail[cid].append(f"[{stamp} P{r['phase']}] {r['feld']}: "
                          f"{r['alt'] or '(leer)'} -> {r['neu']} ({r['konfidenz']}) "
                          f"{r['begruendung']}")

    updates = []
    for cid, props in grouped.items():
        props = dict(props)
        props["dq_letzte_pruefung"] = stamp
        # Alte Werte protokollieren, damit jede Änderung umkehrbar ist.
        props["dq_befund"] = "\n".join(trail[cid])[:65000]
        updates.append({"id": cid, "properties": props})

    print(f"{len(approved)} freigegebene Feldänderungen auf {len(updates)} Kontakten.")
    if args.dry_run:
        print("--dry-run gesetzt: nichts geschrieben.")
        for u in updates[:5]:
            print(f"  {u['id']}: {', '.join(f'{k}={v!r}' for k, v in u['properties'].items() if k != 'dq_befund')}")
        return 0

    try:
        done = client.batch_update(updates)
    except MissingScope as e:
        print(f"\nFEHLER: {e}", file=sys.stderr)
        print("\nBenötigte Scopes im Private App ergänzen:\n"
              "  crm.objects.contacts.write\n"
              "  crm.schemas.contacts.write  (nur für --create-properties)",
              file=sys.stderr)
        return 3
    print(f"{len(done)} Kontakte aktualisiert. Alte Werte stehen in dq_befund.")
    return 0


def cmd_create_properties(args, client: HubSpotClient) -> int:
    existing = {p["name"] for p in client.get_properties()}
    todo = [d for d in DQ_PROPERTIES if d["name"] not in existing]
    if not todo:
        print("Alle Properties sind vorhanden.")
        return 0
    print(f"{len(todo)} Properties fehlen: {', '.join(d['name'] for d in todo)}")
    if args.dry_run:
        print("--dry-run gesetzt: nichts angelegt.")
        return 0
    try:
        for d in todo:
            client.create_property(d)
            print(f"  angelegt: {d['name']}")
    except MissingScope as e:
        print(f"\nFEHLER: {e}", file=sys.stderr)
        print("\nBenötigter Scope: crm.schemas.contacts.write", file=sys.stderr)
        return 3
    return 0


def cmd_check_scopes(client: HubSpotClient) -> int:
    print("Token-Scopes (No-Op-Proben, ändern keine Daten):")
    scopes = client.check_scopes()
    for name in ("contacts.read", "schemas.contacts.read", "contacts.write"):
        print(f"  {'JA  ' if scopes.get(name) else 'NEIN'}  crm.objects.{name}"
              if "schemas" not in name else
              f"  {'JA  ' if scopes.get(name) else 'NEIN'}  crm.{name}")
    if not scopes.get("contacts.write"):
        print("\n  Schreiben ist nicht möglich. Im HubSpot Private App ergänzen:")
        print("    crm.objects.contacts.write   (für Phase 02-06)")
        print("    crm.schemas.contacts.write   (für --create-properties)")
        print("  Settings -> Integrations -> Private Apps -> App -> Scopes")
        return 1
    return 0


# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 -m scripts.dq.run",
        description="HubSpot Kontaktdaten-Bereinigung. Dry-Run ist der Default.")
    ap.add_argument("--phases", default="0,1,2,3,4,5,6",
                    help="Kommagetrennt, Default alle: 0=Properties 1=Geister "
                         "2=Postfächer 3=Ableiten 4=Swaps 5=Normalisieren 6=Anreichern")
    ap.add_argument("--out", default="befund", help="Zielordner für die CSVs")
    ap.add_argument("--source", default=None,
                    help="Phase 04 auf eine Datensatzquelle begrenzen, z.B. IMPORT")
    ap.add_argument("--convention-sample", type=int, default=4000,
                    help="Wie viele saubere Kontakte zum Lernen der Domain-Konventionen")
    ap.add_argument("--portal", default=None, help="Portal-ID für die Links in der CSV")
    ap.add_argument("--apply", metavar="CSV",
                    help="Freigegebene CSV schreiben (nur Zeilen mit freigabe=ja)")
    ap.add_argument("--create-properties", action="store_true",
                    help="Die fünf dq_-Properties in HubSpot anlegen")
    ap.add_argument("--check-scopes", action="store_true", help="Token-Scopes prüfen")
    ap.add_argument("--dry-run", action="store_true",
                    help="Auch bei --apply und --create-properties nichts schreiben")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    needs_write = bool(args.apply or args.create_properties) and not args.dry_run
    try:
        client = HubSpotClient(allow_write=needs_write or args.check_scopes,
                               verbose=args.verbose)
    except RuntimeError as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 2

    if args.check_scopes:
        return cmd_check_scopes(client)
    if args.create_properties:
        return cmd_create_properties(args, client)
    if args.apply:
        return cmd_apply(args, client)
    return cmd_analyse(args, client)


if __name__ == "__main__":
    raise SystemExit(main())
