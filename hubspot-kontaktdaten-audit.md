# HubSpot Kontaktdaten-Audit & Bereinigungsroutine

**Portal:** 145132698 (Hivebuy) · **Stand:** 12.08.2026
**Stichprobe:** die letzten 500 Kontakte nach `createdate` (499 eindeutig, 05.08.–11.08.2026)
**Portal-Gesamtbestand:** 12.839 Kontakte

---

## 0. Kurzfassung

Dein Verdacht bestätigt sich, aber die Ursache liegt an zwei verschiedenen Stellen:

1. **Der Namens-Swap.** In der Stichprobe stehen bei **109 von 499 Kontakten (21,8%)** Vor- und Nachname in den falschen Feldern (`Vorname: Huber / Nachname: Robert` bei `robert.huber@heller.biz`). Diese Kontakte kommen fast alle aus **einem einzigen Listen-Import** vom 05.08.2026.
2. **Der Namens-Verlust (das von Dir beschriebene "nur E-Mail"-Problem).** Portalweit haben **760 Kontakte keinen Vornamen** und 789 keinen Nachnamen. Das betrifft nicht den Import, sondern die automatischen Kanäle: **EXTENSION 34,6%**, CONVERSATIONS 13,7%, INTEGRATION 6,9% — gegen **IMPORT nur 0,1%**.

Wichtig für die Bereinigung: Von den 760 namenlosen Kontakten sind **423 (55,7%) vollautomatisch aus der E-Mail befüllbar**, aber **52 sind Funktionspostfächer** (`bestellung@`, `eprocurement@`, `info@`), die *keinen* Personennamen bekommen dürfen — davon sind 18 bereits Kunden. Und: eine naive Ableitung "Token 1 = Vorname" würde bei 14 Kontakten den Fehler neu einbauen, weil manche Firmen `nachname.vorname@` verwenden.

**Die Reihenfolge der Bereinigung ist deshalb nicht beliebig:** erst Funktionspostfächer aussortieren, dann Namen ableiten, dann Swaps korrigieren.

---

## 1. Befund: Befüllungsgrad der Stichprobe (n=499)

| Feld | leer | Bewertung |
|---|---|---|
| `hs_language` | **100,0%** | tot — blockiert sprachrichtige Mailings |
| `contact_typ__channel_` | **100,0%** | Custom Property (Inbound/Outbound/ABM) existiert, wird nie gefüllt |
| `website` | 100,0% | unkritisch (Firmenobjekt trägt das) |
| `hubspot_owner_id` | **97,4%** | 486 Leads ohne Verantwortlichen |
| `country` | **98,0%** | blockiert Geo-Segmentierung |
| `zip` | 95,8% | unkritisch |
| `mobilephone` | 48,5% | akzeptabel |
| `phone` | 5,0% | gut |
| `salutation` | 5,0% | gut befüllt (Herr 331, Frau 140) |
| `jobtitle` | 3,6% | gut |
| `firstname` | 1,4% | gut *in dieser Stichprobe* (portalweit anders!) |
| `lastname` | 0,8% | gut *in dieser Stichprobe* |
| `email` | 0,2% | sehr gut |
| `company` | 0,6% | sehr gut |

**Quellenverteilung der Stichprobe:** IMPORT 471 · CONVERSATIONS 16 · INTEGRATION 6 · FORM 2 · EXTENSION 2 · CRM_UI 2

> ⚠️ **Einschränkung:** Weil 94% der letzten 500 aus einem Import stammen, ist diese Stichprobe **nicht repräsentativ für Deinen B2C-/Integrationszulauf**. Deshalb wurde die Namensfeld-Analyse zusätzlich portalweit gefahren (Abschnitt 3).

---

## 2. Befund: Feldprobleme in der Stichprobe

### 2.1 Vor- und Nachname vertauscht — 109 Kontakte (21,8%) 🔴

Das mit Abstand größte Problem. Beispiele:

| Record ID | Vorname (falsch) | Nachname (falsch) | E-Mail | Anrede |
|---|---|---|---|---|
| 838457636046 | Huber | Robert | robert.huber@heller.biz | Herr |
| 838457486542 | Mlynek | Madina | madina.mlynek@sprimag.de | Frau |
| 838428933323 | Schillings | Katharina | katharina.schillings@konecranes.com | Frau |
| 838453643488 | Beckmann | Andrea | andrea.beckmann@tedi.com | Frau |
| 838415920331 | STOCKER | Ursula | ursula.stocker@holcim.com | Frau |

**Wie belastbar ist die Erkennung?** Kreuzvalidierung aus Vornamen-Lexikon gegen E-Mail-Reihenfolge in der Stichprobe:

| Lexikon-Urteil | E-Mail = `vorname.nachname` | E-Mail = `nachname.vorname` |
|---|---|---|
| Felder korrekt | **155** | 5 |
| Felder vertauscht | 2 | **71** |

→ Die E-Mail-Reihenfolge ist ein zu **~97% verlässliches** Signal. Zusammen mit dem Lexikon sind 109 Fälle eindeutig. Weitere **101 Kontakte bleiben unentscheidbar** (kein Lexikontreffer), davon 34 mit `nachname.vorname`-Reihenfolge → sehr wahrscheinlich ebenfalls vertauscht.

**Hochrechnung:** Der Swap kam über einen Import. Bei 3.237 IMPORT-Kontakten im Portal ist von einem **vierstelligen Backlog** auszugehen. Das ist noch nicht vollständig gemessen — die Swap-Erkennung sollte über die gesamte Import-Kohorte laufen, nicht nur über die letzten 500.

### 2.2 Kaputte / leere Namensfelder — 7 Kontakte

| Record ID | Befund |
|---|---|
| 842329326804 | kein Name, nur `gtoskar@xometry.de` |
| 840865370329 | kein Name, nur `matthias.seiler@unite.eu` |
| 839995143400 | kein Name, nur `yusufalioezyilmaz@gmail.com` |
| 839935079621 | kein Name, nur `yannick.lueckert@pima.de` |
| 838453826808 | Vorname leer, Nachname = `exMA.L` |
| 838474794198 | Vorname leer, Nachname = `MeilchenPhilippe` (zusammengelaufen) |
| 838428734676 | Vorname leer, Nachname = `Einkauf`, E-Mail `thomas.zibusch@elk.at` |

### 2.3 Rollenbezeichnung statt Personenname — 4 Kontakte

`Operativ Einkauf` (E-Mail: `silke.fehrenbach@elma-ultrasonic.com` — die Person *ist* bekannt), `Einkauf`, `Demo Admin`.

### 2.4 Anrede — 4 direkte Widersprüche + Enum-Wildwuchs

| Record ID | Anrede | Vorname |
|---|---|---|
| 838475380975 | Herr | Martina |
| 838429480166 | Herr | Alexandra |
| 838475379913 | Frau | Daniel |
| 838428734680 | Frau | Michele |

Werteverteilung: `Herr` 331 · `Frau` 140 · leer 25 · **`Mr.` 2 · `Ms.` 1** → deutsch/englisch gemischt.

Nützlicher Nebeneffekt: Die Anrede ist ein **zweites, unabhängiges Signal** zur Swap-Erkennung, weil sie in 95% der Fälle gepflegt ist.

### 2.5 Formatierung der Namensfelder

- ALLCAPS: `FLEURY`, `STOCKER`, `WOHLGENANNT` (3)
- Kleinschreibung: `van` (1)
- Titel im Namensfeld: Vorname `Dr. Christof`, Nachname `Herr` (2)
- Zusammengelaufen: Nachname `IGLESIAS Kraume Isabell Ulrike` (1)

### 2.6 Telefonnummern nicht E.164 — 91 Felder 🟡

60× `phone` (12,0%) und 31× `mobilephone` (6,2%) ohne Ländervorwahl: `07452824147`, `0715630022153`, `066112313`. Bricht Click-to-Call und WhatsApp-/Dialer-Integrationen.

### 2.7 Firmenname inkonsistent bei identischer E-Mail-Domain — 4 Domains

| Domain | konkurrierende Schreibweisen |
|---|---|
| hartmann.info | `HARTMANN GROUP`, `Hartmann`, `Paul Hartmann` |
| koerber.com | `Körber`, `Körber Pharma` |
| tq-group.com | `TQ Group`, `TQ-Group` |
| gemue.de | `GEMÜ`, `Gemu Middle East Fzco` |

Außerdem Slogans im Firmenfeld: `EUROFUNK I Creating safety by technology.`

### 2.8 Dubletten — unauffällig ✅

**0** doppelte E-Mail-Adressen, **1** Namensdublette (`Daniel Fischer`, IDs 838456849600 / 838475379913). Die Dublettenprüfung ist gesund, hier ist kein Handlungsbedarf.

### 2.9 Nicht-Befund (Korrektur)

`associatedcompanyid` kam in der Search-API zu 100% leer zurück. Das ist ein **API-Artefakt** — die Firmenverknüpfungen existieren tatsächlich (per Cross-Object-Query gegengeprüft). Kein Problem.

---

## 3. Portalweiter Befund: die 760 namenlosen Kontakte

Das ist das von Dir beschriebene Muster. Es entsteht **nicht** im Import, sondern in den automatischen Kanälen:

| Datensatzquelle | Kontakte gesamt | ohne Vorname | Quote |
|---|---|---|---|
| **EXTENSION** | 407 | 141 | **34,6%** 🔴 |
| **CONVERSATIONS** | 665 | 91 | **13,7%** 🔴 |
| **INTEGRATION** | 7.341 | 505 | **6,9%** 🟡 |
| FORM | 700 | 4 | 0,6% ✅ |
| IMPORT | 3.237 | 4 | 0,1% ✅ |
| CRM_UI | 383 | 3 | 0,8% ✅ |

### Klassifikation nach Reparierbarkeit (n=759)

| Kategorie | Anzahl | Anteil | Behandlung |
|---|---|---|---|
| `vorname.nachname@` | **423** | 55,7% | vollautomatisch befüllbar |
| `v.nachname@` | 102 | 13,4% | Nachname automatisch, Vorname anreichern |
| ein Token | 94 | 12,4% | wahrscheinlich Nachname, prüfen |
| **Funktionspostfach** | **52** | 6,9% | **kein Personenname — taggen!** |
| unklar | 9 | 1,2% | manuell |
| keine E-Mail | 79 | 10,4% | davon **77 leere Geisterdatensätze** |

### 3.1 Die 52 Funktionspostfächer sind kein Müll

`bestellung@reichelt.de`, `eprocurement@bti.de`, `edi.support@igefa.de`, `info@eib-office.de`, `einkauf@ounda.de`, `adminscm@hmf-germany.com`, `hr.admin@unite.eu` …

Lifecycle-Verteilung: **customer 18** · lead 20 · other 8 · salesqualifiedlead 4 · opportunity 2

→ Kommerziell relevant. Sie brauchen nur eine *andere* Behandlung: als Funktionspostfach markieren, aus personalisierten Mailings ausschließen, Namensfelder bewusst leer lassen.

### 3.2 Die 77 Geisterdatensätze sind Müll

Kein Name, keine E-Mail, keine Firma, kein Telefon. Alle aus `INTEGRATION`, überwiegend November 2025, `hs_marketable_status = false`, `lifecyclestage = lead`. Beispiele: 566979040500, 567044315362, 566329261268. → Löschkandidaten.

### 3.3 ⚠️ Die kritische Falle: Domain-Konventionen

Eine naive Regel "Token 1 = Vorname" **baut neue Fehler ein**. Gemessen an den 423 automatisch befüllbaren Kontakten:

| | Anzahl |
|---|---|
| korrekt herum (Token 1 = Vorname) | 255 (60,3%) |
| **vertauscht (Token 1 = Nachname)** | **14 (3,3%)** |
| Reihenfolge nicht entscheidbar | 154 (36,4%) |

Die Konvention ist **firmenspezifisch**:

| Domain | `vorname.nachname` | `nachname.vorname` | Konvention |
|---|---|---|---|
| securitas.de | 1 | **13** | `nachname.vorname` |
| buefa.de | **73** | 1 | `vorname.nachname` |
| wuerth.com | 7 | 0 | `vorname.nachname` |
| lgi.de | 5 | 0 | `vorname.nachname` |
| hypovbg.at | 4 | 0 | `vorname.nachname` |

Und es rutschen Nicht-Personen durch die Musterprüfung: `www.tropfen5073@gmx.de`, `public.hgt@bechtle.com`, `ebc.hgt@bechtle.com`, `berlin.grand@hyatt.com`, `cgraf.ext@igus.net`.

**Konsequenz:** Die Reihenfolge muss pro Domain aus den *bereits korrekten* Kontakten gelernt werden. Diese Domain-Konventionstabelle ist das zentrale Asset der ganzen Routine — sie entsteht aus Deinen eigenen sauberen Daten.

---

## 4. Die Bereinigungsroutine

### Phase 0 — Grundlage schaffen (einmalig)

**Schritt 1: Properties für Nachvollziehbarkeit anlegen.** Kein automatischer Schreibvorgang ohne Spur.

| Property | Typ | Zweck |
|---|---|---|
| `dq_status` | Enum: `ok`, `auto_bereinigt`, `pruefen`, `funktionspostfach`, `unbrauchbar` | Steuert Listen & Dashboard |
| `kontakt_typ` | Enum: `Person`, `Funktionspostfach` | Trennt Personen von Sammelpostfächern |
| `name_quelle` | Enum: `manuell`, `aus_email_abgeleitet`, `enrichment` | Verhindert, dass abgeleitete Namen später als bestätigt gelten |
| `dq_befund` | Text (mehrzeilig) | Welche Regel griff + **alte Werte** → Rollback möglich |
| `dq_letzte_pruefung` | Datum | Wiederholbarkeit |

**Schritt 2: Domain-Konventionstabelle bauen.** Für jede E-Mail-Domain aus allen Kontakten mit vertrauenswürdigem Vor-/Nachnamen auszählen, ob der Local Part `vorname.nachname` oder `nachname.vorname` ist. Ergebnis: Lookup `Domain → Konvention (+ Konfidenz)`. Bei gemischten Domains (buefa.de 73:1, securitas.de 1:13) gilt die Mehrheit, Ausreißer gehen auf `pruefen`.

**Schritt 3: Vornamen-Lexikon aufbauen** (~2.000 Vornamen DE/AT/CH + international). Mein Testlauf mit ~700 Namen ergab 36% ohne Treffer; ein größeres Lexikon plus Domain-Tabelle schließt die Lücke weitgehend.

### Phase 1 — Müll entfernen (risikolos)

**Schritt 4:** Die 77 leeren Geisterdatensätze exportieren, auf Verknüpfungen (Deals/Tickets/Aktivitäten) prüfen, dann löschen.

### Phase 2 — Funktionspostfächer trennen (**vor** jeder Namenslogik)

**Schritt 5:** Local Part gegen Rollen-Blocklist prüfen — `info`, `kontakt`, `bestellung`, `einkauf`, `eprocure(ment)`, `edi`, `support`, `service`, `buchhaltung`, `rechnung`, `accounting`, `hr`, `jobs`, `admin`, `noreply`, `zentrale`, `scm`, `logistik` … — plus Strukturmuster (`www.`, `public.`, `.ext`, kryptische Kürzel wie `gcp6fe`).

→ `kontakt_typ = Funktionspostfach`, `dq_status = funktionspostfach`, Namensfelder **leer lassen**, aus personalisierten Mailings ausschließen, von der Namensableitung ausnehmen. **52 Kontakte.**

Dieser Schritt muss zuerst laufen, sonst erzeugt Phase 3 Kontakte namens "Bestellung Reichelt".

### Phase 3 — Namen aus E-Mail ableiten (das Volumengeschäft)

**Schritt 6:** Nur für `kontakt_typ = Person` **und** Vorname leer:

1. Local Part normalisieren: `+suffix` und Endziffern entfernen, an `.` `_` `-` splitten
2. Härteprüfung: ≥2 Tokens, erstes **und** letztes Token je ≥3 Buchstaben, rein alphabetisch
   *(Diese Prüfung ist nötig — ohne sie wird aus `el-jazouli.s@kasselwasser.de` "El S" und aus `m.priller-passreiter@hamberger.de` "M Passreiter".)*
3. Reihenfolge bestimmen, in dieser Priorität:
   a) Vornamen-Lexikon — genau ein Token ist bekannter Vorname → das ist der Vorname
   b) Domain-Konventionstabelle
   c) sonst **nicht schreiben** → `dq_status = pruefen`
4. Korrekt kapitalisieren (Bindestrich-Namen: `Priller-Passreiter`; Namenspartikel klein: `van`, `von`, `de`, `der`)
5. Schreiben + `name_quelle = aus_email_abgeleitet`, `dq_status = auto_bereinigt`

Erwartetes Ergebnis: ~409 der 423 korrekt, 14 brauchen die Reihenfolgedrehung, der Rest fällt sauber auf `pruefen`.

**Schritt 7:** `v.nachname@` (102) und Ein-Token-Fälle (94): nur Nachnamen schreiben, `dq_status = pruefen`, in Enrichment-Queue (Breeze Intelligence / Clearbit) oder für den AE beim nächsten Kontakt.

### Phase 4 — Vertauschte Namen korrigieren (der 22%-Block)

**Schritt 8: Erkennung** je Kontakt mit Vorname **und** Nachname **und** E-Mail:

1. Normalisieren (Diakritika strippen, kleinschreiben), beide Tokens gegen Local Part matchen
2. Ist Nachname ein bekannter Vorname und Vorname nicht → **Swap**
3. Kein Lexikontreffer → E-Mail-Reihenfolge (97% verlässlich), aber bei unbekannter oder gemischter Domain-Konvention auf `pruefen` statt automatisch schreiben
4. **Gegenprüfung über die Anrede:** `Herr`/`Frau` + geschlechtstypischer Vorname bestätigt oder widerlegt den Swap unabhängig von der E-Mail

**Schritt 9: Schreiben** — Felder tauschen, alte Werte in `dq_befund` protokollieren, `dq_status = auto_bereinigt`.

Umfang: 109 bestätigte Swaps allein in den letzten 500. **Die Erkennung über die gesamte Import-Kohorte (3.237 Kontakte) laufen lassen** — dort liegt der eigentliche Backlog.

### Phase 5 — Normalisieren

**Schritt 10 — Namen:** Whitespace trimmen, Doppelblanks kollabieren, ALLCAPS/Kleinschreibung → Proper Case (Ausnahmeliste für Partikel), Titel (`Dr.`, `Prof.`, `Dipl.-Ing.`) aus dem Vornamen in eine eigene Property `titel` ziehen, Ziffern und Sonderzeichen entfernen.

**Schritt 11 — Anrede:** Enum auf `Herr`/`Frau` normalisieren (`Mr.`→`Herr`, `Ms.`/`Mrs.`→`Frau`), gegen Vornamen abgleichen, Widersprüche auf `pruefen`.

**Schritt 12 — Telefon → E.164:** Ländervorwahl in dieser Reihenfolge ableiten: vorhandenes `+` → `country` des Kontakts → Land der verknüpften Firma → TLD der E-Mail (`.de`→+49, `.at`→+43, `.ch`→+41). Leerzeichen, Schrägstriche, Klammern entfernen. **91 Felder** in der Stichprobe. Als dauerhafte Regel, nicht als Einmalaktion.

**Schritt 13 — Firmenname:** Pro E-Mail-Domain eine kanonische Schreibweise festlegen (Mehrheit + manuelle Klärung der 4 Konfliktdomains). Der Name des **verknüpften Firmenobjekts** ist der Master; das kontaktseitige Textfeld `company` als abgeleitet behandeln, nicht als Eingabefeld.

### Phase 6 — Segmentierungslücken schließen

**Schritt 14:** `country` (98% leer) und `hs_language` (100% leer) aus E-Mail-TLD + Telefonvorwahl + Firmenland ableiten. Ohne `hs_language` versendet HubSpot keine sprachrichtigen Mails.

**Schritt 15:** `contact_typ__channel_` (Inbound/Outbound/ABM, 100% leer) rückwirkend füllen: `IMPORT` + `OFFLINE` → Outbound, `FORM`/`ORGANIC_SEARCH` → Inbound. Die Property existiert für Dein Reporting und liegt komplett brach.

**Schritt 16:** `hubspot_owner_id` — 486 der 499 Kontakte ohne Verantwortlichen. Kein Hygieneproblem im engeren Sinn, aber 97% unbetreute Leads. Über Routing-Regeln zuweisen.

### Phase 7 — An der Quelle abstellen ⭐

**Schritt 17.** Ohne diesen Schritt ist der ganze Rest eine Einmalaktion, die sich in drei Monaten wiederholt.

| Quelle | Problem | Fix |
|---|---|---|
| **EXTENSION** (34,6% namenlos) | Connector überträgt Namen nicht | Feldmapping korrigieren |
| **CONVERSATIONS** (13,7%) | Chat/Inbox erzeugt Kontakt aus Absenderadresse | Ableitungslogik als HubSpot-Workflow bei Kontakterstellung, nicht als Batch |
| **INTEGRATION** (6,9%, 505 absolut) | größter Absolutbeitrag + die 77 Geisterdatensätze | Feldmapping prüfen, Erzeugung leerer Records abstellen |
| **IMPORT** | 22% Swap-Rate über eine einzige Datei | **Pre-Flight-Check auf der CSV vor dem Upload** — Swap- und Rollenpostfach-Erkennung auf der Datei laufen lassen. Eine Stunde Arbeit vorher gegen tausende Records Reparatur nachher. |
| **FORM** | bereits sauber (0,6%) | Vor-/Nachname als Pflichtfeld belassen |

**Schritt 18: Als Regelbetrieb verankern.**
- Skript täglich oder wöchentlich laufen lassen
- Aktive Liste **„Datenqualität: prüfen"** auf `dq_status = pruefen` — die Fälle, die Menschen entscheiden müssen
- Dashboard auf `dq_status` und `kontakt_typ`, damit Regressionen sichtbar werden

---

## 5. Umsetzungsvarianten

| Variante | Vorteil | Nachteil |
|---|---|---|
| **(a) HubSpot-native** — Workflows + Custom Coded Actions bei Kontakterstellung | keine externe Infrastruktur, wirkt in Echtzeit | Domain-Konventionstabelle und Lexikon in HubSpot schlecht pflegbar |
| **(b) Externes Skript** gegen die CRM-API (Python/Node), geplant | volle Kontrolle, Dry-Run testbar, hält Lexikon + Domain-Tabelle, Batch-Update | eigener Betrieb nötig |
| **(c) Operations Hub Datenqualität + Enrichment** | wenig Eigenbau | Kosten, greift nicht bei Swaps und Funktionspostfächern |

**Empfehlung: (b) für den Backlog + (a) für den Zulauf.** Das Skript arbeitet die 760 namenlosen und die vierstellige Swap-Kohorte einmal ab; die Workflows verhindern, dass es zurückkommt.

---

## 6. Leitplanken

Aus den Fehlern, die in dieser Analyse selbst aufgetreten sind:

1. **Immer erst Dry-Run**, Diff als CSV exportieren, freigeben lassen. Nie blind schreiben.
2. **Nie einen Personennamen für ein Funktionspostfach** ableiten.
3. **Nie Token 1 als Vornamen** ohne Reihenfolgeprüfung — hätte 14 neue Fehler erzeugt.
4. **Alte Werte protokollieren** (`dq_befund`), damit jeder automatische Schreibvorgang umkehrbar ist.
5. **Manuelle Pflege respektieren:** Kontakte mit `name_quelle = manuell` nicht überschreiben.
6. **Kunden aus destruktiven Schritten ausnehmen** (18 der Funktionspostfächer sind Kunden) — dort nur markieren, nicht löschen.
7. **Mindestlängen erzwingen** (≥3 Buchstaben je Token), sonst entstehen Namen wie „El S".

---

## 7. Priorisierung

| # | Maßnahme | Umfang | Aufwand | Wirkung |
|---|---|---|---|---|
| 1 | Pre-Flight-Check für Imports (Phase 7) | alle künftigen Imports | S | 🔴 sehr hoch |
| 2 | Funktionspostfächer taggen (Phase 2) | 52 | S | 🔴 hoch — schützt Phase 3 |
| 3 | Namen aus E-Mail ableiten (Phase 3) | 423 automatisch | M | 🔴 hoch |
| 4 | Swap-Korrektur Import-Kohorte (Phase 4) | ~1.000+ geschätzt | M | 🔴 hoch |
| 5 | Feldmapping EXTENSION/CONVERSATIONS (Phase 7) | laufend | M | 🔴 hoch |
| 6 | 77 Geisterdatensätze löschen (Phase 1) | 77 | S | 🟡 mittel |
| 7 | Telefon E.164 (Phase 5) | 91 Felder | S | 🟡 mittel |
| 8 | `hs_language` + `country` füllen (Phase 6) | ~490 | S | 🟡 mittel |
| 9 | `contact_typ__channel_` rückfüllen (Phase 6) | 499 | S | 🟡 mittel |
| 10 | Anrede normalisieren (Phase 5) | 7 | S | 🟢 niedrig |
| 11 | Firmennamen kanonisieren (Phase 5) | 4 Domains | S | 🟢 niedrig |

---

## 8. Nächster Schritt

Es wurde **nichts in HubSpot geschrieben** — diese Analyse ist rein lesend. Für die Umsetzung brauche ich von Dir eine Entscheidung zu:

1. **Umsetzungsvariante** (Empfehlung: b + a)
2. **Freigabe für Phase 1** (77 Geisterdatensätze löschen) — irreversibel
3. **Ob die Swap-Erkennung** über die gesamte Import-Kohorte laufen soll (3.237 Kontakte), um den echten Backlog zu messen

Danach ist der sinnvolle erste Lauf: Phase 0–3 als Dry-Run mit CSV-Diff zur Freigabe.

---

## Anhang: Reproduzierbarkeit

Die Auswertungsskripte liegen unter `scripts/`:

| Skript | Zweck |
|---|---|
| `01_feldqualitaet.py` | Befüllungsgrad, Namensfeld-Defekte, Telefon, Dubletten, Quellen-Kreuztabelle |
| `02_swap_erkennung.py` | Vor-/Nachname-Swap via Vornamen-Lexikon + E-Mail-Reihenfolge, Anrede-Abgleich |
| `03_namenlose_klassifikation.py` | Klassifikation der namenlosen Kontakte nach Reparierbarkeit, erzeugt Vorschlags-CSV |
| `04_domain_konventionen.py` | Lernt `vorname.nachname` vs. `nachname.vorname` je Domain |

Eingabe sind JSON-Antworten der HubSpot Search-API (`objectType=CONTACT`). Die Skripte schreiben nicht zurück.
