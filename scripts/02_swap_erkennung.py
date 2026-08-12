#!/usr/bin/env python3
"""Verfeinerte Vorname/Nachname-Swap-Erkennung + Anrede-Check."""
import json, re, os, unicodedata
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
    for r in json.loads(raw[raw.index("{"):])["results"]:
        if r["id"] in seen: continue
        seen.add(r["id"]); p = r["properties"]; p["_id"] = str(r["id"]); rows.append(p)

def g(r,k):
    v = r.get(k); return "" if v is None else str(v).strip()
def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()

# Vornamen-Lexikon (DE/AT/CH + international, gaengige Formen)
GIVEN = set("""
alexander alexandra alina alois amelie andre andrea andreas andreea angela anja anke anna
annalena anne annette annika anton antonia ardit arne arnold artur astrid axel barbara
bastian beate benedikt benjamin bernd bernhard bettina birgit bjorn bruno burkhard
camilo carina carl carla carlo carmen carola carolin caroline carsten catharina cathrin
chiara christa christian christiane christina christine christof christoph claudia clemens
conny constanze cornelia corinna damian daniel daniela danny david dennis dieter dirk
dominic dominik dorothea edouard eduard elena elisabeth ellen elke emanuel emil emma
enrico eric erik erika ernst esther eva fabian fabienne felix ferdinand florian frank
franziska frederieke frederik friedrich gabriel gabriele gaetan gebhard georg gerald
gerd gerhard gerlinde gernot gertrud gisela giorgio gregor grit guido gunter gustav
hannah hanno hans harald hartmut hedwig heidi heike heiko heinrich heinz helena helga
helmut hendrik henning henrik herbert hermann hilde holger horst hubert huber ida ilka
ines inga ingo ingrid irene iris isabel isabell isabella isabelle ivan jakob james jamil
jan jana janina janine jasmin jennifer jens jessica joachim jochen joelle johann johanna
johannes jonas jorg josef judith julia julian julius jurgen justus kai karen karin karl
karsten katarina katharina kathrin katja katrin kerstin kevin klaus konrad kristin kristina
kurt lara larissa lars laura lena leon leonie lilian lina lisa lorenz lothar luca lucas
ludwig luisa lukas madina magnus maik maike manfred manuel manuela marc marcel marco marcus
maren margarete maria marie marina mario marion marius mark markus marlene marta martin
martina mathias mathilde matthias maximilian melanie michael michaela michele miranda mirco
mirko monika moritz nadine natalia nathalie nico nicola nicolas nicole niels nikolaus nils
nina norbert norman olaf oliver otto paolo pascal patricia patrick paul paula peter petra
philip philipp philippe pia rainer ralf ralph raphael rebecca regina reiner reinhard rene
renate ricarda richard rita robert roland rolf romy ronald rosa rudolf rupa ruslan ruth
sabine sabrina sandra sara sarah saskia sebastian silke silvia simon simone sofia sonja
sophia sophie stefan stefanie steffen stephan stephanie sten susanne svenja sven sybille
tanja tatjana theo thomas tilo tim timo tobias tom torsten udo ulf ulrich ulrike ursula
uta ute uwe valentin vanessa veronika victoria viktor vivien volker waldemar walter
werner wilhelm wolfgang yannick yusuf zana chris karla nadja leon jamie sam
""".split())

def is_given(tok):
    t = norm(tok).replace("-", " ").split()
    return any(x in GIVEN for x in t) if t else False

# --- Verlaesslichkeit des E-Mail-Reihenfolge-Signals messen ---
order_stats = Counter()
swapped, correct, ambiguous = [], [], []

for r in rows:
    fn, ln, email = g(r,"firstname"), g(r,"lastname"), g(r,"email")
    if not (fn and ln and "@" in email):
        continue
    local = norm(email.split("@")[0])
    nfn, nln = norm(fn), norm(ln)
    if len(nfn) < 3 or len(nln) < 3:
        continue
    if not (nfn in local and nln in local):
        continue
    fn_is, ln_is = is_given(fn), is_given(ln)
    email_order = "fn_first" if local.find(nfn) < local.find(nln) else "ln_first"

    if fn_is and not ln_is:
        correct.append((r, email_order)); order_stats[("felder_ok", email_order)] += 1
    elif ln_is and not fn_is:
        swapped.append((r, email_order)); order_stats[("vertauscht", email_order)] += 1
    else:
        ambiguous.append((r, email_order, fn_is, ln_is))
        order_stats[("unklar", email_order)] += 1

print("=== Kreuzcheck: Lexikon-Urteil vs. E-Mail-Reihenfolge ===")
for k,v in sorted(order_stats.items()):
    print(f"  {k[0]:12s} / email={k[1]:9s}: {v:4d}")

print(f"\n=== EINDEUTIG VERTAUSCHT (Nachname steht im Vorname-Feld): {len(swapped)} ===")
for r, eo in swapped:
    print(f"  {r['_id']}  firstname={g(r,'firstname')!r:26s} lastname={g(r,'lastname')!r:22s} "
          f"email={g(r,'email'):48s} anrede={g(r,'salutation')!r}")

print(f"\n=== FELDER KORREKT: {len(correct)} ===")
print(f"=== UNKLAR (beide/keiner im Lexikon): {len(ambiguous)} ===")
for r, eo, a, b in ambiguous:
    print(f"  {r['_id']}  fn={g(r,'firstname')!r:22s} ln={g(r,'lastname')!r:20s} "
          f"email={g(r,'email'):46s} emailorder={eo} fn_given={a} ln_given={b}")

# --- Swap-Verdacht auch OHNE E-Mail-Bestaetigung: Lexikon allein ---
print("\n=== ZUSATZ: Lexikon-Verdacht ohne E-Mail-Match ===")
extra = []
for r in rows:
    fn, ln, email = g(r,"firstname"), g(r,"lastname"), g(r,"email")
    if not (fn and ln): continue
    local = norm(email.split("@")[0]) if "@" in email else ""
    nfn, nln = norm(fn), norm(ln)
    if len(nfn) >= 3 and len(nln) >= 3 and nfn in local and nln in local:
        continue  # schon oben behandelt
    if is_given(ln) and not is_given(fn):
        extra.append(r)
for r in extra:
    print(f"  {r['_id']}  fn={g(r,'firstname')!r:24s} ln={g(r,'lastname')!r:20s} email={g(r,'email')}")
print(f"  -> {len(extra)} weitere Verdachtsfaelle")

total_swap = len(swapped) + len(extra)
print(f"\n>>> GESAMT klar vertauscht: {total_swap} von {len(rows)} = {100*total_swap/len(rows):.1f}%")

# --- Anrede-Konsistenz ---
print("\n=== ANREDE (salutation) ===")
c = Counter(g(r,"salutation") or "(leer)" for r in rows)
for k,v in c.most_common(20):
    print(f"  {k!r:24s} {v:4d}")

# Anrede vs. Vorname-Geschlecht (grobe Heuristik: weibliche Endungen/Namen)
FEMALE = set("""andrea alexandra alina amelie angela anja anke anna annalena anne annette annika
antonia astrid barbara beate bettina birgit carina carla carmen carola carolin caroline
catharina cathrin chiara christa christiane christina christine claudia conny constanze
cornelia corinna daniela dorothea elena elisabeth ellen elke emma erika esther eva fabienne
franziska frederieke gabriele gerlinde gertrud gisela grit hannah heidi heike helena helga
hilde ida ilka ines inga ingrid irene iris isabel isabell isabella isabelle jana janina
janine jasmin jennifer jessica joelle johanna judith julia karen karin katarina katharina
kathrin katja katrin kerstin kristin kristina lara larissa laura lena leonie lilian lina
lisa luisa madina maike manuela maren margarete maria marie marina marion marlene marta
martina mathilde melanie michaela miranda monika nadine natalia nathalie nicola nicole
nina patricia paula petra pia regina renate ricarda rita romy rosa rupa ruth sabine sabrina
sandra sara sarah saskia silke silvia simone sofia sonja sophia sophie stefanie stephanie
susanne svenja sybille tanja tatjana ulrike ursula uta ute vanessa veronika victoria vivien
zana daniela karla nadja""".split())
MALE_HINT = set("""alexander andre andreas alois anton ardit arne arnold artur axel bastian
benedikt benjamin bernd bernhard bjorn bruno burkhard camilo carl carlo carsten christian
christof christoph clemens damian daniel danny david dennis dieter dirk dominic dominik
edouard eduard emanuel emil enrico eric erik ernst fabian felix ferdinand florian frank
frederik friedrich gabriel gaetan gebhard georg gerald gerd gerhard gernot giorgio gregor
guido gunter gustav hanno hans harald hartmut heiko heinrich heinz helmut hendrik henning
henrik herbert hermann holger horst hubert huber ivan jakob james jamil jan jens joachim
jochen johann johannes jonas jorg josef julian julius jurgen justus kai karl karsten kevin
klaus konrad kurt lars leon lorenz lothar luca lucas ludwig lukas magnus maik manfred manuel
marc marcel marco marcus mario marius mark markus martin mathias matthias maximilian michael
michele mirco mirko moritz nico nicolas niels nikolaus nils norbert norman olaf oliver otto
paolo pascal patrick paul peter philip philipp philippe rainer ralf ralph raphael reiner
reinhard rene richard robert roland rolf ronald rudolf ruslan sebastian simon stefan steffen
stephan sten sven thomas tilo tim timo tobias tom torsten udo ulf ulrich uwe valentin viktor
volker waldemar walter werner wilhelm wolfgang yannick yusuf chris""".split())

mismatch = []
for r in rows:
    sal = norm(g(r,"salutation")); fn = norm(g(r,"firstname")).split()
    if not sal or not fn: continue
    first = fn[0]
    fem_sal = sal in ("frau","ms.","ms","mrs.","mrs","miss")
    male_sal = sal in ("herr","mr.","mr")
    if fem_sal and first in MALE_HINT and first not in FEMALE:
        mismatch.append((r,"Anrede Frau / maennl. Vorname"))
    if male_sal and first in FEMALE:
        mismatch.append((r,"Anrede Herr / weibl. Vorname"))
print(f"\n  Anrede/Vorname-Widerspruch: {len(mismatch)}")
for r,why in mismatch[:25]:
    print(f"      {r['_id']}  {why:34s} anrede={g(r,'salutation')!r} fn={g(r,'firstname')!r} ln={g(r,'lastname')!r}")

# --- Firmenname-Konsistenz: gleiche E-Mail-Domain, unterschiedlicher company-Text ---
print("\n=== FIRMENNAME INKONSISTENT je E-Mail-Domain ===")
dom_comp = defaultdict(set)
for r in rows:
    e = g(r,"email")
    if "@" in e and g(r,"company"):
        dom_comp[e.split("@")[-1].lower()].add(g(r,"company"))
incons = {d:c for d,c in dom_comp.items() if len(c) > 1}
print(f"  {len(incons)} Domains mit abweichenden Firmennamen")
for d,c in sorted(incons.items()):
    print(f"      {d:38s} {sorted(c)}")

# --- Firmenname mit Rechtsform-Rauschen / Slogans ---
print("\n=== FIRMENNAME auffaellig (Slogan/Sonderzeichen/sehr lang) ===")
for r in rows:
    comp = g(r,"company")
    if comp and (len(comp) > 40 or re.search(r"[|]|\.{3}|  +", comp)):
        print(f"      {r['_id']}  company={comp!r}")

# --- Jobtitle-Rauschen ---
print("\n=== JOBTITLE auffaellig (mehrsprachig/zu lang/Trenner) ===")
n_long = 0
for r in rows:
    jt = g(r,"jobtitle")
    if jt and (len(jt) > 45 or re.search(r"\s[/|]\s|\s//\s", jt)):
        n_long += 1
        if n_long <= 20:
            print(f"      {r['_id']}  {jt!r}")
print(f"  -> {n_long} Kontakte mit langem/mehrsprachigem Jobtitel ({100*n_long/len(rows):.1f}%)")
