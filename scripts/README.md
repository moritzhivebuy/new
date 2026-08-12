# Audit-Skripte HubSpot Kontaktdaten

Auswertungsskripte zum Report [`../hubspot-kontaktdaten-audit.md`](../hubspot-kontaktdaten-audit.md).
Reines Lesen und Auswerten — **kein Skript schreibt nach HubSpot zurück.**

## Eingabeformat

Alle Skripte erwarten rohe JSON-Antworten der HubSpot CRM Search API
(`POST /crm/v3/objects/contacts/search`, bzw. `search_crm_objects` über den MCP-Server).
Erwartet wird ein Objekt mit `results[].id` und `results[].properties`.
Vorangestellter Text vor dem ersten `{` wird ignoriert, mehrere Seiten werden über
`id` dedupliziert.

Kein Python-Paket nötig, nur Standardbibliothek (getestet mit Python 3.11).

## Ablauf

### 1. Feldqualität der Stichprobe

Benötigte Properties: `firstname`, `lastname`, `email`, `phone`, `mobilephone`, `company`,
`jobtitle`, `salutation`, `country`, `city`, `zip`, `lifecyclestage`, `hs_analytics_source`,
`hs_object_source_label`, `createdate`, `hs_email_domain`, `hs_language`, `website`,
`hubspot_owner_id`, `hs_marketable_status`, `hs_email_bad_address`, `contact_typ__channel_`,
`hs_lead_status`

```bash
python3 01_feldqualitaet.py seite1.json seite2.json seite3.json
```

Liefert Befüllungsgrad je Feld, Namensfeld-Defekte (E-Mail/Telefon/URL im Namen,
Rollenbezeichnungen, ALLCAPS, Titel, Sonderzeichen), Telefon-Formatprüfung,
Dublettengruppen und eine Kreuztabelle Problemdichte × Datensatzquelle.

> Hinweis: `associatedcompanyid` wird von der Search-API nicht zuverlässig ausgeliefert.
> Der Befund „company-Text ohne Verknüpfung" aus diesem Skript ist ein **Artefakt** und
> muss über eine Cross-Object-Query (`SELECT COMPANY.name FROM CONTACT`) gegengeprüft werden.

### 2. Swap-Erkennung Vor-/Nachname

```bash
python3 02_swap_erkennung.py seite1.json seite2.json seite3.json
```

Klassifiziert jeden Kontakt mit Vorname + Nachname + E-Mail in *korrekt* /
*vertauscht* / *unklar*, über zwei unabhängige Signale:

1. **Vornamen-Lexikon** — genau ein Token ist ein bekannter Vorname
2. **Reihenfolge im E-Mail-Local-Part** — in der Referenzstichprobe zu ~97% verlässlich

Gibt zusätzlich die Kreuztabelle beider Signale aus (zur Validierung der Trefferquote),
Anrede-/Vorname-Widersprüche, inkonsistente Firmennamen je E-Mail-Domain und
Auffälligkeiten in `jobtitle`.

Das Lexikon in der Konstante `GIVEN` umfasst ~700 Vornamen und erklärt damit rund
zwei Drittel der Fälle. **Für den Produktivbetrieb auf ~2.000 Namen erweitern.**

### 3. Klassifikation namenloser Kontakte

Kontakte ohne Vornamen laden (`firstname` mit `NOT_HAS_PROPERTY` filtern),
Properties: `email`, `lastname`, `hs_object_source_label`, `lifecyclestage`, `company`

```bash
DQ_OUT=fix_namen_vorschlag.csv python3 03_namenlose_klassifikation.py seite*.json
```

Teilt die Kontakte in sechs Klassen:

| Klasse | Bedeutung |
|---|---|
| `A_auto_vorname_nachname` | `vorname.nachname@` — automatisch befüllbar |
| `B_initial_plus_nachname` | `v.nachname@` — nur Nachname ableitbar |
| `C_nur_nachname_vermutlich` | ein Token — wahrscheinlich Nachname, prüfen |
| `R_rollen_postfach` | Funktionspostfach — **kein Personenname** |
| `D_unklar_manuell` | manuell |
| `X_keine_email` | keine E-Mail vorhanden |

Schreibt eine Vorschlags-CSV (Zielpfad über `DQ_OUT`, Default `fix_namen_vorschlag.csv`)
mit `Record ID`, abgeleiteten Namen und empfohlener Aktion — als Grundlage für den
Dry-Run-Diff, **nicht** für einen direkten Import.

Die Rollen-Blocklist steht in `ROLE_TOKENS` und ist der wichtigste Stellhebel:
jeder Treffer dort verhindert einen erfundenen Personennamen.

### 4. Domain-Konventionen lernen

```bash
python3 04_domain_konventionen.py fix_namen_vorschlag.csv
```

Verarbeitet den `A_auto_vorname_nachname`-Block aus Schritt 3 und bestimmt je
E-Mail-Domain, ob `vorname.nachname@` oder `nachname.vorname@` gilt.

Das ist die Leitplanke gegen den gefährlichsten Fehler der ganzen Routine: eine naive
Regel „Token 1 = Vorname" baut bei Domains wie `securitas.de` (13:1 für
`nachname.vorname`) den Namens-Swap neu ein. Das Skript weist diese Fälle explizit aus.

## Bekannte Grenzen

- Die Reihenfolge ist ohne Lexikontreffer **nicht** maschinell entscheidbar (~36% der Fälle).
  Diese Kontakte gehören auf `dq_status = pruefen`, nicht in einen automatischen Schreibvorgang.
- Mindestlänge 3 Buchstaben je Token ist zwingend. Ohne sie entsteht aus
  `el-jazouli.s@…` der Name „El S" und aus `m.priller-passreiter@…` „M Passreiter".
- Nicht-Personen-Muster wie `www.tropfen5073@gmx.de`, `public.hgt@bechtle.com`,
  `berlin.grand@hyatt.com` oder `cgraf.ext@igus.net` passieren die reine Strukturprüfung
  und brauchen die Blocklist.
- Die Geschlechtsheuristik für den Anrede-Abgleich ist listenbasiert und bei
  international besetzten Vornamen unscharf. Widersprüche sind Prüfhinweise, keine Urteile.
