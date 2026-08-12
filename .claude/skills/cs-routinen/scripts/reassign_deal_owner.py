#!/usr/bin/env python3
"""Deal-Owner umhängen -- Wartungsskript, kein Teil der Report-Routinen.

Schreibt in HubSpot. Deshalb: **Dry-Run ist der Standard.** Erst mit ``--apply``
wird tatsächlich geschrieben, und vorher wird immer ein Backup der alten Owner
nach ``output/`` geschrieben, damit die Änderung rückgängig gemacht werden kann.

Aufruf:
    # anzeigen, was passieren würde
    python3 scripts/reassign_deal_owner.py --to 109171979

    # tatsächlich umhängen
    python3 scripts/reassign_deal_owner.py --to 109171979 --apply

    # rückgängig machen
    python3 scripts/reassign_deal_owner.py --restore output/<datei>.json --apply

Der Standard-Scope ist bewusst eng: **offene** Deals an **aktiven Kunden**, deren
Owner inaktiv ist. Geschlossene Deals bleiben unangetastet, weil sie
Historie sind und ein Owner-Wechsel dort die Zuordnung vergangener Abschlüsse
verfälscht. Deals an Nicht-Kunden gehören fachlich ins Neugeschäft und nicht
automatisch an CS. Beides lässt sich über ``--scope`` erweitern.

**Achtung Berechtigungen (Stand 12.08.2026):** Der Private-App-Token darf Deals
nur lesen, nicht schreiben. ``--apply`` läuft deshalb auf ein HTTP 403 mit dem
Hinweis auf die fehlenden Scopes ``crm.objects.deals.write``. Die Auswahl und der
Dry-Run funktionieren trotzdem. Solange der Scope fehlt, muss das Schreiben über
``mcp__HubSpot__manage_crm_objects`` laufen (Batch-Limit dort: **10 Objekte pro
Aufruf**); die Owner-Sicherung dieses Skripts sollte man vorher trotzdem
erzeugen, sie ist die Grundlage für ``--restore``.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import hubspot as hs

BATCH_PATH = "/crm/v3/objects/deals/batch/update"
BATCH_SIZE = 100


def select(scope: str) -> list[dict[str, Any]]:
    """Deals nach Scope auswählen. Immer nur solche mit inaktivem Owner."""
    owners = hs.owner_info()
    inactive = {oid for oid, owner in owners.items() if not owner["active"]}
    customer_ids = {row["id"] for row in hs.active_customers()}

    selected: list[dict[str, Any]] = []
    for deal in hs.deals():
        if (deal["owner_id"] or "") not in inactive:
            continue
        on_customer = bool(set(deal["company_ids"]) & customer_ids)
        if scope == "open-active-customers":
            keep = on_customer and not deal["is_closed"]
        elif scope == "open-all":
            keep = not deal["is_closed"]
        elif scope == "active-customers":
            keep = on_customer
        elif scope == "all":
            keep = True
        else:
            raise SystemExit(f"Unbekannter Scope: {scope}")
        if keep:
            selected.append(deal)
    return selected


def resolve_owner(value: str) -> tuple[str, str]:
    """Owner-ID oder Name auf (ID, Name) auflösen und Aktivität prüfen."""
    owners = hs.owner_info()
    if value in owners:
        owner = owners[value]
    else:
        matches = {
            oid: info for oid, info in owners.items() if info["name"].lower() == value.lower()
        }
        if len(matches) != 1:
            raise SystemExit(
                f"Owner '{value}' nicht eindeutig ({len(matches)} Treffer). Bitte Owner-ID angeben."
            )
        value, owner = next(iter(matches.items()))
    if not owner["active"]:
        raise SystemExit(f"Zielowner '{owner['name']}' ist inaktiv. Abbruch.")
    return value, owner["name"]


def write_backup(deals: list[dict[str, Any]], target_id: str, label: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    path = hs.OUTPUT_DIR / f"{stamp}-deal-owner-backup.json"
    hs.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    owners = hs.owner_info()
    path.write_text(
        json.dumps(
            {
                "created": stamp,
                "new_owner_id": target_id,
                "new_owner_name": label,
                "deals": [
                    {
                        "id": deal["id"],
                        "name": deal["name"],
                        "previous_owner_id": deal["owner_id"],
                        "previous_owner_name": owners.get(deal["owner_id"] or "", {}).get("name"),
                    }
                    for deal in deals
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def apply_updates(pairs: list[tuple[str, str]]) -> int:
    """(deal_id, owner_id)-Paare in Batches schreiben."""
    token = hs._access_token()
    if token is None:
        raise SystemExit("Kein API-Token: Schreiben ist im MCP-Cache-Modus nicht möglich.")
    written = 0
    for start in range(0, len(pairs), BATCH_SIZE):
        chunk = pairs[start : start + BATCH_SIZE]
        payload = {
            "inputs": [
                {"id": deal_id, "properties": {"hubspot_owner_id": owner_id}}
                for deal_id, owner_id in chunk
            ]
        }
        response = hs._post_json(BATCH_PATH, payload, token)
        written += len(response.get("results", []))
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Deal-Owner umhängen")
    parser.add_argument("--to", help="Ziel-Owner: ID oder exakter Name")
    parser.add_argument(
        "--scope",
        default="open-active-customers",
        choices=["open-active-customers", "open-all", "active-customers", "all"],
        help="Welche Deals mit inaktivem Owner erfasst werden",
    )
    parser.add_argument("--restore", help="Backup-Datei: Owner daraus wiederherstellen")
    parser.add_argument("--apply", action="store_true", help="tatsächlich schreiben")
    args = parser.parse_args()

    if args.restore:
        backup = json.loads(Path(args.restore).read_text(encoding="utf-8"))
        pairs = [
            (entry["id"], entry["previous_owner_id"])
            for entry in backup["deals"]
            if entry.get("previous_owner_id")
        ]
        print(f"Wiederherstellung aus {args.restore}: {len(pairs)} Deals")
        if not args.apply:
            print("Dry-Run. Mit --apply ausführen.")
            return 0
        print(f"Geschrieben: {apply_updates(pairs)}")
        return 0

    if not args.to:
        raise SystemExit("--to fehlt (Owner-ID oder Name)")

    target_id, target_name = resolve_owner(args.to)
    deals = select(args.scope)
    owners = hs.owner_info()

    print(f"Scope: {args.scope}")
    print(f"Ziel-Owner: {target_name} ({target_id})")
    print(f"Betroffene Deals: {len(deals)}\n")
    for deal in sorted(deals, key=lambda d: (d["pipeline"], d["name"])):
        previous = owners.get(deal["owner_id"] or "", {}).get("name", deal["owner_id"])
        print(
            f"  {deal['id']:>14}  {previous:<18} -> {target_name:<18} "
            f"{hs.stage_label(deal):<45} {deal['name'][:60]}"
        )

    if not deals:
        return 0
    if not args.apply:
        print("\nDry-Run. Nichts geschrieben. Mit --apply ausführen.")
        return 0

    backup_path = write_backup(deals, target_id, target_name)
    print(f"\nBackup: {backup_path}")
    written = apply_updates([(deal["id"], target_id) for deal in deals])
    print(f"Geschrieben: {written} von {len(deals)}")
    return 0 if written == len(deals) else 1


if __name__ == "__main__":
    raise SystemExit(main())
