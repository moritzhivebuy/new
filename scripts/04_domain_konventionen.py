#!/usr/bin/env python3
"""Reihenfolge-Erkennung: welche Domains nutzen vorname.nachname@, welche nachname.vorname@?"""
import csv, re, unicodedata
from collections import defaultdict, Counter

import sys
CSV = sys.argv[1] if len(sys.argv) > 1 else "fix_namen_vorschlag.csv"
rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8"))
        if r["Kategorie"] == "A_auto_vorname_nachname"]

GIVEN = set("""alexander alexandra alina alois amelie amina andre andrea andreas andreea angela anja
anke anna annalena anne annette annika anton antonia ardit arne arnold aron artur astrid attila axel
ayse barbara bastian beate beatrix benedikt benjamin bernd bernhard bettina birgit bjorn bruno
burkhard camilo carina carl carla carlo carmen carola carolin caroline carsten catharina cathrin
cem charles chiara chris christa christian christiane christina christine christof christoph claudia
claudine clemens conny constanze cornelia corinna cyril damian daniel daniela danny dario davide
david denis dennis dieter dirk dominic dominik dominique edonita edouard eduard eik elena elif
elisabeth ellen elke emanuel emanuela emil emma emre enes enrico eric erik erika ermir ernst esther
eva fabian fabienne fabio felix ferdinand florian frank franziska frederic frederieke frederik
friedrich gabriel gabriele gaetan gebhard georg gerald gerd gerhard gerlinde gernot gerold ghalia
giorgio goran gregor grit guido gunter gustav hannah hanna hanno hans harald hardy hartmut hedwig
heidi heike heiko heinrich heinz helena helga helmut hendrik henning henriette henrik herbert hermann
hilde ida igor ilka ines inga ingo ingrid irene iris isa isabel isabell isabella isabelle ivan ivaylo
jacob jakob james jamil jan jana janina janine jasmin jennifer jens jessica joachim jochen joel joelle
johann johanna johannes jonas joerg jorg josef judith julia julian julien julius jurgen justus kai
karen karin karl karsten katalin katarina katharina kathrin katja katrin kerstin kevin kishore klaas
klaus konrad kristin kristina kurt lara larissa lars laura lea lena leon leone leonie lilian lina
lion lisa lorenz lothar luca lucas ludwig luise luisa lukas madina magdalena magnus maik maike
malgorzata malee manfred manuel manuela marc marcel marco marcus maren margarete maria marianna
marie marina marion marius mark markus marlene marta martin martina marvin mathias mathilde matthias
maurizio maximilian mehmet melanie merlin merve michael michaela michele mike minfeng miranda mirco
mirko monika nadine nadja nasir natalia nathalie nico nicola nicolas nicole niels niklas nikolaus
nils nina norbert norman olaf oleg oliver olivier otto paolo pascal patrice patricia patrick paul
paula peter petra philip philipp philippe pia polina rainer ralf ralph rami raphael rebecca regina
reiner reinhard rene ricarda richard ringo rita robert roland rolf romain roman romy rosa rudolf rupa
ruslan ruth sabine sabrina samir samuel sandra sanjin sara sarah sascha saskia silke silvia simo
simon simona simone sofia sonja sophia sophie stefan stefanie steffen steffi stephan stephane
stephanie steve sten sujit susanne svenja sven sybille sylvain sylvana tabea tanja tatjana theo
theresa theresia thomas tilo tim timo tobias tom torsten tufan udo ulf ulrich ulrike ursula uta ute
uwe valentin valentina vanessa verena veronika victoria viktor vivien volker waldemar walter werner
wilhelm wolfgang wolfram yannick yilmaz yulia yusuf zana anais""".split())

def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()

def is_given(t):
    return norm(t) in GIVEN

order = Counter()
reversed_rows, ok_rows, unknown_rows = [], [], []
dom_order = defaultdict(Counter)

for r in rows:
    fn, ln = r["Vorname_neu"], r["Nachname_neu"]
    dom = r["E-Mail"].split("@")[-1].lower()
    a, b = is_given(fn), is_given(ln)
    if a and not b:
        order["korrekt (Token1=Vorname)"] += 1; ok_rows.append(r); dom_order[dom]["fn_first"] += 1
    elif b and not a:
        order["VERTAUSCHT (Token1=Nachname)"] += 1; reversed_rows.append(r); dom_order[dom]["ln_first"] += 1
    elif a and b:
        order["beides Vorname (ambig)"] += 1; unknown_rows.append(r)
    else:
        order["unbekannt (kein Lexikontreffer)"] += 1; unknown_rows.append(r)

print("=== Reihenfolge im Auto-Bucket (n=%d) ===" % len(rows))
for k, v in order.most_common():
    print(f"  {k:34s} {v:4d}  ({100*v/len(rows):.1f}%)")

print(f"\n=== VERTAUSCHT: E-Mail ist nachname.vorname@ ({len(reversed_rows)}) ===")
for r in reversed_rows:
    print(f"  {r['E-Mail']:48s} naiv-> fn={r['Vorname_neu']:14s} ln={r['Nachname_neu']:16s} "
          f"KORREKT-> fn={r['Nachname_neu']} ln={r['Vorname_neu']}")

print("\n=== Domains mit erkennbarer Konvention (>=2 Belege) ===")
for dom, c in sorted(dom_order.items(), key=lambda x: -sum(x[1].values())):
    if sum(c.values()) >= 2:
        conv = "nachname.vorname" if c["ln_first"] > c["fn_first"] else "vorname.nachname"
        mixed = " GEMISCHT!" if c["ln_first"] and c["fn_first"] else ""
        print(f"  {dom:34s} fn_first={c['fn_first']:3d} ln_first={c['ln_first']:3d} -> {conv}{mixed}")

print(f"\n=== Ohne Lexikontreffer -> nicht automatisch entscheidbar ({len(unknown_rows)}) ===")
for r in unknown_rows[:30]:
    print(f"  {r['E-Mail']:48s} fn?={r['Vorname_neu']:14s} ln?={r['Nachname_neu']}")
print(f"  ... {len(unknown_rows)} insgesamt")

print("\n>>> FAZIT Automatisierbarkeit des Auto-Buckets:")
print(f"    sicher richtig herum : {len(ok_rows):4d}")
print(f"    sicher vertauscht    : {len(reversed_rows):4d}  (Regel muss drehen!)")
print(f"    Reihenfolge unklar   : {len(unknown_rows):4d}  (Domain-Konvention oder manuell)")
