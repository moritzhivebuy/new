#!/usr/bin/env python3
"""Routine 3 -- Renewals.

Erzeugt einen Markdown-Brief mit vier Blöcken:

  1. Vertragsende im Fenster (Standard 90 Tage)
  1b. Kündigungsfrist läuft im Fenster ab (Vertragsende dahinter)
  2. Abgelaufene Vertragsdaten bei aktiven Kunden
  3. Aktive Kunden ohne Vertragsdatum

Block 2 und 3 sind nicht optional: ohne sie liest sich das 90-Tage-Fenster wie
eine vollständige Risikoliste, obwohl ein Drittel der Kundenbasis nur deshalb
nicht auftaucht, weil das Feld leer oder veraltet ist.

Aufruf:
    python3 scripts/renewals.py                     # heute, 90 Tage
    python3 scripts/renewals.py --as-of 2026-08-12   # reproduzierbar
    python3 scripts/renewals.py --window-days 180 --notice-months 3
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

import hubspot as hs

STATE_FILE = hs.OUTPUT_DIR / ".renewals-state.json"


# --------------------------------------------------------------------------
# Auswertung
# --------------------------------------------------------------------------


def enrich(customer: dict[str, Any], stichtag: date, notice_months: int, mrr_base: float) -> dict[str, Any]:
    """Fristen, Restlaufzeit und Aktivitätsalter an einen Kunden anhängen."""
    row = dict(customer)
    end = customer["contract_end"]
    row["mrr_share"] = (customer["mrr"] / mrr_base) if (customer["mrr"] and mrr_base) else None
    row["days_to_end"] = hs.days_between(stichtag, end) if end else None
    row["notice_deadline"] = hs.add_months(end, -notice_months) if end else None
    row["days_to_notice"] = (
        hs.days_between(stichtag, row["notice_deadline"]) if row["notice_deadline"] else None
    )
    row["days_since_activity"] = (
        hs.days_between(customer["last_activity"], stichtag) if customer["last_activity"] else None
    )
    row["projected_end"] = project_end(customer, stichtag)
    row["url"] = hs.company_url(customer["id"])
    row["link"] = hs.md_link(customer["name"], row["url"])
    row["deals"] = deals_for(customer["id"])
    row["open_deals"] = [deal for deal in row["deals"] if not deal["is_closed"]]
    row["flags"] = flags_for(row)
    return row


_DEALS_INDEX: dict[str, list[dict[str, Any]]] | None = None


def deals_for(company_id: str) -> list[dict[str, Any]]:
    global _DEALS_INDEX
    if _DEALS_INDEX is None:
        _DEALS_INDEX = hs.deals_by_company()
    return _DEALS_INDEX.get(company_id, [])


def project_end(customer: dict[str, Any], stichtag: date) -> date | None:
    """Vertragsende aus Start + n x Laufzeit fortschreiben.

    Das ist die Rechnung, die der HubSpot-Workflow aus Voraussetzung 1 künftig
    automatisch machen soll. Hier nur als Vorschlag ausgewiesen, nie als Fakt:
    ob der Vertrag tatsächlich verlängert wurde, steht nicht im CRM.
    """
    start, duration = customer["contract_start"], customer["duration_months"]
    if not start or not duration or duration <= 0:
        return None
    projected = hs.add_months(start, duration)
    guard = 0
    while projected < stichtag and guard < 100:
        projected = hs.add_months(projected, duration)
        guard += 1
    return projected


def flags_for(row: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    share = row.get("mrr_share")
    if share is not None and share >= hs.TOP_RISK_MRR_SHARE:
        flags.append(f"Top-Risiko ({hs.fmt_pct(share)} MRR)")
    age = row.get("days_since_activity")
    if row["last_activity"] is None:
        flags.append("keine Aktivität erfasst")
    elif age is not None and age > hs.ACTIVITY_CRITICAL_DAYS:
        flags.append(f"kalt ({age} Tage)")
    elif age is not None and age > hs.ACTIVITY_WARN_DAYS:
        flags.append(f"still ({age} Tage)")
    days_to_notice = row.get("days_to_notice")
    if days_to_notice is not None and days_to_notice < 0:
        flags.append(f"Frist verstrichen ({abs(days_to_notice)} Tage)")
    if row.get("mrr") is None:
        flags.append("kein MRR im CRM")
    return flags


def build(stichtag: date, window_days: int, notice_months: int) -> dict[str, Any]:
    customers = hs.active_customers()
    mrr_base = hs.total_mrr(customers)
    window_end = date.fromordinal(stichtag.toordinal() + window_days)

    rows = [enrich(customer, stichtag, notice_months, mrr_base) for customer in customers]

    in_window = [
        row for row in rows if row["contract_end"] and stichtag <= row["contract_end"] <= window_end
    ]
    notice_window = [
        row
        for row in rows
        if row["contract_end"]
        and row["contract_end"] > window_end
        and row["notice_deadline"]
        and stichtag <= row["notice_deadline"] <= window_end
    ]
    expired = [row for row in rows if row["contract_end"] and row["contract_end"] < stichtag]
    missing = [row for row in rows if not row["contract_end"]]

    in_window.sort(key=lambda row: row["contract_end"])
    notice_window.sort(key=lambda row: row["notice_deadline"])
    expired.sort(key=lambda row: row["contract_end"])
    missing.sort(key=lambda row: -(row["mrr"] or 0.0))

    duplicates = find_duplicates(rows)
    listed = in_window + notice_window + expired + missing

    return {
        "stichtag": stichtag,
        "deal_coverage": deal_coverage(rows, listed, stichtag),
        "window_days": window_days,
        "window_end": window_end,
        "notice_months": notice_months,
        "mrr_base": mrr_base,
        "customer_count": len(rows),
        "in_window": in_window,
        "notice_window": notice_window,
        "expired": expired,
        "missing": missing,
        "duplicates": duplicates,
    }


def deal_coverage(
    rows: list[dict[str, Any]], listed: list[dict[str, Any]], stichtag: date
) -> dict[str, Any]:
    """Prüfen, ob die Deals an den aktiven Kunden vollständig erfasst sind.

    Die Renewal-Logik selbst hängt an COMPANY-Feldern. Die Deals sind die
    Gegenprobe: läuft zu einem fälligen Vertrag überhaupt ein Vorgang, und gibt
    es Deals, die aus der Betrachtung fallen, weil sie an keinem aktiven Kunden
    hängen.
    """
    all_deals = hs.deals()
    if not all_deals:
        return {"available": False}

    customer_ids = {row["id"] for row in rows}
    linked_ids: set[str] = set()
    unlinked_open: list[dict[str, Any]] = []
    no_company: list[dict[str, Any]] = []

    for deal in all_deals:
        if not deal["company_ids"]:
            no_company.append(deal)
        matched = [cid for cid in deal["company_ids"] if cid in customer_ids]
        if matched:
            linked_ids.add(deal["id"])
        elif not deal["is_closed"]:
            unlinked_open.append(deal)

    on_customers = [deal for deal in all_deals if deal["id"] in linked_ids]
    open_on_customers = [deal for deal in on_customers if not deal["is_closed"]]

    # Offene Deals der gelisteten Kunden, mit dem Kunden als Kontext.
    listed_open: list[dict[str, Any]] = []
    for row in listed:
        for deal in row["open_deals"]:
            listed_open.append({"customer": row, "deal": deal})
    listed_open.sort(key=lambda item: (item["deal"]["close_date"] or date.max))

    # Owner der offenen Deals gegen die Owner-Liste prüfen: die Umstellung auf
    # aktive Kollegen betraf die Companies, nicht zwangsläufig die Deals.
    owners = hs.owner_info()
    stale_owners: dict[str, int] = {}
    for deal in open_on_customers:
        owner = owners.get(deal["owner_id"] or "")
        if owner and not owner["active"]:
            stale_owners[owner["name"]] = stale_owners.get(owner["name"], 0) + 1

    return {
        "available": True,
        "deal_owners_inactive": stale_owners,
        "total": len(all_deals),
        "on_customers": on_customers,
        "open_on_customers": open_on_customers,
        "by_pipeline_open": _count_by(open_on_customers, "pipeline"),
        "customers_with_deals": len({cid for deal in on_customers for cid in deal["company_ids"] if cid in customer_ids}),
        "customers_total": len(customer_ids),
        "unlinked_open": unlinked_open,
        "no_company": no_company,
        "multi_company": [deal for deal in all_deals if len(deal["company_ids"]) > 1],
        "listed_open": listed_open,
        "overdue_open": [
            item
            for item in listed_open
            if item["deal"]["close_date"] and item["deal"]["close_date"] < stichtag
        ],
    }


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item[key]] = counts.get(item[key], 0) + 1
    return counts


def find_duplicates(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Verdachtsfälle für Dubletten (Voraussetzung 4), rein informativ."""
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = row["dedupe_key"]
        if key:
            buckets.setdefault(key, []).append(row)
    return [group for group in buckets.values() if len(group) > 1]


# --------------------------------------------------------------------------
# Alert: neu im Fenster
# --------------------------------------------------------------------------


def read_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def write_state(report: dict[str, Any]) -> None:
    hs.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(
            {
                "last_run": report["stichtag"].isoformat(),
                "window_days": report["window_days"],
                "in_window_ids": sorted(row["id"] for row in report["in_window"]),
                "notice_window_ids": sorted(row["id"] for row in report["notice_window"]),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def diff_state(report: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    """Neueintritte gegenüber dem letzten Lauf.

    Zwei Fälle ohne Alert, beide bewusst:
      * **Erster Lauf** -- kein Vergleichsstand, sonst wäre die komplette Liste
        "neu".
      * **Geänderte Fensterbreite** -- jeder zusätzlich sichtbare Kunde wäre
        sonst ein Fehlalarm, obwohl sich nur der Ausschnitt geändert hat.
    """
    empty: dict[str, Any] = {"new_in_window": [], "new_in_notice": [], "suppressed": None}
    if not state:
        return {**empty, "suppressed": "first_run"}
    if state.get("window_days") != report["window_days"]:
        return {**empty, "suppressed": "window_changed"}
    known_window = set(state.get("in_window_ids") or [])
    known_notice = set(state.get("notice_window_ids") or [])
    return {
        "suppressed": None,
        "reference_date": state.get("last_run"),
        "new_in_window": [row for row in report["in_window"] if row["id"] not in known_window],
        "new_in_notice": [
            row for row in report["notice_window"] if row["id"] not in known_notice
        ],
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def fmt_factor(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def owner_label(row: dict[str, Any], owners: dict[str, dict[str, Any]]) -> str:
    owner_id = row["owner_id"]
    if not owner_id:
        return "nicht zugeordnet"
    owner = owners.get(owner_id)
    if owner is None:
        return owner_id
    return owner["name"] if owner["active"] else f"{owner['name']} (inaktiv)"


def activity_cell(row: dict[str, Any]) -> str:
    if not row["last_activity"]:
        return "keine"
    return f"{hs.fmt_date(row['last_activity'])} ({row['days_since_activity']} T)"


def notice_cell(row: dict[str, Any]) -> str:
    deadline, days = row["notice_deadline"], row["days_to_notice"]
    if deadline is None:
        return "-"
    if days is None:
        return hs.fmt_date(deadline)
    if days < 0:
        return f"{hs.fmt_date(deadline)} (verstrichen)"
    return f"{hs.fmt_date(deadline)} (in {days} T)"


def table(header: list[str], body: list[list[str]]) -> list[str]:
    if not body:
        return ["_Keine Einträge._", ""]
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    lines += ["| " + " | ".join(cells) + " |" for cells in body]
    lines.append("")
    return lines


def sum_line(rows: list[dict[str, Any]], mrr_base: float) -> str:
    total = sum(row["mrr"] or 0.0 for row in rows)
    share = (total / mrr_base) if mrr_base else None
    unknown = sum(1 for row in rows if row["mrr"] is None)
    suffix = f", davon {unknown} ohne MRR-Wert" if unknown else ""
    return (
        f"**Summe: {hs.fmt_eur(total)} EUR MRR** über {len(rows)} Kunden "
        f"({hs.fmt_pct(share)} der MRR-Basis){suffix}."
    )


def render(report: dict[str, Any], alerts: dict[str, list[dict[str, Any]]]) -> str:
    names = hs.owner_info()
    base = report["mrr_base"]
    lines: list[str] = [
        f"# CS-Routine 3 -- Renewals (Stand {hs.fmt_date(report['stichtag'])})",
        "",
        f"Basis: {report['customer_count']} aktive Kunden "
        f"(`lifecyclestage = customer`, `churn_date IS NULL`), "
        f"{hs.fmt_eur(base)} EUR MRR gesamt. "
        f"Fenster: {report['window_days']} Tage bis {hs.fmt_date(report['window_end'])}. "
        f"Angenommene Kündigungsfrist: {report['notice_months']} Monate zum Laufzeitende.",
        "",
    ]

    lines += render_alerts(alerts, names)

    # ---- Block 1
    lines += [
        f"## 1. Vertragsende im Fenster ({report['window_days']} Tage)",
        "",
    ]
    lines += table(
        ["Kunde", "Vertragsende", "Tage", "Kündigungsfrist", "MRR", "Anteil", "Laufzeit", "Owner", "Letzte Aktivität", "Hinweise"],
        [
            [
                row["link"],
                hs.fmt_date(row["contract_end"]),
                str(row["days_to_end"]),
                notice_cell(row),
                hs.fmt_eur(row["mrr"]),
                hs.fmt_pct(row["mrr_share"]),
                f"{row['duration_months']} Mon." if row["duration_months"] else "-",
                owner_label(row, names),
                activity_cell(row),
                "; ".join(row["flags"]) or "-",
            ]
            for row in report["in_window"]
        ],
    )
    if report["in_window"]:
        lines += [sum_line(report["in_window"], base), ""]
        passed = [row for row in report["in_window"] if (row["days_to_notice"] or 0) < 0]
        if passed:
            lines += [
                f"Bei {len(passed)} von {len(report['in_window'])} Kunden ist die "
                f"{report['notice_months']}-Monats-Frist bereits verstrichen. Diese Verträge "
                "haben sich formal verlängert, sofern nichts Abweichendes vereinbart wurde -- "
                "hier geht es nicht mehr um Renewal-Ansprache, sondern um Bestätigung der "
                "Verlängerung und um Upsell.",
                "",
            ]

    # ---- Block 1b
    lines += [
        f"## 1b. Kündigungsfrist läuft in den nächsten {report['window_days']} Tagen ab",
        "",
        "Vertragsende liegt hinter dem Fenster, der Entscheidungszeitpunkt aber davor. "
        "Das ist der Block, in dem Renewal-Ansprache tatsächlich noch wirkt.",
        "",
    ]
    lines += table(
        ["Kunde", "Frist bis", "Tage bis Frist", "Vertragsende", "MRR", "Anteil", "Laufzeit", "Owner", "Letzte Aktivität"],
        [
            [
                row["link"],
                hs.fmt_date(row["notice_deadline"]),
                str(row["days_to_notice"]),
                hs.fmt_date(row["contract_end"]),
                hs.fmt_eur(row["mrr"]),
                hs.fmt_pct(row["mrr_share"]),
                f"{row['duration_months']} Mon." if row["duration_months"] else "-",
                owner_label(row, names),
                activity_cell(row),
            ]
            for row in report["notice_window"]
        ],
    )
    if report["notice_window"]:
        lines += [sum_line(report["notice_window"], base), ""]

    # ---- Block 2
    lines += [
        "## 2. Abgelaufene Vertragsdaten (aktive Kunden)",
        "",
        "`contract_end_date` liegt in der Vergangenheit, der Kunde ist aber aktiv und "
        "ungechurnt. Entweder wurde verlängert und das Feld nicht nachgezogen, oder der "
        "Vertragsstatus ist ungeklärt. Die Spalte *Fortschreibung* ist ein Vorschlag aus "
        "`contract_start_date + n x contract_duration_months_`, kein CRM-Fakt.",
        "",
    ]
    lines += table(
        ["Kunde", "Vertragsende (CRM)", "Tage überfällig", "Fortschreibung", "MRR", "Anteil", "Owner", "Letzte Aktivität"],
        [
            [
                row["link"],
                hs.fmt_date(row["contract_end"]),
                str(abs(row["days_to_end"])),
                hs.fmt_date(row["projected_end"], dash="nicht berechenbar"),
                hs.fmt_eur(row["mrr"]),
                hs.fmt_pct(row["mrr_share"]),
                owner_label(row, names),
                activity_cell(row),
            ]
            for row in report["expired"]
        ],
    )
    if report["expired"]:
        lines += [sum_line(report["expired"], base), ""]

    # ---- Block 3
    lines += [
        "## 3. Aktive Kunden ohne Vertragsdatum",
        "",
        "Diese Kunden erscheinen in **keiner** Fensterabfrage. Wer nur Block 1 liest, hält "
        "sie für unproblematisch, weil das Feld leer ist.",
        "",
    ]
    lines += table(
        ["Kunde", "Vertragsbeginn", "Laufzeit", "Fortschreibung", "MRR", "Anteil", "Owner", "Letzte Aktivität"],
        [
            [
                row["link"],
                hs.fmt_date(row["contract_start"]),
                f"{row['duration_months']} Mon." if row["duration_months"] else "-",
                hs.fmt_date(row["projected_end"], dash="nicht berechenbar"),
                hs.fmt_eur(row["mrr"]),
                hs.fmt_pct(row["mrr_share"]),
                owner_label(row, names),
                activity_cell(row),
            ]
            for row in report["missing"]
        ],
    )
    if report["missing"]:
        lines += [sum_line(report["missing"], base), ""]

    lines += render_deals(report, names)
    lines += render_data_quality(report, names)
    return "\n".join(lines).rstrip() + "\n"


def render_deals(report: dict[str, Any], names: dict[str, dict[str, Any]]) -> list[str]:
    coverage = report["deal_coverage"]
    if not coverage.get("available"):
        return [
            "## 4. Offene Deals",
            "",
            "_Nicht verfügbar: Deals kommen aus der Associations-API und brauchen einen "
            "API-Token. Im MCP-Cache-Modus bleibt dieser Block leer, statt über Firmennamen "
            "zu joinen._",
            "",
        ]

    lines = [
        "## 4. Offene Deals auf den gelisteten Kunden",
        "",
        "Gegenprobe zu den Blöcken oben: läuft zu einem fälligen Vertrag überhaupt ein "
        "Vorgang im CRM.",
        "",
    ]
    lines += table(
        ["Kunde", "Deal", "Pipeline / Stage", "Betrag", "Close-Date", "Owner"],
        [
            [
                item["customer"]["link"],
                hs.md_link(item["deal"]["name"], item["deal"]["url"]),
                hs.stage_label(item["deal"]),
                hs.fmt_eur(item["deal"]["amount"]),
                deal_close_cell(item["deal"], report["stichtag"]),
                owner_label({"owner_id": item["deal"]["owner_id"]}, names),
            ]
            for item in coverage["listed_open"]
        ],
    )

    open_sales = [
        deal for deal in coverage["open_on_customers"] if deal["pipeline"] == hs.SALES_PIPELINE
    ]
    if not open_sales:
        lines += [
            f"**Kein einziger offener Deal in der Sales-Pipeline** über alle "
            f"{coverage['customers_total']} aktiven Kunden. Die "
            f"{len(coverage['open_on_customers'])} offenen Deals verteilen sich auf "
            "Onboarding und Upsell. Renewals werden im CRM also nicht als Deal geführt: "
            "der Vertragsverlängerung steht kein Vorgang gegenüber, an dem sich Fortschritt "
            "ablesen ließe. Solange das so ist, sind die COMPANY-Felder die einzige "
            "Renewal-Quelle, und der Report kann nicht zwischen \"noch nicht angefasst\" und "
            "\"läuft, nur nicht dokumentiert\" unterscheiden.",
            "",
        ]
    if coverage["overdue_open"]:
        lines += [
            f"{len(coverage['overdue_open'])} der {len(coverage['listed_open'])} hier "
            "gelisteten offenen Deals haben ein überschrittenes Close-Date. Entweder ist der "
            "Vorgang liegengeblieben oder das Datum ist nicht gepflegt.",
            "",
        ]
    return lines


def deal_close_cell(deal: dict[str, Any], stichtag: date) -> str:
    close = deal["close_date"]
    if close is None:
        return "-"
    if close < stichtag:
        return f"{hs.fmt_date(close)} (überschritten, {hs.days_between(close, stichtag)} T)"
    return hs.fmt_date(close)


def render_alerts(alerts: dict[str, Any], names: dict[str, dict[str, Any]]) -> list[str]:
    if alerts["suppressed"] == "first_run":
        return [
            "_Erster Lauf: kein Vergleichsstand, daher kein Neueintritts-Alert. "
            "Ab dem nächsten Lauf werden Neueintritte gemeldet._",
            "",
        ]
    if alerts["suppressed"] == "window_changed":
        return [
            "_Fensterbreite gegenüber dem letzten Lauf geändert: Neueintritts-Alert "
            "unterdrückt, weil sonst jeder zusätzlich sichtbare Kunde als neu gälte._",
            "",
        ]
    new_window = alerts["new_in_window"]
    new_notice = alerts["new_in_notice"]
    if not new_window and not new_notice:
        return [
            f"_Keine Neueintritte seit dem Lauf vom "
            f"{hs.fmt_date(date.fromisoformat(alerts['reference_date'])) if alerts.get('reference_date') else 'letzten Stand'}._",
            "",
        ]
    lines = ["## Alert -- neu seit dem letzten Lauf", ""]
    for row in new_window:
        lines.append(
            f"- **Neu im Fenster:** {row['link']} -- Vertragsende "
            f"{hs.fmt_date(row['contract_end'])} (in {row['days_to_end']} Tagen), "
            f"{hs.fmt_eur(row['mrr'])} EUR MRR, Owner {owner_label(row, names)}."
        )
    for row in new_notice:
        lines.append(
            f"- **Neu in der Frist:** {row['link']} -- Kündigungsfrist bis "
            f"{hs.fmt_date(row['notice_deadline'])} (in {row['days_to_notice']} Tagen), "
            f"Vertragsende {hs.fmt_date(row['contract_end'])}, "
            f"{hs.fmt_eur(row['mrr'])} EUR MRR."
        )
    lines.append("")
    return lines


def render_data_quality(report: dict[str, Any], names: dict[str, str]) -> list[str]:
    untracked = report["expired"] + report["missing"]
    untracked_mrr = sum(row["mrr"] or 0.0 for row in untracked)
    base = report["mrr_base"]
    count = report["customer_count"]
    share_customers = (len(untracked) / count) if count else 0.0
    tracked_window_mrr = sum(row["mrr"] or 0.0 for row in report["in_window"])

    lines = [
        "## Datenqualität",
        "",
        f"- **{len(untracked)} von {count} aktiven Kunden** ({hs.fmt_pct(share_customers)}) haben "
        f"kein belastbares Vertragsende: {len(report['expired'])} abgelaufen, "
        f"{len(report['missing'])} ohne Datum. Dahinter stehen {hs.fmt_eur(untracked_mrr)} EUR MRR "
        f"({hs.fmt_pct(untracked_mrr / base if base else None)} der Basis).",
        f"- Sauber getrackt im Fenster: {hs.fmt_eur(tracked_window_mrr)} EUR MRR. Das ungetrackte "
        f"Volumen ist ein Faktor {fmt_factor(untracked_mrr / tracked_window_mrr)} größer."
        if tracked_window_mrr
        else "- Im Fenster ist derzeit kein Vertrag sauber getrackt.",
    ]

    missing_mrr = [row for row in report["expired"] + report["missing"] + report["in_window"] if row["mrr"] is None]
    if missing_mrr:
        lines.append(
            f"- {len(missing_mrr)} Kunden ohne `company_mrr`: "
            + ", ".join(row["link"] for row in missing_mrr)
            + ". Deren Risiko lässt sich nicht quantifizieren."
        )

    inactive_owner_rows = [
        row for row in report["expired"] + report["missing"] + report["in_window"] + report["notice_window"]
        if not row["owner_id"]
    ]
    if inactive_owner_rows:
        lines.append(
            f"- {len(inactive_owner_rows)} Kunden ohne `hubspot_owner_id`: "
            + ", ".join(row["link"] for row in inactive_owner_rows)
            + "."
        )

    if names:
        listed = (
            report["in_window"] + report["notice_window"] + report["expired"] + report["missing"]
        )
        distribution: dict[str, int] = {}
        for row in listed:
            if row["owner_id"]:
                label = owner_label(row, names)
                distribution[label] = distribution.get(label, 0) + 1
        if distribution:
            lines.append(
                "- Owner-Verteilung in diesem Brief: "
                + ", ".join(
                    f"{name} ({count})"
                    for name, count in sorted(distribution.items(), key=lambda item: -item[1])
                )
                + "."
            )
        inactive = [
            row
            for row in listed
            if row["owner_id"] and not (names.get(row["owner_id"], {}).get("active", True))
        ]
        if inactive:
            inactive_mrr = sum(row["mrr"] or 0.0 for row in inactive)
            lines.append(
                f"- {len(inactive)} dieser Kunden ({hs.fmt_eur(inactive_mrr)} EUR MRR) laufen auf "
                "einen inaktiven Owner. Solange die Zuordnung nicht umgehängt ist, hat der Brief "
                "für diese Kunden keinen Adressaten."
            )

    coverage = report["deal_coverage"]
    if coverage.get("available"):
        lines.append(
            f"- **Deal-Abdeckung:** {coverage['total']} Deals im Account, "
            f"{len(coverage['on_customers'])} davon an aktiven Kunden, "
            f"{len(coverage['open_on_customers'])} offen. Alle "
            f"{coverage['customers_with_deals']} von {coverage['customers_total']} aktiven "
            "Kunden haben mindestens einen Deal, es fehlt also keiner ganz."
        )
        if coverage["unlinked_open"]:
            without_company = sum(1 for deal in coverage["unlinked_open"] if not deal["company_ids"])
            lines.append(
                f"- {len(coverage['unlinked_open'])} **offene Deals hängen an keinem aktiven "
                f"Kunden** und fallen aus jeder kundenbezogenen Auswertung: "
                f"{without_company} ohne jede Company-Verknüpfung, "
                f"{len(coverage['unlinked_open']) - without_company} an einer Company, die kein "
                "aktiver Kunde ist (Neugeschäft, gechurnt oder falsch getaggt)."
            )
        if coverage["no_company"]:
            closed = sum(1 for deal in coverage["no_company"] if deal["is_closed"])
            lines.append(
                f"- {len(coverage['no_company'])} Deals haben **gar keine Company-Verknüpfung** "
                f"({len(coverage['no_company']) - closed} offen, {closed} geschlossen). Sie "
                "lassen sich keinem Kunden zuordnen und zählen in keiner Kundenauswertung mit."
            )
        stale = coverage["deal_owners_inactive"]
        if stale:
            lines.append(
                f"- **{sum(stale.values())} der {len(coverage['open_on_customers'])} offenen Deals an "
                "aktiven Kunden laufen noch auf inaktive Owner** ("
                + ", ".join(
                    f"{name}: {count}" for name, count in sorted(stale.items(), key=lambda i: -i[1])
                )
                + "). Die Owner-Umstellung hat die Companies erfasst, die Deals nicht."
            )
        if coverage["multi_company"]:
            lines.append(
                f"- {len(coverage['multi_company'])} Deals hängen an mehr als einer Company: "
                + ", ".join(
                    hs.md_link(deal["name"], deal["url"]) for deal in coverage["multi_company"]
                )
                + ". Bei Dubletten ist das ein Hinweis darauf, welche Records zusammengehören."
            )

    for excluded in hs.excluded_non_customers():
        lines.append(
            f"- **{excluded['name']}** (ID {excluded['id']}) ist aus der Basis "
            f"ausgeschlossen: {excluded['reason']}. Solange das Feld im CRM nicht "
            "korrigiert ist, hängt der Ausschluss an einer Liste im Code."
        )

    if report["duplicates"]:
        lines.append("- Dubletten-Verdacht unter den aktiven Kunden:")
        for group in report["duplicates"]:
            lines.append(
                "    - " + " / ".join(row["link"] for row in group)
            )

    lines.append("")
    return lines


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="CS-Routine 3: Renewals")
    parser.add_argument("--as-of", help="Stichtag YYYY-MM-DD (Standard: heute, UTC)")
    parser.add_argument("--window-days", type=int, default=90, help="Fensterbreite in Tagen")
    parser.add_argument(
        "--notice-months",
        type=int,
        default=hs.NOTICE_PERIOD_MONTHS,
        help="Kündigungsfrist in Monaten zum Laufzeitende",
    )
    parser.add_argument("--out", help="Zielpfad (Standard: output/<Stichtag>-renewals.md)")
    parser.add_argument("--stdout", action="store_true", help="Nur ausgeben, nicht schreiben")
    parser.add_argument(
        "--no-state",
        action="store_true",
        help="Alert-Stand nicht fortschreiben (für Testläufe)",
    )
    args = parser.parse_args()

    stichtag = hs.today(args.as_of)
    try:
        report = build(stichtag, args.window_days, args.notice_months)
    except hs.HubSpotError as error:
        print(f"Datenzugriff fehlgeschlagen:\n{error}")
        return 1

    alerts = diff_state(report, read_state())
    document = render(report, alerts)

    if args.stdout:
        print(document)
    else:
        path = Path(args.out) if args.out else hs.OUTPUT_DIR / f"{stichtag.isoformat()}-renewals.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document, encoding="utf-8")
        print(f"Geschrieben: {path}")
        print(
            f"Fenster: {len(report['in_window'])} | Frist: {len(report['notice_window'])} | "
            f"abgelaufen: {len(report['expired'])} | ohne Datum: {len(report['missing'])}"
        )

    if not args.no_state:
        write_state(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
