#!/usr/bin/env python3
"""Klassifikation aller Kontakte OHNE Vorname: automatisch reparierbar vs. Rollen-Postfach."""
import json, re, os
from collections import Counter, defaultdict

import sys

def _input_files():
    """JSON-Antworten der HubSpot Search-API als CLI-Argumente."""
    if len(sys.argv) < 2:
        sys.exit(f"Aufruf: {sys.argv[0]} <search-api-response.json> [weitere.json ...]")
    return sys.argv[1:]

FILES = _input_files()

rows, seen = [], set()
for f in FILES:
    raw = open(f, encoding="utf-8").read()
    d = json.loads(raw[raw.index("{"):])
    for r in d["results"]:
        if r["id"] in seen: continue
        seen.add(r["id"]); p = r["properties"]; p["_id"] = str(r["id"]); rows.append(p)
print(f"geladen: {len(rows)} Kontakte ohne Vorname (total laut API: {d.get('total')})\n")

def g(r,k):
    v = r.get(k); return "" if v is None else str(v).strip()

# Rollen-/Funktions-Postfaecher
ROLE_TOKENS = {"info","kontakt","contact","office","service","support","hilfe","help","team",
    "zentrale","empfang","reception","sekretariat","mail","email","post","webmaster","admin",
    "administrator","noreply","no-reply","donotreply","bestellung","bestellungen","order","orders",
    "ordering","einkauf","purchasing","purchase","procurement","eprocure","eprocurement","edi",
    "buchhaltung","accounting","rechnung","rechnungen","invoice","invoices","finance","billing",
    "buchhalt","kreditoren","debitoren","ap","ar","vertrieb","sales","verkauf","marketing",
    "presse","press","pr","hr","personal","jobs","bewerbung","karriere","career","recruiting",
    "it","edv","logistik","logistics","versand","shipping","lager","qm","qs","technik","technical",
    "scm","adminscm","shop","web","online","newsletter","abo","datenschutz","privacy","legal",
    "compliance","gf","geschaeftsfuehrung","vorstand","board","buero","bureau","zentraleinkauf",
    "materialwirtschaft","beschaffung","disposition","dispo","ek","zek","central","group","gruppe",
    "mail-in","inbox","tickets","ticket","anfrage","anfragen","request","requests","kundenservice",
    "customerservice","kundendienst","crm","erp","sap","system","test","demo","dummy","noname"}

def classify(email):
    """-> (kategorie, abgeleiteter_vorname, abgeleiteter_nachname)"""
    if not email or "@" not in email:
        return ("X_keine_email", "", "")
    local = email.split("@")[0].lower()
    core = re.sub(r"\+.*$", "", local)            # plus-Adressierung entfernen
    core = re.sub(r"\d+$", "", core)               # trailing Ziffern
    parts = [p for p in re.split(r"[._\-]+", core) if p]

    # Rollen-Postfach?
    if any(p in ROLE_TOKENS for p in parts) or core in ROLE_TOKENS:
        return ("R_rollen_postfach", "", "")

    # vorname.nachname -> beide Teile >= 3 Zeichen und alphabetisch
    if len(parts) == 2 and all(len(p) >= 3 and p.isalpha() for p in parts):
        return ("A_auto_vorname_nachname", parts[0].capitalize(), parts[1].capitalize())

    # v.nachname / vnachname (Initial + Nachname)
    if len(parts) == 2 and len(parts[0]) == 1 and len(parts[1]) >= 3 and parts[1].isalpha():
        return ("B_initial_plus_nachname", "", parts[1].capitalize())
    if len(parts) == 1 and core.isalpha() and 4 <= len(core) <= 20:
        # nur nachname ODER initial+nachname zusammengeschrieben -> unsicher
        return ("C_nur_nachname_vermutlich", "", core.capitalize())

    # vorname.mittel.nachname -- nur wenn ERSTES und LETZTES Token je >= 3 Buchstaben
    if len(parts) >= 3 and all(p.isalpha() for p in parts):
        if len(parts[0]) >= 3 and len(parts[-1]) >= 3:
            return ("A_auto_vorname_nachname", parts[0].capitalize(), parts[-1].capitalize())
        # sonst: Doppelname/Initial im Spiel -> nicht automatisch
        cand = [p for p in parts if len(p) >= 3]
        if cand:
            return ("B_initial_plus_nachname", "", cand[-1].capitalize())
        return ("D_unklar_manuell", "", "")

    return ("D_unklar_manuell", "", "")

buckets = defaultdict(list)
for r in rows:
    cat, fn, ln = classify(g(r,"email"))
    buckets[cat].append((r, fn, ln))

print("=== KLASSIFIKATION der Kontakte ohne Vorname ===")
tot = len(rows)
LABELS = {
 "A_auto_vorname_nachname": "vollautomatisch befuellbar (vorname.nachname@)",
 "B_initial_plus_nachname": "Nachname automatisch, Vorname nur Initial -> Enrichment/manuell",
 "C_nur_nachname_vermutlich": "nur ein Token -> Nachname wahrscheinlich, pruefen",
 "R_rollen_postfach": "ROLLEN-/FUNKTIONSPOSTFACH -> KEIN Personenname, taggen",
 "D_unklar_manuell": "unklar -> manuell / Enrichment",
 "X_keine_email": "keine E-Mail vorhanden",
}
for cat in ["A_auto_vorname_nachname","B_initial_plus_nachname","C_nur_nachname_vermutlich",
            "R_rollen_postfach","D_unklar_manuell","X_keine_email"]:
    n = len(buckets[cat])
    print(f"  {cat:28s} {n:4d}  ({100*n/tot:5.1f}%)  {LABELS[cat]}")

for cat in ["A_auto_vorname_nachname","B_initial_plus_nachname","R_rollen_postfach","D_unklar_manuell","X_keine_email"]:
    print(f"\n--- {cat} (Beispiele) ---")
    for r, fn, ln in buckets[cat][:14]:
        cur_ln = g(r,"lastname")
        print(f"  {r['_id']}  {g(r,'email'):50s} src={g(r,'hs_object_source_label'):14s} "
              f"lc={g(r,'lifecyclestage'):20s} -> fn={fn!r} ln={ln!r} (ln bisher={cur_ln!r})")

# Quelle x Kategorie
print("\n=== QUELLE x KATEGORIE ===")
tab = defaultdict(Counter)
for cat, lst in buckets.items():
    for r,_,_ in lst:
        tab[g(r,"hs_object_source_label") or "(leer)"][cat] += 1
for src in sorted(tab, key=lambda s: -sum(tab[s].values())):
    n = sum(tab[src].values())
    print(f"  {src}  (n={n})")
    for cat, c in tab[src].most_common():
        print(f"      {cat:28s} {c:4d}")

# Lifecyclestage der Rollenpostfaecher (Relevanz!)
print("\n=== Rollen-Postfaecher nach Lifecycle Stage ===")
print("  ", Counter(g(r,'lifecyclestage') for r,_,_ in buckets["R_rollen_postfach"]).most_common())
print("\n=== Auto-befuellbare nach Lifecycle Stage ===")
print("  ", Counter(g(r,'lifecyclestage') for r,_,_ in buckets["A_auto_vorname_nachname"]).most_common())

# CSV fuer den Import-Fix erzeugen
import csv
out = os.environ.get("DQ_OUT", "fix_namen_vorschlag.csv")
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["Record ID","E-Mail","Datensatzquelle","Kategorie","Vorname_neu","Nachname_neu","Nachname_alt","Aktion"])
    for cat in ["A_auto_vorname_nachname","B_initial_plus_nachname","C_nur_nachname_vermutlich",
                "R_rollen_postfach","D_unklar_manuell","X_keine_email"]:
        for r, fn, ln in buckets[cat]:
            aktion = {"A_auto_vorname_nachname":"automatisch setzen",
                      "B_initial_plus_nachname":"Nachname setzen, Vorname anreichern",
                      "C_nur_nachname_vermutlich":"pruefen",
                      "R_rollen_postfach":"als Funktionspostfach taggen, Name leer lassen",
                      "D_unklar_manuell":"manuell",
                      "X_keine_email":"manuell"}[cat]
            w.writerow([r["_id"], g(r,"email"), g(r,"hs_object_source_label"), cat, fn, ln, g(r,"lastname"), aktion])
print(f"\nCSV geschrieben: {out}")
