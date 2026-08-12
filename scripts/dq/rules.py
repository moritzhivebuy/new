"""Entscheidungslogik der Bereinigungsroutine.

Reine Funktionen ohne Netzwerk und ohne Seiteneffekte, damit sie testbar sind
(siehe test_rules.py). Jede Funktion gibt neben dem Ergebnis eine Konfidenz
und eine Begruendung zurueck -- die Begruendung landet in `dq_befund`, damit
jeder automatische Schreibvorgang nachvollziehbar und umkehrbar ist.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .lexicon import (FEMALE, FREEMAIL, GIVEN, MALE, NATIONAL_TRUNK, PARTICLES,
                      ROLE_TOKENS, STRUCT_BLOCK, TITLES, TLD_COUNTRY)

# Konfidenzstufen. Nur HIGH wird automatisch geschrieben; MEDIUM und LOW
# landen auf dq_status=pruefen und warten auf einen Menschen.
HIGH, MEDIUM, LOW = "high", "medium", "low"

MIN_TOKEN = 3  # Mindestlaenge je Namensteil. Ohne das entsteht "El S".


# ---------------------------------------------------------------------------
# Helfer
# ---------------------------------------------------------------------------
def fold(s: str) -> str:
    """Diakritika entfernen und kleinschreiben, fuer Vergleiche."""
    if not s:
        return ""
    s = s.replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    s = s.replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def is_given(token: str) -> bool:
    """Ist das Token ein bekannter Vorname?

    Bei zusammengesetzten Namen muessen ALLE Teile Vornamen sein. Sonst
    gelten Doppel-Nachnamen als Vorname, sobald ein Teil zufaellig auch ein
    Vorname ist -- "Straib-Lorenz", "Rudolph-Beeh" und "Ahrens-Mueller"
    wuerden sonst Namensfelder faelschlich tauschen.
    """
    f = fold(token)
    if not f:
        return False
    if f in GIVEN:
        return True
    parts = [p for p in re.split(r"[-\s]+", f) if p]
    return len(parts) > 1 and all(p in GIVEN for p in parts)


def split_local(email: str) -> list[str]:
    """Local Part in Namenstokens zerlegen. Plus-Adressierung und
    angehaengte Ziffern fallen weg."""
    if not email or "@" not in email:
        return []
    local = email.split("@")[0].lower()
    local = re.sub(r"\+.*$", "", local)
    local = re.sub(r"\d+$", "", local)
    return [p for p in re.split(r"[._\-]+", local) if p]


def email_domain(email: str) -> str:
    return email.split("@")[-1].lower().strip() if email and "@" in email else ""


def proper_case(name: str) -> str:
    """Namen sauber kapitalisieren.

    Regeln:
      - Partikel innerhalb des Namens werden klein ("van der Bergh")
      - ein fuehrendes Partikel behaelt die Schreibweise der Eingabe
        ("van der Bergh" bleibt, "Von Muller" bleibt)
      - bewusst gemischte Schreibweisen bleiben unangetastet ("McDonald")
      - Bindestriche und Apostrophe werden in EINEM Durchlauf behandelt,
        damit sich die Teilschritte nicht gegenseitig ueberschreiben
    """
    if not name:
        return ""
    name = re.sub(r"\s+", " ", name.strip())
    out = []
    for i, word in enumerate(w for w in name.split(" ") if w):
        if fold(word) in PARTICLES:
            out.append(word.lower() if i > 0 else word)
            continue
        letters = [c for c in word if c.isalpha()]
        # Gemischte Schreibweise ist eine Aussage -- nicht zerstoeren.
        if letters and not all(c.isupper() for c in letters) \
                and not all(c.islower() for c in letters):
            out.append(word)
            continue
        out.append(re.sub(r"[^-'’]+",
                          lambda m: m.group(0)[:1].upper() + m.group(0)[1:].lower(),
                          word))
    return " ".join(out)


# ---------------------------------------------------------------------------
# Phase 02 -- Funktionspostfach erkennen
# ---------------------------------------------------------------------------
@dataclass
class MailboxVerdict:
    is_role: bool
    confidence: str
    reason: str


def classify_mailbox(email: str) -> MailboxVerdict:
    """Sammel-/Funktionspostfach oder echte Person?

    Muss vor jeder Namensableitung laufen, sonst entstehen Kontakte
    namens "Bestellung Reichelt".
    """
    if not email or "@" not in email:
        return MailboxVerdict(False, LOW, "keine E-Mail vorhanden")

    tokens = split_local(email)
    local_raw = email.split("@")[0].lower()

    hits = [t for t in tokens if t in ROLE_TOKENS]
    if hits:
        return MailboxVerdict(True, HIGH, f"Rollen-Token im Local Part: {', '.join(hits)}")

    core = re.sub(r"[._\-]", "", local_raw)
    if core in ROLE_TOKENS:
        return MailboxVerdict(True, HIGH, f"Local Part ist Rollenbegriff: {core}")

    struct = [t for t in tokens if t in STRUCT_BLOCK]
    if struct and len(tokens) <= 2:
        return MailboxVerdict(True, MEDIUM,
                              f"struktureller Marker statt Name: {', '.join(struct)}")

    # Firmenname als Postfach: "frasec-einkauf-und-infrastruktur@frasec.de"
    if len(tokens) >= 4:
        return MailboxVerdict(True, MEDIUM,
                              f"{len(tokens)} Tokens im Local Part, kein Personenmuster")

    # Kryptisch: keine Vokale oder Ziffern mitten im Kuerzel ("gcp6fe", "scdb")
    if len(tokens) == 1:
        t = tokens[0]
        if len(t) <= 5 and not is_given(t):
            if not re.search(r"[aeiouy]", t) or re.search(r"\d", local_raw):
                return MailboxVerdict(True, MEDIUM, f"kryptisches Kuerzel: {t}")

    return MailboxVerdict(False, HIGH, "kein Rollenmuster erkennbar")


# ---------------------------------------------------------------------------
# Domain-Konventionen -- gelernt aus den bereits sauberen Kontakten
# ---------------------------------------------------------------------------
@dataclass
class Convention:
    order: str          # "fn_first" | "ln_first"
    fn_first: int
    ln_first: int

    @property
    def support(self) -> int:
        return self.fn_first + self.ln_first

    @property
    def confidence(self) -> str:
        """Mehrheit muss klar sein, sonst ist die Domain gemischt."""
        if self.support < 2:
            return LOW
        win, lose = max(self.fn_first, self.ln_first), min(self.fn_first, self.ln_first)
        if lose == 0 and win >= 2:
            return HIGH
        if win >= 5 * max(lose, 1):
            return HIGH
        if win >= 2 * max(lose, 1):
            return MEDIUM
        return LOW


def learn_conventions(contacts: list[dict]) -> dict[str, Convention]:
    """Aus Kontakten mit vertrauenswuerdigem Namen lernen, ob eine Domain
    `vorname.nachname@` oder `nachname.vorname@` verwendet.

    Vertrauenswuerdig heisst: Vor- und Nachname gesetzt, beide im Local Part
    enthalten, und genau einer der beiden ist ein bekannter Vorname.
    """
    tally: dict[str, Convention] = {}
    for c in contacts:
        p = c.get("properties", c)
        fn, ln = (p.get("firstname") or "").strip(), (p.get("lastname") or "").strip()
        email = (p.get("email") or "").strip()
        dom = email_domain(email)
        if not (fn and ln and dom) or dom in FREEMAIL:
            continue
        ffn, fln = fold(fn), fold(ln)
        if len(ffn) < MIN_TOKEN or len(fln) < MIN_TOKEN:
            continue
        local = fold(email.split("@")[0])
        if ffn not in local or fln not in local:
            continue
        a, b = is_given(fn), is_given(ln)
        if a == b:
            continue  # beide oder keiner -> kein verlaessliches Signal
        conv = tally.setdefault(dom, Convention("fn_first", 0, 0))
        # Wo steht der tatsaechliche Vorname im Local Part?
        given_tok = ffn if a else fln
        other_tok = fln if a else ffn
        if local.find(given_tok) < local.find(other_tok):
            conv.fn_first += 1
        else:
            conv.ln_first += 1
    for conv in tally.values():
        conv.order = "fn_first" if conv.fn_first >= conv.ln_first else "ln_first"
    return tally


# ---------------------------------------------------------------------------
# Phase 03 -- Namen aus der E-Mail ableiten
# ---------------------------------------------------------------------------
@dataclass
class NameGuess:
    firstname: str = ""
    lastname: str = ""
    confidence: str = LOW
    reason: str = ""


def derive_name(email: str, conventions: dict[str, Convention] | None = None) -> NameGuess:
    """Vor- und Nachnamen aus dem Local Part ableiten.

    Bestimmt die Reihenfolge in dieser Prioritaet:
      1. Vornamen-Lexikon -- genau ein Token ist bekannter Vorname
      2. Domain-Konventionstabelle
      3. sonst: nicht schreiben (LOW), Kontakt auf pruefen setzen

    Nimmt NIE blind Token 1 als Vornamen -- das wuerde bei Domains wie
    securitas.de (nachname.vorname) den Fehler neu einbauen.
    """
    conventions = conventions or {}
    tokens = split_local(email)
    dom = email_domain(email)

    if not tokens:
        return NameGuess(reason="kein verwertbarer Local Part")

    if len(tokens) == 1:
        t = tokens[0]
        if len(t) >= 4 and t.isalpha() and not is_given(t):
            return NameGuess(lastname=proper_case(t), confidence=MEDIUM,
                             reason="ein Token, vermutlich Nachname -- Vorname fehlt")
        if is_given(t):
            return NameGuess(firstname=proper_case(t), confidence=MEDIUM,
                             reason="ein Token, bekannter Vorname -- Nachname fehlt")
        return NameGuess(reason=f"ein Token, nicht zuordenbar: {t}")

    first, last = tokens[0], tokens[-1]

    # Initial + Nachname: "a.witkowska", "m.priller-passreiter"
    if len(first) < MIN_TOKEN or len(last) < MIN_TOKEN:
        cand = [t for t in tokens if len(t) >= MIN_TOKEN and t.isalpha()]
        if cand:
            # Bei "m.priller-passreiter" ist der Nachname mehrteilig.
            surname = " ".join(cand) if len(cand) > 1 and len(first) < MIN_TOKEN else cand[-1]
            return NameGuess(lastname=proper_case(surname), confidence=MEDIUM,
                             reason="Initial statt Vorname -- nur Nachname ableitbar")
        return NameGuess(reason="Tokens zu kurz fuer eine Ableitung")

    if not (first.isalpha() and last.isalpha()):
        return NameGuess(reason="nicht-alphabetische Tokens")

    a, b = is_given(first), is_given(last)

    if a and not b:
        return NameGuess(proper_case(first), proper_case(last), HIGH,
                         f"'{first}' ist bekannter Vorname (Lexikon)")
    if b and not a:
        return NameGuess(proper_case(last), proper_case(first), HIGH,
                         f"'{last}' ist bekannter Vorname (Lexikon), Reihenfolge gedreht")

    conv = conventions.get(dom)
    if conv and conv.confidence in (HIGH, MEDIUM):
        why = (f"Domain-Konvention {dom} = {conv.order} "
               f"({conv.fn_first}:{conv.ln_first}, Konfidenz {conv.confidence})")
        if conv.order == "fn_first":
            return NameGuess(proper_case(first), proper_case(last), conv.confidence, why)
        return NameGuess(proper_case(last), proper_case(first), conv.confidence, why)

    hint = "beide Tokens sind Vornamen" if (a and b) else "kein Lexikontreffer"
    return NameGuess(reason=f"Reihenfolge unklar -- {hint}, keine Domain-Konvention fuer {dom}")


# ---------------------------------------------------------------------------
# Phase 04 -- Vor-/Nachname vertauscht
# ---------------------------------------------------------------------------
@dataclass
class SwapVerdict:
    swapped: bool = False
    confidence: str = LOW
    reason: str = ""
    signals: list[str] = field(default_factory=list)


def detect_swap(firstname: str, lastname: str, email: str, salutation: str = "",
                conventions: dict[str, Convention] | None = None) -> SwapVerdict:
    """Stehen Vor- und Nachname im falschen Feld?

    Wertet bis zu drei unabhaengige Signale aus: Vornamen-Lexikon,
    Reihenfolge im Local Part und die Anrede. Nur wenn kein Signal
    widerspricht und mindestens eines stark ist, wird HIGH gemeldet.
    """
    conventions = conventions or {}
    fn, ln = (firstname or "").strip(), (lastname or "").strip()
    if not (fn and ln):
        return SwapVerdict(reason="Vor- oder Nachname fehlt -- Phase 03 zustaendig")

    ffn, fln = fold(fn), fold(ln)
    if len(ffn) < MIN_TOKEN or len(fln) < MIN_TOKEN:
        return SwapVerdict(reason="Namensteil zu kurz fuer eine Beurteilung")
    if ffn == fln:
        return SwapVerdict(reason="Vor- und Nachname identisch")

    # Truemmerfelder nicht tauschen -- das verschlimmert sie nur.
    # Beispiel: firstname='Lena-', lastname='Kristin Deisler'
    for label, value in (("Vorname", fn), ("Nachname", ln)):
        if " " in value.strip() or value.strip().endswith(("-", ".", ",")) \
                or re.search(r"[0-9@|/\\]", value):
            return SwapVerdict(
                False, LOW,
                f"{label} {value!r} ist mehrteilig oder beschaedigt -- "
                f"erst Feld reparieren, dann tauschen")

    votes_swap, votes_ok, signals = 0, 0, []
    # Ein Swap braucht mindestens ein Signal ausserhalb des Lexikons.
    # Namen wie "Wolf", "Guenther" oder "Martin" sind Vor- UND Nachname --
    # das Lexikon allein kann sie nicht auseinanderhalten.
    corroborated = False

    # Signal 1: Vornamen-Lexikon
    a, b = is_given(fn), is_given(ln)
    if a and not b:
        votes_ok += 2
        signals.append(f"Lexikon: '{fn}' ist Vorname -> korrekt")
    elif b and not a:
        votes_swap += 2
        signals.append(f"Lexikon: '{ln}' ist Vorname -> vertauscht")

    # Signal 2: Reihenfolge im E-Mail-Local-Part.
    # Doppelnamen werden teilweise gematcht: "vera.ahrens@" belegt die
    # Reihenfolge auch dann, wenn im Feld "Ahrens-Mueller" steht.
    def _pos(name_folded: str) -> int:
        cands = [name_folded]
        cands += [p for p in re.split(r"[-\s]+", name_folded) if len(p) >= MIN_TOKEN]
        found = [local.find(c) for c in cands if c and local.find(c) >= 0]
        return min(found) if found else -1

    local = fold(email.split("@")[0]) if email and "@" in email else ""
    pos_fn, pos_ln = (_pos(ffn), _pos(fln)) if local else (-1, -1)
    if local and pos_fn >= 0 and pos_ln >= 0 and pos_fn != pos_ln:
        if pos_ln < pos_fn:
            dom = email_domain(email)
            conv = conventions.get(dom)
            if conv and conv.order == "ln_first" and conv.confidence in (HIGH, MEDIUM):
                signals.append(f"E-Mail: {dom} nutzt nachname.vorname -> kein Beweis")
            else:
                votes_swap += 1
                corroborated = True
                signals.append("E-Mail: Nachname steht vor Vorname -> vertauscht")
        else:
            votes_ok += 1
            signals.append("E-Mail: Vorname steht vor Nachname -> korrekt")
    elif local:
        # Signal 2b: Initial + Nachname ("amartin", "b.weigler", "alexander.p").
        # Welcher der beiden Namen passt auf das Initial, welcher auf den
        # ausgeschriebenen Teil? Das entscheidet die Reihenfolge unabhaengig
        # vom Lexikon -- und faengt genau die Faelle, in denen ein Nachname
        # zugleich ein gaengiger Vorname ist ("Martin", "Werner", "Peter").
        # Nur das Muster "Initial zuerst" wird ausgewertet:
        #   "b.weigler", "amartin" -> Vorname beginnt mit b/a, Nachname folgt
        #
        # Das umgekehrte Muster "full.initial" waere ambig und wird bewusst
        # ignoriert: "alexander.p" ist vorname.nachnameinitial, "gajic.r" ist
        # nachname.vornameinitial -- beide Konventionen kommen real vor.
        #
        # Bei Freemail-Adressen greift das Signal ebenfalls nicht: private
        # Postfaecher folgen keiner Firmenkonvention ("smadlen@hotmail.de").
        toks = [t for t in re.split(r"[._\-]+", local) if t]
        claim = None
        if len(toks) == 2 and len(toks[0]) == 1 and len(toks[1]) > 1:
            claim = (toks[0], toks[1])
        elif len(toks) == 1 and len(toks[0]) > 3:
            claim = (toks[0][0], toks[0][1:])

        if claim and email_domain(email) not in FREEMAIL:
            initial, full = claim
            as_is = ffn.startswith(initial) and fln == full
            as_swapped = fln.startswith(initial) and ffn == full
            # Nur ein Vote: schwaecheres Signal als zwei ausgeschriebene Namen.
            if as_is and not as_swapped:
                votes_ok += 1
                signals.append(f"E-Mail '{initial}'+'{full}' passt zur aktuellen "
                               f"Belegung -> korrekt")
            elif as_swapped and not as_is:
                votes_swap += 1
                corroborated = True
                signals.append(f"E-Mail '{initial}'+'{full}' passt nur gedreht "
                               f"-> vertauscht")

    # Signal 3: Anrede gegen Geschlecht des jeweiligen Vornamen-Kandidaten
    sal = fold(salutation)
    if sal in ("herr", "hr", "mr", "mr."):
        want, other = MALE, FEMALE
    elif sal in ("frau", "fr", "mrs", "mrs.", "ms", "ms.", "miss"):
        want, other = FEMALE, MALE
    else:
        want = other = None
    if want is not None:
        fn_fits = ffn in want and ffn not in other
        ln_fits = fln in want and fln not in other
        if ln_fits and not fn_fits:
            votes_swap += 1
            corroborated = True
            signals.append(f"Anrede '{salutation}' passt zu '{ln}', nicht zu '{fn}' -> vertauscht")
        elif fn_fits and not ln_fits:
            votes_ok += 1
            signals.append(f"Anrede '{salutation}' passt zu '{fn}' -> korrekt")

    if not signals:
        return SwapVerdict(reason="kein verwertbares Signal")

    if votes_swap and not votes_ok:
        if votes_swap >= 2 and corroborated:
            return SwapVerdict(True, HIGH,
                               f"{votes_swap} Signal(e) fuer Swap, keines dagegen", signals)
        why = ("nur das Lexikon spricht fuer einen Swap, E-Mail und Anrede "
               "bestaetigen nicht" if not corroborated else
               f"{votes_swap} Signal fuer Swap, zu schwach fuer automatisches Schreiben")
        return SwapVerdict(True, MEDIUM, why, signals)
    if votes_ok and not votes_swap:
        return SwapVerdict(False, HIGH if votes_ok >= 2 else MEDIUM,
                           "Felder korrekt belegt", signals)
    return SwapVerdict(False, LOW, f"Signale widerspruechlich ({votes_swap} vs. {votes_ok})", signals)


# ---------------------------------------------------------------------------
# Phase 05 -- Normalisieren
# ---------------------------------------------------------------------------
@dataclass
class FieldFix:
    value: str
    confidence: str
    reason: str


# Ein automatisch geschriebener Name darf nur aus Buchstaben, Leerzeichen,
# Bindestrich und Apostroph bestehen. Alles andere geht an einen Menschen.
_NAME_OK = re.compile(r"^[^\W\d_]+(?:[ \-'’][^\W\d_]+)*$", re.UNICODE)
_COMPANY = re.compile(r"(?:^|[\s.])(?:gmbh|mbh|ag|kg|ohg|ug|se|ek|ltd|inc|llc|plc|"
                      r"bv|nv|sarl|srl|spa|s\.a|co)(?:$|[\s.])|&", re.I)
_UNREADABLE = re.compile(r"[?�]")


def clean_name_field(value: str) -> FieldFix | None:
    """Namensfeld normalisieren -- oder zur manuellen Klaerung melden.

    Bewusst konservativ: automatisch geschrieben wird nur, wenn das Ergebnis
    ein sauberer Name ist. Beschaedigte Werte werden gemeldet, nicht geraten.
    Aus "B?Hmer" darf nicht "BHmer" werden, wenn die E-Mail "boehmer" sagt.
    """
    if not value:
        return None
    original, reasons = value, []
    v = re.sub(r"\s+", " ", value.strip())
    if v != value:
        reasons.append("Whitespace bereinigt")

    # -- Faelle, die nie automatisch angefasst werden --------------------
    if re.search(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}|https?://|www\.", v):
        return FieldFix(v, LOW, "E-Mail oder URL im Namensfeld -- manuell klaeren")
    if _UNREADABLE.search(v):
        return FieldFix(v, LOW, "unlesbares Zeichen (vermutlich Encoding-Schaden) "
                                "-- manuell klaeren, nicht entfernen")
    if "_" in v:
        return FieldFix(v, LOW, "Unterstrich im Namen -- vermutlich Dienst-/Systemkonto")
    if _COMPANY.search(v):
        return FieldFix(v, LOW, "Firmenname oder Rechtsform im Namensfeld -- manuell klaeren")
    letters = [c for c in v if c.isalpha()]
    if len(letters) <= 4 and v.isupper():
        return FieldFix(v, LOW, f"kurzes Kuerzel {v!r}, kein Personenname -- manuell klaeren")

    # -- Titel und akademische Zusaetze entfernen ------------------------
    toks = [t for t in v.replace(",", " ").split(" ") if t]
    kept = [t for t in toks if fold(t).rstrip(".") not in TITLES]
    if len(kept) != len(toks):
        removed = [t for t in toks if t not in kept]
        if not kept:
            return FieldFix(v, LOW, f"Feld enthaelt nur Titel/Anrede: {' '.join(removed)}")
        reasons.append(f"Titel entfernt: {' '.join(removed)}")
        v = " ".join(kept)

    # Satzzeichenreste am Rand ("Moreira," -> "Moreira"). Ein Punkt hinter
    # einem einzelnen Buchstaben ist ein Mittelinitial und bleibt stehen --
    # "Bogislav M." ist richtig geschrieben, "Bogislav M" waere schlechter.
    trimmed = v.rstrip(" ,;")
    if trimmed.endswith(".") and not re.search(r"(?:^|[\s\-])[^\W\d_]\.$", trimmed):
        trimmed = trimmed.rstrip(".").rstrip()
    trimmed = trimmed.lstrip(" ,;.")
    if trimmed != v:
        reasons.append("Satzzeichen am Rand entfernt")
        v = trimmed

    # -- Gross-/Kleinschreibung ------------------------------------------
    letters = [c for c in v if c.isalpha()]
    if len(letters) >= 3 and (all(c.isupper() for c in letters)
                              or all(c.islower() for c in letters)):
        cased = proper_case(v)
        if cased != v:
            reasons.append("Gross-/Kleinschreibung korrigiert")
            v = cased

    if not v or v == original:
        return None
    # Letzte Huerde: nur ein sauberer Name wird automatisch geschrieben.
    if not _NAME_OK.match(v):
        return FieldFix(v, LOW, f"Ergebnis {v!r} ist kein sauberer Name "
                                f"-- manuell klaeren")
    return FieldFix(v, HIGH, "; ".join(reasons))


SALUTATION_MAP = {
    "herr": "Herr", "hr": "Herr", "mr": "Herr", "mr.": "Herr", "monsieur": "Herr",
    "frau": "Frau", "fr": "Frau", "mrs": "Frau", "mrs.": "Frau", "ms": "Frau",
    "ms.": "Frau", "miss": "Frau", "madame": "Frau",
}


def clean_salutation(salutation: str, firstname: str = "") -> FieldFix | None:
    """Anrede auf Herr/Frau normalisieren und gegen den Vornamen pruefen."""
    if not salutation:
        return None
    target = SALUTATION_MAP.get(fold(salutation).rstrip("."))
    if target is None:
        return FieldFix(salutation, LOW, f"unbekannter Anredewert: {salutation!r}")

    ffn = fold(firstname).split(" ")[0] if firstname else ""
    if ffn:
        fem = ffn in FEMALE and ffn not in MALE
        male = ffn in MALE and ffn not in FEMALE
        if (target == "Herr" and fem) or (target == "Frau" and male):
            return FieldFix(salutation, LOW,
                            f"Anrede {target!r} widerspricht Vornamen {firstname!r} -- pruefen")
    if target == salutation:
        return None
    return FieldFix(target, HIGH, f"Anrede normalisiert: {salutation!r} -> {target!r}")


E164_MAX = 15          # ITU-Obergrenze inkl. Laendervorwahl
NATIONAL_SUSPECT = 12  # laenger -> vermutlich Durchwahl angehaengt

# Vorwahlen, die wir kennen, laengste zuerst (fuer Praefix-Erkennung).
_KNOWN_CC = sorted({code.lstrip("+") for code, _ in TLD_COUNTRY.values()},
                   key=len, reverse=True)


def _country_code(country_hint: str, email: str) -> tuple[str, str]:
    """Ländervorwahl aus Landesangabe oder E-Mail-TLD. -> (code, quelle)"""
    hint = (country_hint or "").strip().lower()
    if hint:
        for code, name in TLD_COUNTRY.values():
            if hint == name.lower():
                return code, "Landesangabe"
    if email and "@" in email:
        tld = email_domain(email).rsplit(".", 1)[-1]
        if tld in TLD_COUNTRY:
            return TLD_COUNTRY[tld][0], f"E-Mail-TLD .{tld}"
    return "", ""


def to_e164(raw: str, country_hint: str = "", email: str = "") -> FieldFix | None:
    """Telefonnummer auf E.164 bringen.

    Vorwahl in dieser Reihenfolge: vorhandenes '+' oder '00', Landeshinweis
    des Kontakts, TLD der E-Mail. Ohne belegbare Vorwahl wird nicht geraten.
    Ergebnisse jenseits von 15 Stellen oder mit verdaechtig langem nationalem
    Teil gehen zur Pruefung -- dort haengt fast immer eine Durchwahl dran,
    die sich nicht verlaesslich abtrennen laesst.
    """
    if not raw or not raw.strip():
        return None
    original = raw.strip()

    if re.search(r"[a-zA-Z]", original):
        return FieldFix(original, LOW, "Buchstaben in der Telefonnummer -- manuell klaeren")
    if _UNREADABLE.search(original):
        return FieldFix(original, LOW, "unlesbares Zeichen in der Nummer -- manuell klaeren")

    # Fuehrende Anfuehrungszeichen sind Tabellenkalkulations-Artefakte
    # ("'+49 73 11740") und wuerden die '+'-Erkennung aushebeln.
    work = original.lstrip("'\"`´ \t")
    # Die geklammerte Amtsnull "(0)" ist der optionale nationale Praefix und
    # entfaellt in E.164. Textuell entfernen, bevor die Ziffern gezogen werden.
    work = re.sub(r"\(\s*0\s*\)", "", work)
    digits = re.sub(r"\D", "", work)
    if not digits:
        return FieldFix(original, LOW, "keine Ziffern in der Telefonnummer")

    cc, src = _country_code(country_hint, email)
    cc_digits = cc.lstrip("+")

    if work.startswith("+") or digits.startswith("00"):
        body = digits[2:] if digits.startswith("00") and not work.startswith("+") else digits
        # Amtsnull direkt nach einer bekannten Vorwahl entfernen.
        for known in _KNOWN_CC:
            if body.startswith(known):
                rest = body[len(known):]
                if rest.startswith(NATIONAL_TRUNK):
                    rest = rest.lstrip(NATIONAL_TRUNK)
                body = known + rest
                break
        cand, why = "+" + body, f"E.164 formatiert: {original!r}"
    elif (cc_digits and digits.startswith(cc_digits)
          and not digits.startswith(NATIONAL_TRUNK)
          and len(digits) - len(cc_digits) >= 6):
        # Die Vorwahl steht schon da, nur ohne '+': "49 228 2870", "49308299981299".
        # Eine nationale Nummer ohne fuehrende Amtsnull ist kein gueltiges
        # Format -- beginnt sie mit der Landesvorwahl, ist sie genau das.
        cand = "+" + digits
        why = f"fehlendes '+' ergaenzt (Vorwahl {cc} war bereits enthalten): {original!r}"
    elif cc:
        national = digits.lstrip(NATIONAL_TRUNK) if digits.startswith(NATIONAL_TRUNK) else digits
        cand = f"{cc}{national}"
        why = f"E.164 ergaenzt aus {src}: {original!r}"
    else:
        return FieldFix(original, LOW, "keine Laendervorwahl ableitbar -- pruefen")

    nd = re.sub(r"\D", "", cand)
    if len(nd) < 8:
        return FieldFix(original, LOW, f"Nummer zu kurz nach Normalisierung: {cand}")
    if len(nd) > E164_MAX:
        return FieldFix(original, LOW,
                        f"{len(nd)} Stellen, ueber dem E.164-Maximum von {E164_MAX} "
                        f"-- vermutlich Durchwahl angehaengt, manuell klaeren")
    matched_cc = next((k for k in _KNOWN_CC if nd.startswith(k)), "")
    if matched_cc and len(nd) - len(matched_cc) > NATIONAL_SUSPECT:
        return FieldFix(cand, MEDIUM,
                        f"{why} -> {cand!r}; nationaler Teil ist "
                        f"{len(nd) - len(matched_cc)} Stellen lang -- Durchwahl pruefen")
    if cand == original:
        return None
    return FieldFix(cand, HIGH, f"{why} -> {cand!r}")


# ---------------------------------------------------------------------------
# Phase 06 -- Land, Sprache, Kanal
# ---------------------------------------------------------------------------
def derive_country_language(email: str, phone: str = "") -> tuple[FieldFix | None, FieldFix | None]:
    """Land und Sprache aus E-Mail-TLD bzw. Telefonvorwahl ableiten."""
    LANG = {"Germany": "de", "Austria": "de", "Switzerland": "de", "Liechtenstein": "de",
            "France": "fr", "Italy": "it", "Spain": "es", "Netherlands": "nl",
            "Belgium": "nl", "Portugal": "pt", "Denmark": "da", "Sweden": "sv",
            "Norway": "no", "Finland": "fi", "Poland": "pl", "Czechia": "cs",
            "United Kingdom": "en", "Ireland": "en", "Turkey": "tr", "Greece": "el",
            "Hungary": "hu", "Romania": "ro", "Croatia": "hr", "Slovenia": "sl",
            "Slovakia": "sk", "Bulgaria": "bg", "Luxembourg": "fr"}

    country = code = None
    dom = email_domain(email)
    if dom and dom not in FREEMAIL:
        tld = dom.rsplit(".", 1)[-1]
        if tld in TLD_COUNTRY:
            code, country = TLD_COUNTRY[tld]
            src = f"E-Mail-TLD .{tld}"
    if country is None and phone:
        d = re.sub(r"\D", "", phone)
        if phone.strip().startswith("+") or d.startswith("00"):
            d = d[2:] if d.startswith("00") else d
            for tld, (c, name) in sorted(TLD_COUNTRY.items(), key=lambda x: -len(x[1][0])):
                if d.startswith(c.lstrip("+")):
                    code, country, src = c, name, f"Telefonvorwahl {c}"
                    break
    if country is None:
        return None, None

    lang = LANG.get(country)
    cf = FieldFix(country, MEDIUM, f"Land abgeleitet aus {src}")
    lf = FieldFix(lang, MEDIUM, f"Sprache abgeleitet aus Land {country}") if lang else None
    return cf, lf


INBOUND_TRAFFIC = ("ORGANIC_SEARCH", "PAID_SEARCH", "DIRECT_TRAFFIC", "SOCIAL_MEDIA",
                   "PAID_SOCIAL", "REFERRALS", "EMAIL_MARKETING", "AI_REFERRALS",
                   "OTHER_CAMPAIGNS")


def derive_channel(record_source: str, analytics_source: str) -> FieldFix | None:
    """contact_typ__channel_ aus Datensatz- und Traffic-Quelle ableiten.

    Nur die eindeutigen Faelle bekommen HIGH: ein Listen-Import ist Outbound,
    ein Formular oder eine getrackte Web-Session ist Inbound.

    `OFFLINE` allein bedeutet lediglich "keine Web-Session bekannt" und sagt
    nichts ueber die Richtung -- das trifft auch auf per Integration
    angelegte Produkt-Kontakte zu. Solche Faelle gehen auf MEDIUM, damit die
    Zuordnung eine Geschaeftsentscheidung bleibt und nicht stillschweigend
    tausende Kontakte als Outbound markiert.
    """
    rs, a = (record_source or "").upper(), (analytics_source or "").upper()
    if rs == "IMPORT":
        return FieldFix("Outbound", HIGH, f"Datensatzquelle IMPORT -> Outbound")
    if rs == "FORM" or a in INBOUND_TRAFFIC:
        return FieldFix("Inbound", HIGH, f"Quelle {rs or '-'}/{a or '-'} -> Inbound")
    if rs == "CONVERSATIONS":
        return FieldFix("Inbound", MEDIUM,
                        "Chat/Inbox -- meist Inbound, aber auch Antwort auf Outreach moeglich")
    if a == "OFFLINE":
        return FieldFix("Outbound", MEDIUM,
                        f"Quelle {rs or '-'}/OFFLINE -- keine Web-Session bekannt, "
                        f"Richtung nicht belegt (Zuordnung fachlich entscheiden)")
    return None


# ---------------------------------------------------------------------------
# Phase 01 -- Geisterdatensatz
# ---------------------------------------------------------------------------
GHOST_FIELDS = ("firstname", "lastname", "email", "phone", "mobilephone", "company",
                "jobtitle", "website", "city", "zip", "country")


def is_ghost(props: dict) -> tuple[bool, str]:
    """Datensatz ohne jeden inhaltlichen Wert -- Loeschkandidat.

    Bewusst streng: sobald irgendein Feld gefuellt ist oder eine
    Verknuepfung existiert, ist es kein Geisterdatensatz.
    """
    filled = [f for f in GHOST_FIELDS if (props.get(f) or "").strip()]
    if filled:
        return False, f"Felder gefuellt: {', '.join(filled)}"
    for f in ("num_associated_deals", "hs_analytics_num_page_views",
              "num_notes", "num_contacted_notes"):
        try:
            if float(props.get(f) or 0) > 0:
                return False, f"Aktivitaet vorhanden ({f})"
        except (TypeError, ValueError):
            pass
    return True, "kein einziges inhaltliches Feld gefuellt, keine Aktivitaet"
