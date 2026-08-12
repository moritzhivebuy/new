"""Tests der Entscheidungslogik gegen die echten Faelle aus dem Audit.

Aufruf:  python3 -m scripts.dq.test_rules
Kein Netzwerk, keine Abhaengigkeiten. Exit-Code 1 bei Fehlern.
"""
from __future__ import annotations

from .rules import (HIGH, LOW, MEDIUM, Convention, classify_mailbox, clean_name_field,
                    is_given,
                    clean_salutation, derive_channel, derive_country_language, derive_name,
                    detect_swap, is_ghost, learn_conventions, proper_case, to_e164)

_fails: list[str] = []
_count = 0


def check(label: str, got, want):
    global _count
    _count += 1
    if got != want:
        _fails.append(f"{label}\n      erwartet: {want!r}\n      erhalten: {got!r}")


# ===========================================================================
# Phase 02 -- Funktionspostfaecher (echte Adressen aus dem Portal)
# ===========================================================================
for addr in ["bestellung@reichelt.de", "eprocurement@bti.de", "edi.support@igefa.de",
             "info@eib-office.de", "einkauf@ounda.de", "adminscm@hmf-germany.com",
             "hr.admin@unite.eu", "eprocure@jh-profishop.de", "kontakt@websmile.media",
             "bestellung@der-textilmakler.de", "einkauf@airbusbank.com",
             "accounting-rebuy-recommerce-gmbh@rebuy.com",
             "frasec-einkauf-und-infrastruktur@frasec.de", "www.tropfen5073@gmx.de",
             "public.hgt@bechtle.com", "cgraf.ext@igus.net", "scdb@dvhmedien.com"]:
    check(f"Rollenpostfach erkannt: {addr}", classify_mailbox(addr).is_role, True)

# Echte Personen duerfen NICHT als Rollenpostfach durchgehen.
for addr in ["kristin.schmelzer@neinstedt.de", "hardy.kuebler@hypovbg.at",
             "matthias.seiler@unite.eu", "a.witkowska@rebuy.com", "kieslich@wera.de",
             "ringo.lischke@ipb-halle.de", "yannick.lueckert@pima.de",
             "ghalia.saidavilindberg@academedia.se", "m.priller-passreiter@hamberger.de"]:
    check(f"Person nicht als Rolle geflaggt: {addr}", classify_mailbox(addr).is_role, False)


# ===========================================================================
# Phase 03 -- Namensableitung
# ===========================================================================
g = derive_name("kristin.schmelzer@neinstedt.de")
check("derive vorname.nachname -> Vorname", g.firstname, "Kristin")
check("derive vorname.nachname -> Nachname", g.lastname, "Schmelzer")
check("derive vorname.nachname -> Konfidenz", g.confidence, HIGH)

# Reihenfolge per Lexikon gedreht (securitas.de nutzt nachname.vorname).
g = derive_name("bach.alexander@securitas.de")
check("derive nachname.vorname -> Vorname", g.firstname, "Alexander")
check("derive nachname.vorname -> Nachname", g.lastname, "Bach")
check("derive nachname.vorname -> Konfidenz", g.confidence, HIGH)

g = derive_name("ehmann.sarah@securitas.de")
check("derive ehmann.sarah -> Vorname", g.firstname, "Sarah")
check("derive ehmann.sarah -> Nachname", g.lastname, "Ehmann")

# Das Lexikon kennt auch seltenere Vornamen und dreht die Reihenfolge.
g = derive_name("pappas.panagiotis@securitas.de")
check("seltener Vorname erkannt -> Vorname", g.firstname, "Panagiotis")
check("seltener Vorname erkannt -> Nachname", g.lastname, "Pappas")

# Beide Tokens ohne Lexikontreffer -> KEIN Schreiben ohne Domain-Konvention.
g = derive_name("fernandez.joseantonio@securitas.de")
check("derive ohne Lexikontreffer -> Konfidenz LOW", g.confidence, LOW)
check("derive ohne Lexikontreffer -> nichts geschrieben", (g.firstname, g.lastname), ("", ""))

# Mit gelernter Domain-Konvention wird derselbe Fall entscheidbar.
conv = {"securitas.de": Convention("ln_first", 1, 13)}
g = derive_name("fernandez.joseantonio@securitas.de", conv)
check("derive mit Konvention -> Vorname", g.firstname, "Joseantonio")
check("derive mit Konvention -> Nachname", g.lastname, "Fernandez")
check("derive mit Konvention -> Konfidenz", g.confidence, HIGH)

# Die Mindestlaenge verhindert "El S" und "M Passreiter".
g = derive_name("el-jazouli.s@kasselwasser.de")
check("el-jazouli.s -> kein Vorname erfunden", g.firstname, "")
check("el-jazouli.s -> Konfidenz nicht HIGH", g.confidence == HIGH, False)

g = derive_name("m.priller-passreiter@hamberger.de")
check("Initial+Doppelname -> kein Vorname", g.firstname, "")
check("Initial+Doppelname -> Nachname vollstaendig", g.lastname, "Priller Passreiter")
check("Initial+Doppelname -> Konfidenz MEDIUM", g.confidence, MEDIUM)

g = derive_name("a.witkowska@rebuy.com")
check("Initial+Nachname -> kein Vorname", g.firstname, "")
check("Initial+Nachname -> Nachname", g.lastname, "Witkowska")

g = derive_name("kieslich@wera.de")
check("nur Nachname -> Nachname", g.lastname, "Kieslich")
check("nur Nachname -> Konfidenz MEDIUM", g.confidence, MEDIUM)

g = derive_name("berlin.grand@hyatt.com")
check("beide Tokens unbekannt ohne Konvention -> LOW", g.confidence, LOW)
check("beide Tokens unbekannt -> nichts geschrieben", (g.firstname, g.lastname), ("", ""))


# ===========================================================================
# Konventionen lernen
# ===========================================================================
sample = [
    {"properties": {"firstname": "Sarah", "lastname": "Ehmann", "email": "ehmann.sarah@securitas.de"}},
    {"properties": {"firstname": "Alexander", "lastname": "Bach", "email": "bach.alexander@securitas.de"}},
    {"properties": {"firstname": "Tobias", "lastname": "Metz", "email": "metz.tobias@securitas.de"}},
    {"properties": {"firstname": "Kristin", "lastname": "Schmelzer", "email": "kristin.schmelzer@neinstedt.de"}},
    {"properties": {"firstname": "Karen", "lastname": "Serauky", "email": "karen.serauky@neinstedt.de"}},
    {"properties": {"firstname": "Nancy", "lastname": "Eichmann", "email": "nancy.eichmann@neinstedt.de"}},
]
learned = learn_conventions(sample)
check("Konvention securitas.de gelernt", learned["securitas.de"].order, "ln_first")
check("Konvention securitas.de Support", learned["securitas.de"].support, 3)
check("Konvention securitas.de Konfidenz", learned["securitas.de"].confidence, HIGH)
check("Konvention neinstedt.de gelernt", learned["neinstedt.de"].order, "fn_first")
# Freemail wird bewusst nicht gelernt.
check("Freemail nicht gelernt", "gmx.de" in learn_conventions(
    [{"properties": {"firstname": "Christian", "lastname": "Hessinger",
                     "email": "christian.hessinger@gmx.de"}}]), False)


# ===========================================================================
# Phase 04 -- Swap-Erkennung (echte Faelle aus der Stichprobe)
# ===========================================================================
SWAPPED = [
    ("Huber", "Robert", "robert.huber@heller.biz", "Herr"),
    ("Mlynek", "Madina", "madina.mlynek@sprimag.de", "Frau"),
    ("Schillings", "Katharina", "katharina.schillings@konecranes.com", "Frau"),
    ("Beckmann", "Andrea", "andrea.beckmann@tedi.com", "Frau"),
    ("STOCKER", "Ursula", "ursula.stocker@holcim.com", "Frau"),
    ("Killmaier", "Jochen", "jochen.killmaier@joline.de", "Herr"),
    ("Teufel", "Jan", "jan.teufel@zimmer-group.com", "Herr"),
    ("Hesse", "Ilka", "ilka.hesse@khs.com", "Frau"),
    ("Dzelili", "Ardit", "ardit.dzelili@3acomposites.com", "Herr"),
    ("Gruber", "Daniela", "daniela.gruber@gigasport.at", "Frau"),
]
for fn, ln, mail, sal in SWAPPED:
    v = detect_swap(fn, ln, mail, sal)
    check(f"Swap erkannt: {fn}/{ln}", v.swapped, True)
    check(f"Swap Konfidenz HIGH: {fn}/{ln}", v.confidence, HIGH)

# Korrekt belegte Felder duerfen NICHT getauscht werden -- auch dann nicht,
# wenn die E-Mail nachname.vorname verwendet.
CORRECT = [
    ("Oliver", "Brandt", "oliver.brandt@spitalfmi.ch", "Herr"),
    ("Stefan", "Uhlich", "uhlich.stefan@securitas.de", "Herr"),
    ("Daniela", "Knauth", "knauth.daniela@securitas.de", "Frau"),
    ("Tobias", "Berchner", "tobias.berchner@siegenia.com", "Herr"),
    ("Frederieke", "Bakenecker", "fbakenecker@teupen.com", "Frau"),
    ("Lisa-Maria", "Redl", "lisa-maria.redl@treves-group.com", "Frau"),
]
for fn, ln, mail, sal in CORRECT:
    v = detect_swap(fn, ln, mail, sal)
    check(f"kein Swap: {fn}/{ln}", v.swapped, False)

# Die Domain-Konvention entschaerft das E-Mail-Signal, das Lexikon bleibt fuehrend.
sec = {"securitas.de": Convention("ln_first", 1, 13)}
v = detect_swap("Stefan", "Uhlich", "uhlich.stefan@securitas.de", "Herr", sec)
check("securitas: korrekte Felder bleiben korrekt", v.swapped, False)
check("securitas: Konfidenz HIGH", v.confidence, HIGH)

# Fehlender Namensteil ist Sache von Phase 03, nicht Phase 04.
check("Swap ohne Nachnamen -> kein Urteil",
      detect_swap("Thomas", "", "thomas.zibusch@elk.at").swapped, False)

# --- Regressionen aus dem ersten Live-Dry-Run -------------------------------
# Nachname, der zugleich gaengiger Vorname ist. Das Initial in der E-Mail
# bestaetigt die AKTUELLE Belegung -- es darf nicht getauscht werden.
v = detect_swap("Annabelle", "Martin", "amartin@bihl-wiedemann.de", "Frau")
check("Initial+Nachname bestaetigt korrekte Belegung", v.swapped, False)
for fn, ln, mail in [("Sabine", "Werner", "swerner@example.de"),
                     ("Andrea", "Peter", "a.peter@example.de"),
                     ("Katrin", "Thomas", "k.thomas@example.de")]:
    check(f"kein Swap bei Nachname-als-Vorname: {fn} {ln}",
          detect_swap(fn, ln, mail).swapped, False)

# Umgekehrt: Initial passt auf den Nachnamen -> echter Swap, HIGH.
v = detect_swap("Weigler", "Benjamin", "b.weigler@kroschke.com", "Herr")
check("Initial+Nachname erkennt echten Swap", v.swapped, True)
check("Initial+Nachname Swap-Konfidenz", v.confidence, HIGH)
v = detect_swap("Pappas", "Alexander", "alexander.p@pro-beam.com", "Herr")
check("Swap ueber Lexikon trotz ambigem full.initial", v.swapped, True)

# "full.initial" ist ambig und darf allein nichts entscheiden:
# gajic.r = nachname.vornameinitial -> Radmila Gajic ist korrekt belegt.
v = detect_swap("Radmila", "Gajic", "gajic.r@eppendorf.de")
check("full.initial ohne Lexikontreffer -> kein Swap", v.swapped, False)

# Freemail folgt keiner Firmenkonvention -> Initial-Signal greift nicht.
v = detect_swap("Madlen", "Schneider", "smadlen@hotmail.de")
check("Freemail-Initial -> kein Swap", v.swapped, False)
check("Freemail-Initial -> kein Initial-Signal",
      any("passt" in s for s in v.signals), False)

# Doppelnachnamen: ein Teil im Local Part reicht, um die Reihenfolge zu belegen.
v = detect_swap("Ahrens-Mueller", "Vera", "vera.ahrens@buefa.de")
check("Doppelnachname teilgematcht -> Swap", v.swapped, True)
check("Doppelnachname teilgematcht -> HIGH", v.confidence, HIGH)

# Ein Doppelnachname, der einen Vornamen enthaelt, ist kein Vorname.
check("Straib-Lorenz ist kein Vorname", is_given("Straib-Lorenz"), False)
check("Rudolph-Beeh ist kein Vorname", is_given("Rudolph-Beeh"), False)
check("Ahrens-Mueller ist kein Vorname", is_given("Ahrens-Mueller"), False)
check("Ann-Sophie ist ein Vorname", is_given("Ann-Sophie"), True)
check("Kai-Uwe ist ein Vorname", is_given("Kai-Uwe"), True)
for fn, ln, mail in [("Julianna", "Straib-Lorenz", "julianna.straib@gmail.com"),
                     ("Gun", "Rudolph-Beeh", "gun.rudolph@derbusiness.com")]:
    check(f"kein Swap bei Doppelnachname: {fn} {ln}",
          detect_swap(fn, ln, mail).swapped, False)

# Ohne Signal ausserhalb des Lexikons wird nie automatisch getauscht.
v = detect_swap("Arnim", "Wolf", "wolf@mpia.de")
check("Lexikon allein -> nicht HIGH", v.confidence == HIGH, False)
v = detect_swap("Harries", "Günther", "info@paradies-optik.de")
check("Lexikon allein bei Rollenpostfach -> nicht HIGH", v.confidence == HIGH, False)

# Truemmerfelder werden nicht getauscht, sondern zur Reparatur gemeldet.
v = detect_swap("Lena-", "Kristin Deisler", "lena-kristin.deisler@stockmeier.com", "Frau")
check("mehrteiliges Feld -> kein Swap", v.swapped, False)
check("mehrteiliges Feld -> Konfidenz LOW", v.confidence, LOW)
check("mehrteiliges Feld -> Begruendung nennt Reparatur", "reparieren" in v.reason, True)
check("Feld mit Bindestrich am Ende -> kein Swap",
      detect_swap("Lena-", "Kristin", "x@y.de").swapped, False)
check("Feld mit Ziffer -> kein Swap",
      detect_swap("Meier2", "Thomas", "thomas.meier@y.de").swapped, False)


# ===========================================================================
# Phase 05 -- Normalisierung
# ===========================================================================
check("ALLCAPS korrigiert", clean_name_field("WOHLGENANNT").value, "Wohlgenannt")
check("ALLCAPS Konfidenz", clean_name_field("FLEURY").confidence, HIGH)
check("Titel entfernt", clean_name_field("Dr. Christof").value, "Christof")
check("Nur-Titel-Feld -> LOW", clean_name_field("Herr").confidence, LOW)
check("Whitespace bereinigt", clean_name_field("  Anja  Tschuor ").value, "Anja Tschuor")
check("saubere Werte unveraendert", clean_name_field("Oliver"), None)
check("Bindestrich-Name erhalten", clean_name_field("lisa-maria").value, "Lisa-Maria")
check("E-Mail im Namensfeld -> LOW", clean_name_field("a@b.de").confidence, LOW)
check("kaputtes Feld exMA.L unveraendert-oder-LOW",
      clean_name_field("exMA.L") is None or clean_name_field("exMA.L").confidence != HIGH, True)

# --- Regressionen aus dem Live-Dry-Run: Namensfelder -----------------------
# Encoding-Schaden nicht "reparieren", sondern melden.
check("Mojibake B?Hmer -> LOW", clean_name_field("B?Hmer").confidence, LOW)
check("Mojibake B?Hmer -> Wert unveraendert", clean_name_field("B?Hmer").value, "B?Hmer")
check("Mojibake Fabian?F -> LOW", clean_name_field("Fabian?F").confidence, LOW)
# Dienst-/Systemkonten
check("Unterstrich -> LOW", clean_name_field("Hivebuy_rw").confidence, LOW)
check("Unterstrich 2 -> LOW", clean_name_field("svc_Admin").confidence, LOW)
# Kuerzel sind keine Namen
check("Kuerzel DZR -> LOW", clean_name_field("DZR").confidence, LOW)
check("Kuerzel MMS -> LOW", clean_name_field("MMS").confidence, LOW)
check("langes ALLCAPS bleibt korrigierbar", clean_name_field("KOELBL").value, "Koelbl")
check("langes ALLCAPS -> HIGH", clean_name_field("KOELBL").confidence, HIGH)
# Firmennamen im Namensfeld
check("GmbH im Namensfeld -> LOW",
      clean_name_field("DAS Teppichwerk GmbH & Co. KG").confidence, LOW)
check("Ampersand -> LOW", clean_name_field("Meier & Sohn").confidence, LOW)
# Titelketten, die Reste hinterlassen, gehen an den Menschen
check("Titelkette mit Rest -> LOW",
      clean_name_field("Dr. Dipl. -Kfm. Tim Mundhenke, StB").confidence, LOW)
# Akademische Suffixe hinter Komma werden sauber entfernt
check("Phd-Suffix entfernt", clean_name_field("Moreira, Phd").value, "Moreira")
check("Phd-Suffix -> HIGH", clean_name_field("Moreira, Phd").confidence, HIGH)
check("MBA-Suffix entfernt", clean_name_field("Dobreva, MBA").value, "Dobreva")
check("Titel hinter Komma entfernt", clean_name_field("Andreas, Ing. Mag.").value, "Andreas")
check("Dr ohne Punkt entfernt", clean_name_field("Dr Michael").value, "Michael")

check("proper_case Partikel klein", proper_case("van der Bergh"), "van der Bergh")
check("proper_case fuehrendes Partikel gross", proper_case("Von Muller"), "Von Muller")
check("proper_case Doppelname", proper_case("PRILLER-PASSREITER"), "Priller-Passreiter")

check("Mr. -> Herr", clean_salutation("Mr.").value, "Herr")
check("Ms. -> Frau", clean_salutation("Ms.").value, "Frau")
check("Herr unveraendert", clean_salutation("Herr"), None)
check("Anrede-Widerspruch erkannt", clean_salutation("Herr", "Martina").confidence, LOW)
check("Anrede-Widerspruch erkannt 2", clean_salutation("Frau", "Daniel").confidence, LOW)
check("Anrede passend -> kein Fix", clean_salutation("Frau", "Ursula"), None)

# --- Regressionen aus dem Live-Dry-Run: Telefon ----------------------------
check("Amtsnull in Klammern entfernt",
      to_e164("+49 (0) 172 – 6 93 90 78").value, "+491726939078")
check("Amtsnull in Klammern entfernt 2",
      to_e164("+49 (0) 29 32 – 97 42 – 146").value, "+4929329742146")
check("Amtsnull ohne Klammern nach Vorwahl",
      to_e164("+49 0172 6939078").value, "+491726939078")
check("Vorwahl ohne Plus nicht verdoppelt",
      to_e164("49308299981299", "", "x@y.de").value, "+49308299981299")
check("Vorwahl ohne Plus 2",
      to_e164("49 201 1766-2000", "", "x@y.de").value, "+4920117662000")
check("Durchwahl -> nicht automatisch",
      to_e164("+49 711 656960-7101").confidence != HIGH, True)
check("ueber 15 Stellen -> LOW",
      to_e164("+49 2203 3691 127371").confidence, LOW)
check("Fragezeichen in Nummer -> LOW",
      to_e164("49 (0) 341 ? 230 66 70", "", "x@y.de").confidence, LOW)
check("bereits sauber und lang genug -> kein Fix", to_e164("+4915116412099"), None)

check("E.164 aus DE-TLD", to_e164("07452824147", "", "x@doll.eu") is not None, True)
check("E.164 aus Land", to_e164("07452824147", "Germany").value, "+497452824147")
check("E.164 fuehrende Null entfernt", to_e164("0715630022153", "Germany").value, "+49715630022153")
check("E.164 Leerzeichen entfernt", to_e164("+49 172 5794663").value, "+491725794663")
check("E.164 00-Praefix", to_e164("004915172716331").value, "+4915172716331")
check("E.164 bereits korrekt -> kein Fix", to_e164("+4927139311131"), None)
check("E.164 Buchstaben -> LOW", to_e164("0711 abc").confidence, LOW)
check("E.164 ohne Hinweis -> LOW", to_e164("07452824147").confidence, LOW)
check("E.164 leer -> None", to_e164(""), None)



# --- Regressionen aus dem zweiten Live-Dry-Run -----------------------------
# Vorwahl ohne '+' auch bei kurzen Nummern erkennen (war verdoppelt).
check("kurze Nummer mit CC ohne Plus",
      to_e164("49 228 2870", "", "x@y.de").value, "+492282870")
check("CC ohne Plus plus Klammer-Amtsnull",
      to_e164("49 (0) 7251 75-0", "", "x@y.de").value, "+497251750")
check("CC ohne Plus 3", to_e164("49(0)251 682-0", "", "x@y.de").value, "+492516820")
# Fuehrendes Tabellen-Apostroph darf die '+'-Erkennung nicht aushebeln.
check("Apostroph vor Plus", to_e164("'+49 73 11740", "", "x@y.de").value, "+497311740")
check("Anfuehrungszeichen vor Plus", to_e164('"+49 30 21210', "", "x@y.de").value, "+493021210")
# Echte Gebietsvorwahl, die wie eine doppelte Landesvorwahl aussieht.
check("+49 491 ist Leer, keine Verdoppelung", to_e164("+49 491 8080").value, "+494918080")
check("+41 41 ist Luzern, keine Verdoppelung", to_e164("+41 41 2298080").value, "+41412298080")

# Mittelinitial behaelt seinen Punkt.
check("Mittelinitial unveraendert", clean_name_field("Bogislav M."), None)
check("Mittelinitial mit Bindestrich unveraendert", clean_name_field("Maik-P."), None)
check("Komma-Rest wird trotzdem entfernt",
      clean_name_field("de Las Heras,").value, "de Las Heras")

# ===========================================================================
# Phase 06 -- Land, Sprache, Kanal
# ===========================================================================
c, l = derive_country_language("anja.tschuor@rosta.com", "+41628890455")
check("Land aus Telefonvorwahl", c.value, "Switzerland")
check("Sprache aus Land", l.value, "de")
c, l = derive_country_language("oliver.brandt@spitalfmi.ch")
check("Land aus TLD .ch", c.value, "Switzerland")
c, l = derive_country_language("gaetan.michel@tiwag.at")
check("Land aus TLD .at", c.value, "Austria")
c, l = derive_country_language("x@gmail.com")
check("Freemail ohne Telefon -> kein Land", c, None)

check("Kanal Outbound aus IMPORT", derive_channel("IMPORT", "OFFLINE").value, "Outbound")
check("Kanal Outbound aus IMPORT -> HIGH", derive_channel("IMPORT", "OFFLINE").confidence, HIGH)
check("Kanal Inbound aus FORM", derive_channel("FORM", "ORGANIC_SEARCH").value, "Inbound")
check("Kanal unbekannt -> None", derive_channel("CRM_UI", ""), None)
# OFFLINE allein belegt keine Richtung -> nicht automatisch schreiben.
check("INTEGRATION/OFFLINE -> nicht HIGH",
      derive_channel("INTEGRATION", "OFFLINE").confidence, MEDIUM)
check("EXTENSION/OFFLINE -> nicht HIGH",
      derive_channel("EXTENSION", "OFFLINE").confidence, MEDIUM)
check("CONVERSATIONS -> nicht HIGH", derive_channel("CONVERSATIONS", "").confidence, MEDIUM)


# ===========================================================================
# Phase 01 -- Geisterdatensaetze
# ===========================================================================
ok, why = is_ghost({"lifecyclestage": "lead", "hs_marketable_status": "false"})
check("Geisterdatensatz erkannt", ok, True)
ok, why = is_ghost({"email": "a@b.de"})
check("Kontakt mit E-Mail ist kein Geist", ok, False)
ok, why = is_ghost({"lastname": "Kremer"})
check("Kontakt mit Nachnamen ist kein Geist", ok, False)
ok, why = is_ghost({"num_associated_deals": "1"})
check("Kontakt mit Deal ist kein Geist", ok, False)


# ===========================================================================
print(f"\n{_count} Pruefungen ausgefuehrt, {len(_fails)} fehlgeschlagen.")
if _fails:
    print("\nFEHLER:")
    for f in _fails:
        print(f"  - {f}")
    raise SystemExit(1)
print("Alle Pruefungen bestanden.")
