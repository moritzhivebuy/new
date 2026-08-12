#!/usr/bin/env python3
"""Datenqualitaets-Analyse der letzten 500 HubSpot-Kontakte."""
import json, re, glob, os, unicodedata
from collections import Counter, defaultdict

import sys

def _input_files():
    """JSON-Antworten der HubSpot Search-API als CLI-Argumente."""
    if len(sys.argv) < 2:
        sys.exit(f"Aufruf: {sys.argv[0]} <search-api-response.json> [weitere.json ...]")
    return sys.argv[1:]

FILES = _input_files()

rows = []
seen_ids = set()
for f in FILES:
    p = f
    raw = open(p, encoding="utf-8").read()
    # Datei kann Praefix-Text enthalten -> erstes '{' suchen
    start = raw.index("{")
    data = json.loads(raw[start:])
    for r in data["results"]:
        if r["id"] in seen_ids:
            continue
        seen_ids.add(r["id"])
        props = r["properties"]
        props["_id"] = str(r["id"])
        rows.append(props)
    print(f"{f}: {len(data['results'])} rows, total_in_portal={data.get('total')}")

print(f"\n=== {len(rows)} eindeutige Kontakte geladen ===\n")

def g(r, k):
    v = r.get(k)
    if v is None:
        return ""
    return str(v).strip()

# ---------- 1. Befuellungsgrad ----------
FIELDS = ["firstname","lastname","email","phone","mobilephone","company","jobtitle",
          "salutation","country","city","zip","lifecyclestage","hs_analytics_source",
          "hs_object_source_label","hs_email_domain","hs_language","website",
          "hubspot_owner_id","hs_marketable_status","contact_typ__channel_",
          "hs_lead_status","associatedcompanyid"]
print("--- 1) BEFUELLUNGSGRAD (leer / 500) ---")
for f in FIELDS:
    empty = sum(1 for r in rows if not g(r, f))
    print(f"  {f:28s} leer: {empty:4d}  ({100*empty/len(rows):5.1f}%)")

# ---------- 2. Quellen-Verteilung ----------
print("\n--- 2) VERTEILUNG record source / traffic source / lifecycle ---")
for f in ["hs_object_source_label","hs_analytics_source","lifecyclestage","contact_typ__channel_","hs_language","country"]:
    c = Counter(g(r,f) or "(leer)" for r in rows)
    print(f"  {f}:")
    for k,v in c.most_common(12):
        print(f"      {k:32s} {v:4d}")

# ---------- 3. Namensfeld-Probleme ----------
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}")
PHONEISH = re.compile(r"^[\d\s\+\-\(\)/\.]{5,}$")
URLISH = re.compile(r"(https?://|www\.)", re.I)

# Rollen-/Funktions-Begriffe statt Personenname
ROLE_WORDS = ["einkauf","purchas","procure","info","kontakt","contact","service","support",
              "buchhaltung","accounting","verwaltung","office","zentrale","team","abteilung",
              "sekretariat","empfang","vertrieb","sales","marketing","personal","hr",
              "rechnung","invoice","bestellung","order","operativ","strategisch","zentraleinkauf",
              "gmbh","ag","kg","mbh","e.k.","ltd","inc","b.v.","s.a.","admin","noreply","no-reply"]

TITLE_WORDS = ["dr.","dr","prof.","prof","dipl.","dipl","ing.","ing","mag.","mag","b.sc","m.sc",
               "mba","herr","frau","mr.","mrs.","ms.","llm"]

def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()

issues = defaultdict(list)

def flag(cat, r, detail):
    issues[cat].append((r["_id"], detail))

for r in rows:
    fn, ln = g(r,"firstname"), g(r,"lastname")
    email = g(r,"email")
    comp  = g(r,"company")
    phone, mob = g(r,"phone"), g(r,"mobilephone")

    # 3a fehlende Namen
    if not fn and not ln:
        flag("A1_name_komplett_leer", r, f"email={email}")
    elif not fn:
        flag("A2_vorname_leer", r, f"lastname={ln} email={email}")
    elif not ln:
        flag("A3_nachname_leer", r, f"firstname={fn} email={email}")

    # 3b E-Mail im Namensfeld
    for fld, val in (("firstname",fn),("lastname",ln),("company",comp)):
        if val and EMAIL_RE.search(val):
            flag("B1_email_in_"+fld, r, f"{fld}={val!r}")

    # 3c Telefon/URL im Namensfeld
    for fld, val in (("firstname",fn),("lastname",ln)):
        if val and PHONEISH.match(val):
            flag("B2_telefonartig_in_"+fld, r, f"{fld}={val!r}")
        if val and URLISH.search(val):
            flag("B3_url_in_"+fld, r, f"{fld}={val!r}")

    # 3d Name = ganze E-Mail-Adresse oder local-part
    if email:
        local = email.split("@")[0]
        if fn and norm(fn) == norm(local):
            flag("B4_vorname_ist_email_localpart", r, f"firstname={fn!r} email={email}")
        if ln and norm(ln) == norm(local):
            flag("B5_nachname_ist_email_localpart", r, f"lastname={ln!r} email={email}")

    # 3e Rollen-/Funktionsname statt Person
    for fld, val in (("firstname",fn),("lastname",ln)):
        n = norm(val)
        if n and any(re.search(r"\b"+re.escape(w)+r"\b", n) or n == w for w in ROLE_WORDS):
            flag("C1_rollenname_in_"+fld, r, f"{fld}={val!r} email={email}")

    # 3f Vorname+Nachname in EINEM Feld (mehrere Tokens im Vornamen bei leerem Nachnamen o. Umgekehrt)
    if fn and not ln and len(fn.split()) >= 2:
        flag("C2_vollname_in_firstname", r, f"firstname={fn!r}")
    if ln and not fn and len(ln.split()) >= 2:
        flag("C3_vollname_in_lastname", r, f"lastname={ln!r}")

    # 3g Gross-/Kleinschreibung
    for fld, val in (("firstname",fn),("lastname",ln)):
        letters = [c for c in val if c.isalpha()]
        if len(letters) >= 3:
            if all(c.isupper() for c in letters):
                flag("D1_ALLCAPS_"+fld, r, f"{fld}={val!r}")
            elif all(c.islower() for c in letters):
                flag("D2_alllower_"+fld, r, f"{fld}={val!r}")

    # 3h Titel im Namensfeld
    for fld, val in (("firstname",fn),("lastname",ln)):
        toks = norm(val).replace(",", " ").split()
        if toks and any(t in TITLE_WORDS for t in toks):
            flag("D3_titel_in_"+fld, r, f"{fld}={val!r}")

    # 3i Whitespace / Sonderzeichen-Muell
    for fld in ("firstname","lastname","email","company","jobtitle"):
        raw = r.get(fld)
        if raw is not None and isinstance(raw,str) and raw != raw.strip():
            flag("D4_whitespace_"+fld, r, f"{fld}={raw!r}")
    for fld, val in (("firstname",fn),("lastname",ln)):
        if val and re.search(r"[0-9_]|\s{2,}|[!\"#$%&*+=<>?@\[\]\\^{}|~]", val):
            flag("D5_sonderzeichen_"+fld, r, f"{fld}={val!r}")

    # 3j Vorname/Nachname vertauscht -> Abgleich mit E-Mail local-part
    if email and fn and ln and "@" in email:
        local = norm(email.split("@")[0])
        nfn, nln = norm(fn), norm(ln)
        # Muster "nachname.vorname" bzw. local beginnt mit Nachname und endet mit Vorname
        if len(nfn) > 2 and len(nln) > 2 and nfn in local and nln in local:
            if local.find(nln) < local.find(nfn):
                flag("E1_verdacht_vor_nachname_vertauscht", r,
                     f"firstname={fn!r} lastname={ln!r} email={email}")

    # 3k E-Mail-Validitaet / Typ
    if email:
        if not EMAIL_RE.fullmatch(email):
            flag("F1_email_syntaktisch_ungueltig", r, f"email={email!r}")
        if email != email.lower():
            flag("F2_email_gross_klein", r, f"email={email!r}")
        dom = email.split("@")[-1].lower()
        FREEMAIL = {"gmail.com","googlemail.com","gmx.de","gmx.net","gmx.at","gmx.ch","web.de",
                    "yahoo.com","yahoo.de","hotmail.com","hotmail.de","outlook.com","outlook.de",
                    "live.com","live.de","icloud.com","me.com","aol.com","t-online.de","freenet.de",
                    "mail.de","posteo.de","protonmail.com","proton.me","bluewin.ch","hispeed.ch"}
        if dom in FREEMAIL:
            flag("F3_freemail_domain", r, f"email={email} source={g(r,'hs_object_source_label')}")
        if g(r,"hs_email_bad_address") in ("true","True"):
            flag("F4_email_bad_address", r, f"email={email}")
    else:
        flag("F0_email_fehlt", r, f"name={fn} {ln} source={g(r,'hs_object_source_label')}")

    # 3l Telefon-Formatierung (E.164?)
    for fld, val in (("phone",phone),("mobilephone",mob)):
        if val:
            digits = re.sub(r"\D","",val)
            if not val.startswith("+"):
                flag("G1_telefon_ohne_ländervorwahl_"+fld, r, f"{fld}={val!r}")
            if re.search(r"[a-zA-Z]", val):
                flag("G2_telefon_mit_buchstaben_"+fld, r, f"{fld}={val!r}")
            if len(digits) < 7:
                flag("G3_telefon_zu_kurz_"+fld, r, f"{fld}={val!r}")

    # 3m company-Feld vs. associatedcompanyid
    if comp and not g(r,"associatedcompanyid"):
        flag("H1_company_text_ohne_verknuepfung", r, f"company={comp!r}")
    if not comp and g(r,"associatedcompanyid"):
        flag("H2_verknuepfung_ohne_company_text", r, f"companyid={g(r,'associatedcompanyid')}")

    # 3n Domain-Mismatch: E-Mail-Domain vs. company-Name (grobe Heuristik)
    # nur Info, kein Auto-Fix

    # 3o Land / Sprache fehlt trotz vorhandener Telefonnummer mit Vorwahl
    if not g(r,"country"):
        flag("I1_land_leer", r, "")
    if not g(r,"hs_language"):
        flag("I2_sprache_leer", r, "")

# ---------- 4. Dubletten ----------
print("\n--- 4) DUBLETTEN ---")
by_email = defaultdict(list)
by_name  = defaultdict(list)
for r in rows:
    e = g(r,"email").lower()
    if e:
        by_email[e].append(r["_id"])
    key = (norm(g(r,"firstname")), norm(g(r,"lastname")))
    if key[0] and key[1]:
        by_name[key].append(r["_id"])
dup_email = {k:v for k,v in by_email.items() if len(v)>1}
dup_name  = {k:v for k,v in by_name.items() if len(v)>1}
print(f"  identische E-Mail mehrfach: {len(dup_email)} Gruppen")
for k,v in list(dup_email.items())[:15]:
    print(f"      {k} -> {v}")
print(f"  identischer Vor+Nachname mehrfach: {len(dup_name)} Gruppen")
for k,v in list(dup_name.items())[:15]:
    print(f"      {k} -> {v}")

# ---------- 5. Ausgabe aller Findings ----------
print("\n--- 5) FINDINGS nach Kategorie ---")
for cat in sorted(issues):
    lst = issues[cat]
    print(f"\n### {cat}: {len(lst)} Kontakte ({100*len(lst)/len(rows):.1f}%)")
    for cid, det in lst[:18]:
        print(f"      {cid}  {det}")
    if len(lst) > 18:
        print(f"      ... +{len(lst)-18} weitere")

# ---------- 6. Kreuztabelle: Probleme je Record Source ----------
print("\n--- 6) PROBLEMDICHTE JE RECORD SOURCE ---")
src_of = {r["_id"]: (g(r,"hs_object_source_label") or "(leer)") for r in rows}
src_total = Counter(src_of.values())
KEY_CATS = [c for c in issues if c.startswith(("A","B","C","E","F0","F1","F3"))]
tab = defaultdict(Counter)
for cat in KEY_CATS:
    for cid,_ in issues[cat]:
        tab[src_of[cid]][cat] += 1
for src, n in src_total.most_common():
    print(f"\n  {src}  (n={n})")
    for cat, c in tab[src].most_common():
        print(f"      {cat:38s} {c:4d}  ({100*c/n:.0f}%)")
