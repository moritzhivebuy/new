"""Erzeugt abnickbare Vorschlagslisten aus einem Dry-Run-Befund.

Aufruf:  python3 -m scripts.dq.vorschlaege befund/aktuell/aenderungen.csv [zielordner]

Zerlegt die Pruefzeilen in zwei grundverschiedene Sorten:

  1. Regelentscheidungen (Phase 06) -- eine fachliche Zusage loest tausende
     Datensaetze auf. Landet in entscheidungen.md.
  2. Einzelfaelle (Phase 02-05) -- nach Muster gruppiert, damit man Gruppen
     abnickt statt Zeilen. Landet in pruefliste.csv.

Zusaetzlich: telefon.csv mit allen Telefonvorschlaegen samt Herkunft der
Laendervorwahl, weil das die haeufigste Rueckfrage ist.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter, defaultdict

FIELDS = ["freigabe", "contact_id", "phase", "feld", "alt", "neu", "konfidenz",
          "email", "begruendung", "hubspot_url"]


def read(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def muster(row: dict) -> str:
    """Begruendung auf ein Muster reduzieren, damit sich Faelle gruppieren.

    Konkrete Werte muessen raus, sonst bildet jedes Kuerzel und jede Domain
    eine eigene Einer-Gruppe und die Liste ist wieder eine Zeilenliste.
    """
    b = row["begruendung"].split("|")[0].strip()
    b = re.sub(r"'[^']*'", "X", b)
    b = re.sub(r"Kuerzel:\s*\S+", "Kuerzel: X", b)
    b = re.sub(r"Ansprechpartner\s+.*?\s+hinterlegt", "Ansprechpartner hinterlegt", b)
    b = re.sub(r"Rollen-Token im Local Part:.*", "Rollen-Token im Local Part", b)
    b = re.sub(r"(fuer|aus|Land)\s+[\w.\-]+\.\w{2,}", r"\1 <domain>", b)
    b = re.sub(r"Land\s+[A-Z]\w+", "Land <land>", b)
    b = re.sub(r"TLD\s+\.\w+", "TLD <tld>", b)
    b = re.sub(r"\d+", "N", b)
    b = re.sub(r"\s+", " ", b).strip(" ;.")
    return f"P{row['phase']} · {b[:80]}"


# ---------------------------------------------------------------------------
def schreibe_entscheidungen(rows: list[dict], out: str) -> dict[str, int]:
    """Phase 06: drei Regeln, je mit Umfang und Stichprobe."""
    p6 = [r for r in rows if r["phase"] == "06" and r["freigabe"] == "nein"]
    gruppen: dict[str, list[dict]] = defaultdict(list)
    for r in p6:
        if r["feld"] == "hs_language":
            gruppen["sprache"].append(r)
        elif r["feld"] == "country":
            gruppen["land"].append(r)
        else:
            gruppen["kanal"].append(r)

    titel = {
        "sprache": ("Sprache (`hs_language`) aus dem Land ableiten",
                    "Ohne `hs_language` versendet HubSpot keine sprachrichtigen "
                    "Mails. Abgeleitet wird aus dem Land, das seinerseits aus "
                    "E-Mail-TLD oder Telefonvorwahl kommt."),
        "land": ("Land (`country`) aus E-Mail-TLD und Telefonvorwahl ableiten",
                 "`.de` → Germany, `.at` → Austria, `.ch` → Switzerland. "
                 "Freemail-Domains werden ausgelassen, dort greift nur die "
                 "Telefonvorwahl."),
        "kanal": ("Kanal (`contact_typ__channel_`) bei Traffic-Quelle `OFFLINE`",
                  "`OFFLINE` heisst nur 'keine Web-Session bekannt' und belegt "
                  "keine Richtung. Betrifft vor allem per Integration angelegte "
                  "Produktkontakte. Deshalb keine Automatik — das ist eine "
                  "Reporting-Definition, keine Datenfrage."),
    }

    lines = ["# Regelentscheidungen Phase 06", "",
             "Jede dieser drei Regeln loest auf einen Schlag tausende Datensaetze auf.",
             "Es sind **keine Einzelfaelle** — hier wird eine fachliche Zusage gebraucht,",
             "keine Sichtpruefung.", "",
             "Zustimmen heisst: die betroffenen Zeilen in `aenderungen.csv` auf",
             "`freigabe=ja` setzen und `--apply` laufen lassen.", ""]
    counts = {}
    for key in ("sprache", "land", "kanal"):
        g = gruppen.get(key, [])
        if not g:
            continue
        counts[key] = len(g)
        head, erklaerung = titel[key]
        lines += [f"## {head}", "",
                  f"**Umfang:** {len(g)} Kontakte", "", erklaerung, "",
                  "Verteilung der vorgeschlagenen Werte:", ""]
        for val, n in Counter(r["neu"] for r in g).most_common(12):
            lines.append(f"- `{val}` — {n} Kontakte")
        lines += ["", "Stichprobe:", "", "| E-Mail | Vorschlag | Begruendung |",
                  "|---|---|---|"]
        for r in g[:8]:
            lines.append(f"| `{r['email']}` | `{r['neu']}` | {r['begruendung'][:70]} |")
        lines += ["", "**Entscheidung:** [ ] uebernehmen   [ ] nicht uebernehmen", "", "---", ""]

    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return counts


# ---------------------------------------------------------------------------
def schreibe_pruefliste(rows: list[dict], out_csv: str, out_md: str) -> int:
    """Phase 02-05: nach Muster gruppierte Einzelfaelle."""
    ein = [r for r in rows if r["freigabe"] == "nein" and r["phase"] in ("02", "03", "04", "05")]
    gruppen: dict[str, list[dict]] = defaultdict(list)
    for r in ein:
        gruppen[muster(r)].append(r)

    # CSV: nach Gruppe sortiert, mit Gruppenspalte und leerer Entscheidungsspalte
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["entscheidung_ja_nein", "gruppe", "kontakt", "feld", "alt",
                    "vorschlag", "email", "begruendung", "hubspot_url"])
        for g in sorted(gruppen, key=lambda k: -len(gruppen[k])):
            for r in sorted(gruppen[g], key=lambda x: x["contact_id"]):
                w.writerow(["", g, r["contact_id"], r["feld"], r["alt"], r["neu"],
                            r["email"], r["begruendung"], r["hubspot_url"]])

    lines = ["# Prueffaelle Phase 02-05", "",
             f"{len({r['contact_id'] for r in ein})} Kontakte, nach Muster gruppiert.",
             "Pro Gruppe einmal entscheiden, nicht pro Zeile.", ""]
    for g in sorted(gruppen, key=lambda k: -len(gruppen[k])):
        rs = gruppen[g]
        kontakte = len({r["contact_id"] for r in rs})
        lines += [f"## {g}", "",
                  f"**{kontakte} Kontakte** ({len(rs)} Feldwerte)", "",
                  "| E-Mail | Feld | jetzt | Vorschlag |", "|---|---|---|---|"]
        for r in rs[:10]:
            lines.append(f"| `{r['email']}` | {r['feld']} | "
                         f"`{r['alt'] or '(leer)'}` | `{r['neu']}` |")
        if len(rs) > 10:
            lines.append(f"| … | … | … | +{len(rs)-10} weitere |")
        lines += ["", "**Entscheidung:** [ ] Gruppe uebernehmen   "
                  "[ ] Gruppe verwerfen   [ ] einzeln pruefen", "", "---", ""]
    with open(out_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return len({r["contact_id"] for r in ein})


# ---------------------------------------------------------------------------
def herkunft(begruendung: str) -> str:
    """Woher kommt die Laendervorwahl im Vorschlag?"""
    if "Vorwahl" in begruendung and "bereits enthalten" in begruendung:
        return "war schon da, nur '+' fehlte"
    if "E-Mail-TLD" in begruendung:
        m = re.search(r"E-Mail-TLD (\.\w+)", begruendung)
        return f"aus E-Mail-Domain {m.group(1)}" if m else "aus E-Mail-Domain"
    if "Landesangabe" in begruendung:
        return "aus Feld country"
    if "E.164 formatiert" in begruendung:
        return "unveraendert, nur Format bereinigt"
    if "Durchwahl" in begruendung:
        return "Durchwahl vermutet -- pruefen"
    return "sonstiges"


def schreibe_telefon(rows: list[dict], out_csv: str, out_md: str) -> tuple[int, int]:
    tel = [r for r in rows if r["feld"] in ("phone", "mobilephone")]
    auto = [r for r in tel if r["freigabe"] == "ja"]
    pruef = [r for r in tel if r["freigabe"] == "nein"]

    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["freigabe", "kontakt", "feld", "jetzt", "vorschlag",
                    "vorwahl_herkunft", "konfidenz", "email", "hubspot_url"])
        for r in tel:
            w.writerow([r["freigabe"], r["contact_id"], r["feld"], r["alt"], r["neu"],
                        herkunft(r["begruendung"]), r["konfidenz"], r["email"],
                        r["hubspot_url"]])

    gruppen: dict[str, list[dict]] = defaultdict(list)
    for r in auto:
        gruppen[herkunft(r["begruendung"])].append(r)

    lines = ["# Telefonnummern auf E.164", "",
             f"**{len(auto)} Vorschlaege** mit hoher Konfidenz, "
             f"**{len(pruef)}** zur Pruefung.", "",
             "Gruppiert nach Herkunft der Laendervorwahl — die Gruppen unterscheiden",
             "sich im Risiko: eine bereinigte Formatierung ist unkritisch, eine",
             "ergaenzte Vorwahl ist eine Annahme.", ""]
    for g in sorted(gruppen, key=lambda k: -len(gruppen[k])):
        rs = gruppen[g]
        lines += [f"## {g}", "", f"**{len(rs)} Nummern**", "",
                  "| jetzt | Vorschlag | E-Mail |", "|---|---|---|"]
        for r in rs[:12]:
            lines.append(f"| `{r['alt']}` | `{r['neu']}` | `{r['email']}` |")
        if len(rs) > 12:
            lines.append(f"| … | … | +{len(rs)-12} weitere |")
        lines += [""]
        vw = Counter(re.match(r"\+\d{1,3}", r["neu"]).group(0)
                     for r in rs if re.match(r"\+\d{1,3}", r["neu"]))
        lines += ["Vorwahlen in dieser Gruppe: "
                  + ", ".join(f"`{k}` ({n})" for k, n in vw.most_common(8)), "", "---", ""]
    if pruef:
        lines += ["## Zur Pruefung, nicht automatisch", "",
                  "| jetzt | Vorschlag | Grund | E-Mail |", "|---|---|---|---|"]
        for r in pruef:
            lines.append(f"| `{r['alt']}` | `{r['neu']}` | {r['begruendung'][:60]} "
                         f"| `{r['email']}` |")
    with open(out_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return len(auto), len(pruef)


# ---------------------------------------------------------------------------
def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    src = argv[1]
    out = argv[2] if len(argv) > 2 else os.path.join(os.path.dirname(src) or ".", "vorschlaege")
    os.makedirs(out, exist_ok=True)
    rows = read(src)

    e = schreibe_entscheidungen(rows, os.path.join(out, "entscheidungen.md"))
    n = schreibe_pruefliste(rows, os.path.join(out, "pruefliste.csv"),
                            os.path.join(out, "pruefliste.md"))
    ta, tp = schreibe_telefon(rows, os.path.join(out, "telefon.csv"),
                              os.path.join(out, "telefon.md"))

    print(f"Regelentscheidungen (Phase 06): {sum(e.values())} Kontakte in {len(e)} Regeln")
    for k, v in e.items():
        print(f"    {k:10s} {v:6d}")
    print(f"Einzelfaelle (Phase 02-05)     : {n} Kontakte")
    print(f"Telefon                        : {ta} Vorschlaege, {tp} zur Pruefung")
    print(f"\ngeschrieben nach {out}/:")
    for f in sorted(os.listdir(out)):
        print(f"    {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
