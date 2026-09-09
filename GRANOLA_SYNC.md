# Granola-Notiz-Sync und Antwortvorschlag (HubSpot-Automatisierung)

Automatischer Flow: Wenn eine Granola-Meeting-Notiz an einem HubSpot-Kontakt hinterlegt wird,
(a) werden die Inhalte der Notiz in die gleichnamigen Kontakt-Properties übertragen,
(b) wird ein Lead angelegt bzw. der bestehende Lead in der Lead-Pipeline bewegt,
(c) wird eine Log-Notiz am Kontakt abgelegt, die alle Schritte nachvollziehbar dokumentiert,
(d) wird bei Erstgesprächen ein Antwortvorschlag als eigene Notiz am Kontakt hinterlegt und
(e) der Kontakt-Owner per Slack-DM darüber informiert.

Portal: 145132698 (Hivebuy)

## Getroffene Entscheidungen (Moritz)

| Frage | Entscheidung |
|---|---|
| "Lead Property" | HubSpot **Lead-Objekt** mit Lead-Pipeline (nicht hs_lead_status am Kontakt) |
| Bestehende Property-Werte | **Überschreiben**, Änderung wird im Log dokumentiert. Ausnahme: manuelle Einträge, die jünger als die Granola-Notiz sind (siehe Konfliktregel) |
| Technische Umsetzung | **Claude-Routine**, alle 30 Minuten, gebunden an die Session mit den HubSpot- und Slack-Verbindungen |
| QUALIFIZIERT: NEIN oder Zeile fehlt | Nur Daten übertragen + Log, **Statusänderung nur bei JA** |
| Datenpriorität | **Die Granola-Notiz hat immer die höchste Priorität**, sie enthält die aktuellsten Informationen |
| Erstgespräch-Erkennung | Meeting-Titel enthält **"Kennenlernen"** (bei Erstgesprächen immer der Fall) |
| Unterlagen in der Mail | Nicht einzeln auflisten, sondern über den **Along-Board-Link** teilen (Platzhalter im Vorschlag) |

## Erkennung einer Granola-Notiz

- Der Body enthält einen Link auf `notes.granola.ai`.
- Qualifizierung steht meist in der ersten Zeile bzw. im Fazit: `QUALIFIZIERT: JA` bzw. `QUALIFIZIERT: NEIN`.

**Wichtig, zwei Ablageformen:** Granola-Zusammenfassungen landen im Portal in **zwei** Objekttypen und
beide müssen durchsucht werden:

| Objekttyp | Body-Property | Bestand am 20.08.2026 |
|---|---|---|
| `notes` | `hs_note_body` | 356 |
| `meetings` | `hs_meeting_body` | 87 |

`calls` enthalten keine Granola-Inhalte. Die Meeting-Variante entsteht, wenn die Zusammenfassung über
"Meeting protokollieren" im CRM abgelegt wird, oft mit Titel-Präfix `[Granola]`. Sie war ursprünglich
nicht berücksichtigt, dadurch wurde Meeting 513289640152 (Josef Pichler, NAVAX, 20.08.2026) nicht
erfasst, obwohl es ein Erstgespräch mit `QUALIFIZIERT: JA` war. Seit dem 20.08.2026 sucht die Routine
in beiden Objekttypen.

**Wichtig, Suchsyntax:** Die Suche muss mit Wildcards arbeiten: `CONTAINS_TOKEN` mit dem Wert
`*notes.granola.ai*`. Ohne Wildcards (`granola`) findet HubSpot einen Teil der Einträge nicht. Das ist
beim Testlauf aufgefallen: die ungenaue Suche lieferte als "neueste" Notiz den 08.07., tatsächlich
existierten Notizen bis zum 17.08.

**Wichtig, Erstgespräch-Erkennung bei Meetings:** Bei der Meeting-Variante ist der Meeting-Titel
(`hs_meeting_title`) direkt am Objekt verfügbar, das Präfix `[Granola]` wird für die
"Kennenlernen"-Prüfung ignoriert.

## Auszuschließende Notizen

Gilt für beide Objekttypen (`notes` und `meetings`).

- Eigene Log-Notizen (enthalten `granola-sync:`) und eigene Antwortvorschläge (enthalten `granola-reply:`).
- Notizen ohne assoziierten Kontakt.
- Notizen am internen Sammelkontakt **Hivebuy GmbH (#365219269839)**: interne Meetings (Daily Checkin
  usw.), kein Kunde, kein Antwortvorschlag.
- Notizen, die das Wort "granola" enthalten, aber keinen `notes.granola.ai`-Link (z.B.
  "GRANOLA NICHT MITGESCHRIEBEN") sind keine Granola-Notizen.
- Fremde Automatisierungen nicht anfassen: Notizen von "Hivebuy Sales-Assistent, Mailvorschlag KW nn"
  (wöchentlicher Mailvorschlag) und "🤖 KI-Antwortvorschlag" (Support-Tickets) stammen aus anderen
  Automatisierungen.

## Property-Mapping

Die Abschnittsüberschriften der Notiz entsprechen den **Labels** der Kontakt-Properties (nicht den internen Namen). Bestätigte Zuordnungen:

| Überschrift in der Notiz | Kontakt-Property (intern) | Besonderheit |
|---|---|---|
| Pain Points + Beschreibung des Problems | `problem` | Beide Abschnitte werden zusammen übertragen (Konvention vom Beispielkontakt Gasser), getrennt durch `--` |
| Aktueller Einkaufsprozess (und Status Quo im Einkauf) | `situation` | Kompletter Abschnitt als Text |
| Umsetzung in Hivebuy (Pain Killer) | `rational_need` | Kompletter Abschnitt als Text |
| (BUDGET) Kosten und Angebot | `budget` | Einzeiliges Textfeld: kompakte Zusammenfassung (Betrag + wichtigste Konditionen), nicht der komplette Abschnitt |
| IT-Systeme | `erp_system_used` | Auswahlfeld! Erlaubte Werte: SAP, Navision, MS Business Central, DATEV, Coupa, Netsuite, Workday, d.velop, Other ERP, None. Mehrfachauswahl möglich (z.B. "MS Business Central;Navision"). Unbekannte ERPs auf "Other ERP", echten Namen ins Log |
| Next Steps | `next_step` | Einzeiliges Textfeld: kompakte Zusammenfassung, mit Semikolon getrennt |

Weitere Abschnitte werden nur übertragen, wenn ihre Überschrift exakt dem Label einer existierenden
Kontakt-Property entspricht (Prüfung zur Laufzeit über die Property-Definitionen). Keine erfundenen
Zuordnungen; nicht zuordenbare Abschnitte (z.B. Fazit, Vorstellung, Optimallösung, AUTHORITY, NEED,
TIME, COMMITMENT, Metriken, Fragestruktur, Für Along) werden im Log aufgelistet.

### Textbereinigung (Pflicht)

Granola-Notizen und Werte aus Fremdautomatisierungen enthalten Artefakte, die nicht in die Properties
gehören:

- **Markierungszahlen** aus Granola: Zeilen, die nur aus wiederholten Ziffern bestehen (`151515`,
  `666`, `333`, `999`). Entfernen.
- **Formel-Reste** wie `"• " +` am Anfang eines Wertes. Entfernen.
- **Rohes JSON** wie `{"Budget":" Kein Budget besprochen..."}`. Auf den reinen Text reduzieren.
- HTML-Entities (`&amp;`, `&lt;`) in Klartext auflösen.
- Bullet-Punkte als einzelne Zeilen mit `- ` schreiben, Abschnittsüberschrift als erste Zeile.

### Konfliktregel (wichtig)

Wurde eine Property **nach** dem Erstelldatum der Granola-Notiz manuell geändert und widerspricht der
neue Wert der Notiz, dann **bleibt der manuelle Wert stehen**. Der Widerspruch wird im Log und als
Prüfpunkt im Antwortvorschlag vermerkt. Begründung: Ein Mensch, der nach dem Meeting etwas einträgt,
hat den neueren Stand. Beispiel aus dem Testlauf: `next_step` stand auf "Robert meldet sich im
September" (manuell, 19.08.), die Notiz vom 17.08. nannte "Erinnerung für Q2 2027".

## Lead-Logik

- **Bestandskunden ohne Lead: kein Lead anlegen.** Steht der Kontakt auf Lifecycle-Stage
  `customer` oder auf Lead-Status `Existing Customer`, wird kein Lead erzeugt, auch wenn keiner
  vorhanden ist. Grund (Moritz, 25.08.2026): Bei Kunden hängt der Lead historisch nur an der
  einen Person, über die der Deal lief. Alle weiteren Kontakte kommen später dazu, oft über das
  Ticketsystem, und sind nur dem Unternehmen zugeordnet. Ein neuer Lead in "New" würde den
  Stand falsch darstellen. Die Begründung wird im Log vermerkt. Erster Fall: Karen Serauky,
  Evangelische Stiftung Neinstedt, 25.08.2026.
- **Ein Lead pro Firma, nicht pro Kontakt (Moritz, 26.08.2026).** Vor dem Anlegen wird geprüft, ob
  **irgendein** Kontakt der zugeordneten Firma schon einen Lead hat. Wenn ja, wird kein neuer Lead
  angelegt, auch wenn der Kontakt aus dem Granola-Eintrag selbst keinen hat. Im Log wird notiert,
  welcher Lead an welchem Kontakt schon existiert.

  Grund: An einem Gespräch nehmen oft zwei Personen derselben Firma teil, und eine davon hat schon
  einen Lead. Zwei Leads für eine Firma zerstören das Reporting. Anlass: Erstgespräch Techniropa am
  24.08.2026 mit Annika Roden (#850236019947) und Markus Peifer (#738609789126), beide an Firma
  #421812840670. Markus hatte bereits Lead 1304982667471, die Routine legte für Annika trotzdem
  einen zweiten an. Moritz hat den zweiten Lead am 26.08.2026 gelöscht.

  Nehmen mehrere Kontakte derselben Firma an einem Gespräch teil und existiert noch gar kein Lead,
  wird genau ein Lead angelegt, an dem Kontakt, dem der Granola-Eintrag zugeordnet ist.

  API: Firma über `GET /crm/v4/objects/contacts/{contactId}/associations/companies`, deren Kontakte
  über `GET /crm/v4/objects/companies/{companyId}/associations/contacts`, dann je Kontakt
  `GET /crm/v4/objects/0-1/{contactId}/associations/0-136`. Hat der Kontakt keine Firma, gilt nur
  die Prüfung am Kontakt selbst.
- **Neue Leads immer in "New" (Moritz, 26.08.2026).** Kein Lead an der Firma und kein Bestandskunde:
  Lead wird angelegt, mit dem Kontakt assoziiert und in die Anfangsphase "New" gesetzt. Auch bei
  `QUALIFIZIERT: JA`. Qualifizieren bleibt eine menschliche Entscheidung.
- **Bestehende Leads werden nie bewegt (Moritz, 26.08.2026).** Die Routine ändert `hs_pipeline_stage`
  an vorhandenen Leads nicht, unabhängig von der QUALIFIZIERT-Zeile. Der Stand wird nur im Log
  vermerkt.

  Grund: Am 24.08.2026 hat die Routine für Annika Roden (Techniropa, Kontakt #850236019947) den Lead
  1331712986304 direkt in "Qualified" angelegt, weil der Granola-Eintrag "QUALIFIZIERT: JA" nannte.
  Moritz am 26.08.2026: "Dies sollte so nicht passieren." Die alte Regel setzte die Phase aus der
  Granola-Zeile, das war eine automatische Qualifizierung ohne menschliche Prüfung. Der betroffene
  Lead bleibt auf Wunsch unverändert in "Qualified".
- Lead in Phase "Lost": wird ebenfalls nie verändert, das ist durch die Regel oben schon abgedeckt.

**Technischer Zugang:** Der HubSpot-MCP-Connector bietet das Lead-Objekt nicht an. Der Lead-Schritt läuft daher über die HubSpot-REST-API mit dem Private-App-Token aus der Umgebungsvariable `HUBSPOT_PRIVATE_APP_TOKEN` (per curl). Verifiziert am 16.07.2026 (Lesen, Schreiben und Pipeline-Abfrage funktionieren).

Lead-Pipeline (`lead-pipeline-id`), Objekt-Typ `0-136`:

| Phase (Label) | Stage-ID | Bedeutung |
|---|---|---|
| New | `new-stage-id` | Anfangsphase für neue Leads |
| Process | `attempting-stage-id` | In Bearbeitung |
| Later | `connected-stage-id` | Zurückgestellt |
| Qualified | `qualified-stage-id` | Ziel bei QUALIFIZIERT: JA |
| Lost | `unqualified-stage-id` | Disqualifiziert (wird von der Routine nicht gesetzt) |

API-Aufrufe:
- Leads eines Kontakts: `GET /crm/v4/objects/0-1/{contactId}/associations/0-136`
- Lead lesen: `GET /crm/v3/objects/0-136/{leadId}?properties=hs_lead_name,hs_pipeline,hs_pipeline_stage`
- Phase setzen: `PATCH /crm/v3/objects/0-136/{leadId}` mit `{"properties": {"hs_pipeline_stage": "<stage-id>"}}`
- Lead anlegen: `POST /crm/v3/objects/0-136` mit `{"properties": {"hs_lead_name": "<Vorname Nachname>", "hs_pipeline_stage": "<stage-id>"}, "associations": [{"to": {"id": <contactId>}, "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 578}]}]}` (578 = Lead zu Primary Contact)

## Antwortvorschlag (Teil d)

Wird erzeugt, wenn zur Granola-Notiz ein **Erstgespräch** gehört, erkennbar am Meeting-Titel mit
"Kennenlernen" (z.B. "Hivebuy: Kennenlernen & Kostensparen"). Der Meeting-Titel steht im Kopf der
Notiz und zusätzlich am Meeting-Objekt (`hs_meeting_title`).

**Datenbasis und Priorität:** Zuerst die Granola-Notiz (höchste Priorität, aktuellster Stand), danach
ergänzend die HubSpot-Daten: Kontakt-Properties, Firma, Deals, frühere Notizen, Calls, Meetings und
E-Mails. Widersprüche werden nicht stillschweigend geglättet, sondern als Prüfpunkt genannt.

**Aufbau der Notiz** (Vorbild: Notiz 512948669631 am Kontakt 838456679629), Stil angelehnt an den
bestehenden "Hivebuy Sales-Assistent":

- Kopf: `<strong>Hivebuy Sales-Assistent, Antwortvorschlag nach Erstgespräch</strong>` plus Marker
  `(granola-reply:<Notiz-ID>)` in Grau, danach Meeting-Titel, Datum und die Datenbasis.
- `<strong>Einschätzung:</strong>` Qualifizierung und Lage in zwei bis drei Sätzen.
- `<strong>Signal:</strong>` Der konkrete Anknüpfungspunkt aus dem Gespräch.
- `<strong>Kontext:</strong>` Rolle, Unternehmen, ERP, relevante Zahlen, HubSpot-Vorgeschichte.
- `<strong>Empfohlener Kanal:</strong>` Kanal, Empfänger, Absender und Zweck.
- `<strong>Betreff: ...</strong>` danach die fertige E-Mail zum Kopieren, in Sie-Form, deutsch,
  kurz und ohne Marketingsprache. Sie greift die Worte des Kunden auf und endet mit Vorname des
  Absenders (Signatur ergänzt der Owner selbst).
- Bei Erstgesprächen enthält die Mail den Satz: "Alle Dokumente und Informationen habe ich Ihnen in
  diesem Board zusammengestellt: **[Along-Link einfügen]**". Der Platzhalter bleibt stehen, der Owner
  setzt das Along-Board ein. Keine Auflistung einzelner Dokumente.
- `<strong>Prüfpunkte vor dem Senden</strong>` als Nummernliste: Along-Link einsetzen, Widersprüche,
  Preisthemen, Datenpflege (fehlender Owner, widersprüchlicher Status), Signatur.
- Fußzeile in Grau: "Automatisch erstellt vom Granola-Antwortvorschlag. Bitte vor dem Senden prüfen."

**Absender:** der Kontakt-Owner. Hat der Kontakt keinen Owner, wird die Person aus den
Hivebuy-Teilnehmenden der Notiz abgeleitet (die das Gespräch geführt hat) und der fehlende Owner als
Prüfpunkt vermerkt.

## Impact Ladder PDF (Teil d2)

Direkt nach dem Antwortvorschlag wird für dasselbe Erstgespräch die Skill `impact-ladder-pdf`
ausgeführt (`.claude/skills/impact-ladder-pdf/SKILL.md`). Sie erzeugt ein zweiseitiges PDF im
Hivebuy-Design, das den Nutzen auf vier Ebenen zeigt: Mitarbeitende, Einkauf, Finance, Management.

Ablauf: Inhalte als JSON nach `output/<kunde-slug>-impact-ladder.json` schreiben, dann
`node scripts/render.js output/<kunde-slug>-impact-ladder.json`. Layout, Farben und Typografie kommen
ausschließlich aus `template/template.html` und werden nie von Claude verändert. Analyse-Regeln,
Sprachregeln, Agentennamen und QA-Checkliste stehen in der SKILL.md.

### Auslieferung des PDFs (offener Punkt)

Der Pfad des PDFs wird im Antwortvorschlag am Kontakt als eigener Abschnitt genannt und in der
Slack-DM mitgeschickt. Das PDF liegt im Container, es wird nicht automatisch an den Kunden gesendet.

**Problem:** Ein Pfad im Container hilft dem Owner nicht, er kann die Datei nicht selbst
herunterladen (gemeldet von Moritz am 20.08.2026 zum Fall NAVAX).

**Geplante Lösung:** PDF per Files-API nach HubSpot hochladen und als Anhang an die
Antwortvorschlag-Notiz hängen, damit der Owner es direkt aus dem Kontakt heraus öffnen kann:

1. `POST /files/v3/files` (multipart) mit `folderPath=/impact-ladder` und
   `options={"access":"PRIVATE","overwrite":true}`, Antwort enthält die File-ID.
2. Beim Anlegen der Notiz `hs_attachment_ids` auf diese File-ID setzen.
3. Statt des Container-Pfads den HubSpot-Dateilink in Notiz und Slack-DM nennen.

**Status:** Der Files-Scope wurde am 20.08.2026 ergänzt, der Upload funktioniert. Erster Fall:
File 456625533137, angehängt an Notiz 513254551785 und 513295632616 am Kontakt 738633192677.
Ein Download-Link auf sieben Tage lässt sich per
`GET /files/v3/files/{fileId}/signed-url?expirationSeconds=604800` erzeugen.

## Bearbeitbare Fassung als Google Slides (Teil d3)

Neben dem PDF entsteht eine bearbeitbare Präsentation, damit der Owner Inhalte anpassen kann
(Vorgabe Moritz, 20.08.2026: als Google Slides, Freigabe an alle Hivebuy-Mitarbeitenden).

Ablauf:

1. `python3 scripts/render_pptx.py output/<kunde-slug>-impact-ladder.json` erzeugt aus demselben
   JSON wie das PDF eine **sechsseitige** Präsentation im 16:9-Format. Schriften sind Frank Ruhl
   Libre und DM Sans, beide in Google Slides vorhanden. Reihenfolge und Überschriften (Vorgabe
   Moritz, 25.08.2026):

   | Slide | Überschrift | Quelle im Granola-Eintrag |
   |---|---|---|
   | 1 | Impact Ladder (Titel) | Kunde, Ansprechpartner, Datum |
   | 2 | Aktuelle Optimierungspotenziale | Pain Points, Beschreibung des Problems |
   | 3 | Wie optimiert Hivebuy den Prozess | **Umsetzung in Hivebuy (Pain Killer)**, JSON-Feld `painkiller` |
   | 4 | Vorteile für Bedarfsträger und den Einkauf | Ladder-Ebene 1 und 2 |
   | 5 | Vorteile für Finance & Controlling und die Geschäftsführung | Ladder-Ebene 3 und 4 |
   | 6 | Zusammenfassung | executive_summary, Zahlenbasis, nächster Schritt |

   Slide 3 ist neu und braucht im JSON die Liste `painkiller`, acht bis elf kurze Funktionen aus
   dem Pain-Killer-Abschnitt. Fehlt die Liste, wird die Slide übersprungen. Die Status-Marker
   "(belegt)" und "(annahme)" bleiben in der Bearbeitungsfassung stehen.
2. `python3 scripts/slim_pptx.py output/<datei>.pptx` entfernt die ungenutzten Layouts, das
   Thumbnail, die Druckereinstellungen und die optionalen Teile `docProps/core.xml`,
   `docProps/app.xml`, `presProps.xml`, `viewProps.xml` und `tableStyles.xml`. 39 KB werden zu
   rund 18,5 KB, das sind etwa 25.000 Base64-Zeichen.

   Kleiner ist beim Upload besser, weil der Inhalt als Base64 im Tool-Aufruf übergeben wird und
   die Zeichenkette dabei fehlerfrei durchkommen muss.

   **Die eigentliche Grenze liegt in der Übergabe, nicht bei Drive (geklärt am 03.09.2026).**
   Die Base64-Zeichenkette wird als Argument im Tool-Aufruf übergeben und muss dafür Zeichen
   für Zeichen ausgegeben werden. Dabei geht sie manchmal kaputt, in zwei Varianten: entweder
   antwortet Drive mit "The file content is not a valid base64 string", oder Drive dekodiert die
   beschädigte Kette stillschweigend zu einer anderen, kaputten Datei. Beobachtungen vom
   03.09.2026 an Wiedmann &amp; Winz: 18.547 Bytes (24.732 Zeichen) und 18.419 Bytes
   (24.560 Zeichen) scheiterten beide mit der Fehlermeldung, 18.143 Bytes (24.192 Zeichen) kamen
   als 17.751 Bytes an.

   **Korrektur vom 08.09.2026: Es ist keine Größengrenze, sondern Unzuverlässigkeit.** Die
   frühere Annahme, ab rund 24.000 Zeichen brenne die Übergabe zuverlässig durch, ist widerlegt:

   | Datei | Base64-Zeichen | lokal | in Drive | Ergebnis |
   |---|---|---|---|---|
   | Spektra Dresden, 1. Versuch | 24.528 | 18.396 | 18.396 | **exakt, in Ordnung** |
   | Dörrenberg, 1. Versuch | 24.472 | 18.352 | 19.129 | beschädigt |
   | Dörrenberg, 2. Versuch | 24.472 | 18.352 | 18.003 | beschädigt, anders |
   | AMW Pharmaceuticals, 1. Versuch | 24.456 | 18.340 | keine Datei | abgelehnt |
   | AMW Pharmaceuticals, 2. Versuch | 24.456 | 18.340 | keine Datei | abgelehnt, gleiche Stelle |
   | AMW Pharmaceuticals, 3. Versuch | 24.456 | 18.340 | 17.836 | beschädigt |

   Dieselbe Datei kam bei zwei Versuchen mit zwei verschiedenen falschen Größen an, während eine
   **größere** Kette im selben Zeitraum fehlerfrei durchlief. Die Übergabe ist also nicht
   größenbegrenzt, sondern schlicht unzuverlässig, und der Fehler ist von außen unsichtbar.

   **Ursache, gemessen am 09.09.2026.** Der Dekoder auf der Gegenseite ist strikt: ein
   Testupload mit einer gültigen, aber über zwei Zeilen umgebrochenen Base64-Kette
   (`SGFsbG8gV2Vs` + Zeilenumbruch + Rest) wurde mit derselben Meldung "The file content is not
   a valid base64 string" abgelehnt. Ein einziges Leerzeichen genügt also. Genau das passiert:
   die Kette muss als 24.456 Zeichen durch die Modellausgabe, und in einer so langen Zeichenkette
   entstehen Leerzeichen und Umbrüche. Zwei Befunde dazu:

   - **Die Abweichung ist teilweise deterministisch.** Versuch 1 und 2 waren dieselbe Kette und
     brachen an derselben Stelle (im Bereich `ppt/slides/slide5.xml`). Denselben String erneut zu
     senden ist deshalb sinnlos. Erst nach `render_pptx.py` + `slim_pptx.py` (gleicher Inhalt,
     neue Zip-Zeitstempel, wieder 18.340 Bytes) war die Kette anders und der Upload lief durch,
     dann allerdings in die stille Variante mit 17.836 Bytes.
   - **Es gibt keinen Weg in Stücken.** `mcp__Google_Drive__update_file` ändert nur Metadaten
     (Titel, parentId), nicht den Inhalt. `create_file` mit `base64Content` ist der einzige
     Kanal, und er nimmt die Datei nur als einen zusammenhängenden String.

   Damit sind alle drei Ausgänge für eine einzige Datei in einem Lauf belegt: abgelehnt,
   abgelehnt an gleicher Stelle, angenommen und beschädigt.

   Praktische Folgen:

   - Die Größenprüfung nach jedem Upload ist keine Vorsichtsmaßnahme, sondern der einzige Weg,
     einen Fehlschlag überhaupt zu bemerken. Sie ist Pflicht (siehe unten).
   - Ein Fehlversuch ist nicht folgenlos: er legt eine kaputte Datei im Ordner ab. Genau das ist
     der Grund, warum im Ordner Dateien liegen, die sich nicht öffnen lassen.
   - Wiederholen ist sinnvoll, weil derselbe Inhalt beim nächsten Versuch durchkommen kann, aber
     jeder Versuch braucht danach die Größenprüfung und im Fehlerfall das Aufräumen.
   - Wiederholen heißt nicht "denselben String nochmal senden". Nach einer Ablehnung erst die
     Präsentation neu erzeugen (`render_pptx.py`, dann `slim_pptx.py`), damit die Base64-Kette
     eine andere ist. Sonst bricht sie an derselben Stelle wieder.

   **Kürzen hilft nicht (geprüft am 03.09.2026).** Am selben Tag wurde versucht, die Datei durch
   deutlich kürzere Texte unter die Grenze zu bringen: zwei Potenziale weniger, `painkiller` von
   zehn auf acht Punkte, alle Bullets, `zahlenbasis` und `annahmen` gestrafft. Ergebnis: von
   18.064 auf 18.018 Bytes, also 46 Bytes. Der Grund ist, dass die komprimierte Datei von der
   XML-Struktur der sechs Slides bestimmt wird, nicht vom Text; dazu kommen rund 2,8 KB
   Zip-Verwaltung bei 21 Einträgen. Auch ein Neupacken mit allen Deflate-Strategien brachte
   null Bytes. **Rund 18 KB ist der Boden für die vorgegebene Sechs-Slide-Struktur.** Texte
   werden deshalb nicht mehr wegen der Dateigröße gekürzt, das verschlechtert nur den Inhalt.

   Konsequenz: Über diesen Connector ist der Upload nicht zuverlässig zu schaffen. Bis eine
   andere Übertragung eingerichtet ist, gilt: Länge und Teilbarkeit prüfen mit
   `python3 -c "import base64;b=base64.b64encode(open(PFAD,'rb').read());print(len(b),len(b)%4)"`,
   die Kette in einer Zeile übergeben, danach `fileSize` mit der lokalen Größe vergleichen und
   höchstens zweimal wiederholen. Danach den Upload als offen melden statt weiter zu versuchen.

   **Vorschlag für eine dauerhafte Lösung (offen, braucht eine Entscheidung von Moritz):** Ein
   Service-Account-Key als Umgebungsvariable im Container. Dann lädt die Routine die Datei per
   `curl` direkt an die Drive-API hoch, die Base64-Kette läuft nicht mehr durch die
   Modellausgabe, und die Trigger-Läufe sind zugleich nicht mehr vom wackeligen
   MCP-Connector abhängig.

   Nach den Messungen vom 09.09.2026 ist das nicht eine von mehreren Möglichkeiten, sondern die
   einzige. Alles andere ist geprüft und ausgeschlossen: kürzen bringt nichts (rund 18 KB ist der
   strukturelle Boden, 15.576 Bytes komprimierte Teile plus rund 2,8 KB Zip-Verwaltung über die
   21 Pflichteinträge des OOXML-Formats), stückweise Übertragung gibt es nicht (`update_file`
   ändert nur Metadaten), und Leerzeichen in der Kette werden hart abgelehnt. Solange die Datei
   als ein 24.000-Zeichen-String durch die Modellausgabe muss, bleibt jeder Upload ein
   Glücksspiel mit drei Ausgängen, von denen einer eine unlesbare Datei im Ordner hinterlässt.
   Im Container liegen derzeit keine Google-Zugangsdaten (geprüft: keine passenden
   Umgebungsvariablen, kein `gcloud` in `~/.config`), deshalb kann die Routine diesen Weg nicht
   selbst einrichten.

   **Was Moritz dafür tun muss:** in der Google Cloud Console einen Service-Account anlegen, ihm
   Schreibrechte auf den Ordner `0APJQKQ-OeVKNUk9PVA` geben (Ordner für die Service-Account-Mail
   freigeben) und den JSON-Key als Secret in die Environment-Konfiguration der Session legen,
   zum Beispiel als `GOOGLE_SERVICE_ACCOUNT_JSON`. Danach kann die Routine den Upload wie die
   HubSpot-Arbeit per `curl` erledigen.
3. Upload per `mcp__Google_Drive__create_file` mit
   `contentMimeType=application/vnd.openxmlformats-officedocument.presentationml.presentation`,
   `parentId=0APJQKQ-OeVKNUk9PVA` und **`disableConversionToGoogleType=true`**. Der Dateiname
   endet auf `.pptx`.

   **Ohne dieses Flag schlägt der Upload mit "Invalid conversion requested" fehl** (festgestellt
   am 26.08.2026). Drive konvertiert pptx nicht automatisch nach Google Slides. Das ist kein
   Problem: die hochgeladene pptx lässt sich unter
   `https://docs.google.com/presentation/d/<file-id>/edit` direkt in Google Slides im Browser
   öffnen und bearbeiten. Genau dieser Link wird weitergegeben, nicht die `viewUrl` aus der
   Tool-Antwort.
4. **Keine Freigabe per Tool nötig.** Moritz hat am 20.08.2026 am Zielordner
   (https://drive.google.com/drive/folders/0APJQKQ-OeVKNUk9PVA) "alle bei Hivebuy können
   bearbeiten" gesetzt. Neue Dateien im Ordner erben das. `share_file` wird also nicht aufgerufen,
   das wäre eine zusätzliche, unnötige Rechteänderung.
5. Slides-Link zusätzlich zum PDF in Antwortvorschlag und Slack-DM nennen.

**Wichtig:** Das PDF aus `template/template.html` bleibt die verbindliche Fassung für den Kunden,
das Layout wird nie verändert. Die Präsentation ist die Arbeitsversion und darf davon abweichen.

**Pflicht (Moritz, 25.08.2026):** Die Präsentation muss immer bearbeitbar in Google Drive liegen.
Der Upload ist damit kein optionaler Schritt mehr.

**Offen:** Der Google-Drive-Connector ist in dieser Umgebung unzuverlässig, er ist oft nur für
einzelne Turns verbunden. Beobachtung vom 26.08.2026, bestätigt am 02.09.2026: In von Moritz
ausgelösten Turns ist Drive verbunden, in den Trigger-Läufen bisher nie. Am 02.09.2026 war Drive
in einem Moritz-Turn verbunden und fiel im nächsten Trigger-Lauf wieder weg, mitten in der
Nacharbeit der offenen Uploads. Fällt er in einem Lauf aus, wird die Präsentation
trotzdem erzeugt und nach HubSpot hochgeladen, der fehlende Slides-Link wird in der Log-Notiz
vermerkt, und der Upload wird im nächsten Lauf nachgeholt, in dem der Connector verfügbar ist.
Nicht als erledigt melden, solange der Slides-Link fehlt.

### Upload-Prüfung (Pflicht, Moritz 02.09.2026)

**Ein Upload ohne Fehlermeldung ist noch kein erfolgreicher Upload.** Am 02.09.2026 ist die
Präsentation CIRCOR IMO ALLWEILER mit 17.791 Bytes in Drive angekommen, lokal hat die Datei
18.417 Bytes. Drive hat die beschädigte Base64-Zeichenkette also nicht abgelehnt, sondern
stillschweigend zu einer kürzeren, kaputten Datei dekodiert. Die Meldung "The file content is not
a valid base64 string" ist damit nur der **sichtbare** von zwei Fehlerfällen.

Nach jedem Upload deshalb:

1. `fileSize` aus der Antwort von `create_file` mit der lokalen Dateigröße vergleichen
   (`ls -l` oder `stat -c%s`). Bei Abweichung ist die Datei kaputt.
2. Stimmt die Größe nicht, die hochgeladene Datei mit `mcp__Google_Drive__trash_file` entfernen
   und neu hochladen. `update_file` hilft nicht, es ändert nur Metadaten, nicht den Inhalt.

   **Offener Punkt für Moritz (08.09.2026):** Das Werkzeug `trash_file` ist inzwischen verfügbar,
   aber Aufräumen steht nicht in der Liste der freigegebenen Operationen im Routine-Prompt
   ("Erlaubt sind ausschließlich ..."). Die Routine räumt deshalb nicht selbst auf und meldet
   kaputte Dateien nur mit ihrer ID zur Löschung. Wenn der Ordner sauber bleiben soll, ohne dass
   Moritz jedes Mal von Hand löscht, muss "beschädigte eigene Uploads in den Papierkorb
   verschieben" in die Erlaubnisliste aufgenommen werden.
3. Erst danach den Slides-Link weitergeben und den Upload als erledigt melden.

Größengleichheit ist ein starkes, aber kein vollständiges Kriterium: ein einzelnes vertauschtes
Base64-Zeichen lässt die Länge unverändert. Zusätzliche Sicherheit gibt
`mcp__Google_Drive__read_file_content` auf die hochgeladene Datei: kommt der Text aller sechs
Slides zurück, ist das Archiv intakt.

**Bereits hochgeladen** (nicht erneut hochladen):

| Kunde | Gespräch | Slides-Link | Größe geprüft |
|---|---|---|---|
| NAVAX Software | 20.08.2026 | https://docs.google.com/presentation/d/1FxoiYDq3oZmaxHocy68g9vFpTw2-Rhj7/edit | nein, Verdacht (Drive 18.341, lokal 18.755) |
| Techniropa | 24.08.2026 | https://docs.google.com/presentation/d/1zhEzmoGRifqd8OHmrh5gLOiALo05aQVP/edit | ja (18.446) |
| Dalli-Group | 25.08.2026 | https://docs.google.com/presentation/d/1A0AKPSazd6ZwNTbTCbMHHnwZ_k8vEKph/edit | ja (18.369) |
| Sonplas | 26.08.2026 | https://docs.google.com/presentation/d/1HURu7ke_zXCAQD5n1wJVe5sA4GkxOEyM/edit | ja (18.376) |
| Ameos Spital Einsiedeln | 27.08.2026 | https://docs.google.com/presentation/d/1NOCdh60GwuJduZMDLPVo-pA2Gq5MN8G9/edit | ja (18.280) |
| Schmalz | 27.08.2026 | https://docs.google.com/presentation/d/1q8vdjyAdQh8D2YgByEnnJPcc1RJkisaQ/edit | ja (18.416) |
| Spektra Dresden | 04.09.2026 | https://docs.google.com/presentation/d/11nxqXbBEspSAc-SCSQbIH4JMwnkwAnov/edit | ja (18.396) |

Offen sind:

- **AMW Pharmaceuticals (08.09.2026):** Drei Versuche am 09.09.2026 (siehe die Tabelle oben).
  Der dritte wurde angenommen, ist aber beschädigt. Bitte löschen:
  1StR-IY8g4Li2IpFhnc-5wqhuTsGJifEb (17.836 statt 18.340 Bytes). Lokal:
  `output/2026-09-08-impact-ladder-amw-pharmaceuticals.pptx`. Danach neu hochladen.

- **Dörrenberg (07.09.2026):** Zwei Versuche am 08.09.2026, beide beschädigt und beide noch im
  Ordner. Bitte löschen: 1gZmYgy9JoNtxDUZPW0mXqolxBX8PRz2T (19.129 Bytes) und
  1mNdHqIBZk15o5TxTCQImFaaypZ9YxLeU (18.003 Bytes). Lokal:
  `output/2026-09-07-impact-ladder-doerrenberg.pptx` mit 18.352 Bytes. Danach neu hochladen.

- **CIRCOR IMO ALLWEILER (28.08.2026):** Datei 1u8gi_nn8UZK3qKWoa7WF5A8wziEEcVwx liegt beschädigt
  im Ordner (18.177 statt 18.417 Bytes). Am 03.09.2026 mit `read_file_content` geprüft: die Antwort
  ist leer, das Archiv ist also tatsächlich unlesbar. Die beiden früheren Fehlversuche
  (1bfrfij3JGhDiqc7gN\_G6fkW-0wz8dfKg, 1wNr6XiEZmq3AIDIVef7ZW1X7jEKRM19y) sind schon im Papierkorb.
  Zu tun: diese Datei in den Papierkorb, die pptx auf unter 18 KB bringen und neu hochladen.
- **Wiedmann &amp; Winz (03.09.2026):** Datei 1pnT3PnOobd2kC6-J4M_ka7Gb7FMVzjsZ liegt beschädigt im
  Ordner (17.751 statt 18.143 Bytes). `trash_file` war in dem Lauf nicht verfügbar. Zu tun: Datei
  in den Papierkorb und `output/2026-09-03-impact-ladder-wiedmann-winz.pptx` neu hochladen.
- **Götz-Gruppe (04.09.2026):** `output/2026-09-04-impact-ladder-goetz-gruppe.pptx` (18.379 Bytes,
  24.508 Base64-Zeichen). Ein Versuch, abgelehnt mit "not a valid base64 string". Nach der Regel
  oben nicht weiter versucht.
- **Microdul AG (01.09.2026):** `output/2026-09-01-impact-ladder-microdul-ag.pptx`, noch nicht
  hochgeladen.
- **NAVAX Software (20.08.2026):** Größe prüfen, bei Abweichung neu hochladen.
- **Wesemann (21.08.2026):** `output/2026-08-21-impact-ladder-wesemann.pptx` stammt aus der Zeit vor
  der Sechs-Slide-Struktur und hat nur fünf Slides, weil im JSON die Liste `painkiller` fehlt. Sie
  muss erst aus dem Pain-Killer-Abschnitt des Granola-Eintrags ergänzt und die Präsentation neu
  erzeugt werden, dann hochgeladen.

## Slack-Benachrichtigung (Teil e)

Nach dem Anlegen des Antwortvorschlags erhält der Kontakt-Owner eine Slack-DM.

**Owner zu Slack:** Owner-E-Mail über `GET /crm/v3/owners/{ownerId}` lesen, dann per
`slack_search_users` die Slack-User-ID zur E-Mail suchen (Schreibweise der E-Mail kann abweichen,
Vergleich in Kleinbuchstaben). Bekannte Zuordnungen:

| Owner-ID | Name | E-Mail | Slack |
|---|---|---|---|
| 255483530 | Robert Eickmeyer | robert@hivebuy.de | U030FCELYPR |
| 32598807 | Emre Topyürek | emre@hivebuy.de | U0AHY4E0YHY |
| 1773489374 | Moritz Lienert | moritz@hivebuy.de | U071B33N4LQ |
| 77804274 | Dennis Hartmann | dennis@hivebuy.de | U08G4AB71QR |

**Fallback:** Kein Owner am Kontakt oder kein Slack-Treffer, dann geht die DM an Moritz
(U071B33N4LQ) mit Hinweis auf den fehlenden Owner.

**Inhalt der DM:** Kontaktname und Firma, Meeting mit Datum, Einschätzung in einem Satz, der aktive
Anknüpfungspunkt, die wichtigsten Prüfpunkte (immer inklusive Along-Link-Platzhalter) und ein Link
auf den Kontakt. Kurz halten, der Vorschlag selbst steht in HubSpot.

## Log-Notiz (Teil c)

Jede verarbeitete Granola-Notiz erzeugt genau eine Log-Notiz am Kontakt, als HTML formatiert
(Beispiel: Notiz 513071918329 am Kontakt 838456679629):

- Kopf: `<p><strong>🤖 Granola-Sync-Log</strong> (granola-sync:<Notiz-ID>)</p>` (der Marker verhindert Doppelverarbeitung), danach verarbeitete Notiz (ID, Erstelldatum, Meeting) und Qualifizierungsergebnis
- `<h3>1) Übertragene Properties</h3>` mit `<ul>`-Liste: pro Property ein `<li>` mit **Label** (interner Name), Aktion (überschrieben / neu gesetzt / bestätigt / bereinigt), gekürztem neuen Wert, Quelle (Abschnitt) und ggf. altem Wert
- `<h3>2) Bewusst NICHT überschrieben</h3>` nur wenn die Konfliktregel gegriffen hat
- `<h3>3) Nicht übertragene Abschnitte</h3>` mit Aufzählung der Abschnitte ohne Property-Pendant
- `<h3>4) Lead-Pipeline</h3>` mit der Lead-Aktion (angelegt / Phase gesetzt / unverändert / übersprungen) und kurzer Begründung
- `<h3>5) Hinweis</h3>` "Dieser Eintrag wurde automatisch vom Granola-Notiz-Sync erstellt", plus Fehler, übersprungene Schritte und Verweis auf den Antwortvorschlag

## Weitere Sonderfälle

- **Notiz mit mehreren Kontakten:** Verarbeitung für den Kontakt, auf den sich der Inhalt erkennbar bezieht; die anderen Kontakte werden im Log genannt.
- **Nicht-Standard-Notizen** (kein Erstgesprächsformat, z.B. Status-Updates): Es wird übertragen, was sich eindeutig zuordnen lässt (typisch: Next Steps, klar genannter ERP-Name). Abschnitte mit abweichenden Überschriften (z.B. "Schmerzpunkte & Bedarf") werden nicht geraten, sondern im Log gelistet. Ein Abschnitt "Pain" gilt als "Pain Points". Kein Antwortvorschlag, da kein Erstgespräch.
- **Erwähnte Personen ohne eindeutige ERP- oder Budget-Angabe:** Feld nicht setzen, Begründung im Log.

## Betrieb

- Zwei Claude-Routinen, Cron `5 * * * *` und `35 * * * *`, ergibt einen Lauf alle 30 Minuten
  (der Scheduler unterstützt minimal stündliche Cron-Ausdrücke, daher zwei versetzte Routinen).
- Beide Routinen sind an diese Session gebunden, weil hier die HubSpot- und Slack-Verbindungen
  hängen. Eine frische Session hätte diese Verbindungen nicht.
- Lookback 3 Stunden pro Lauf; Doppelverarbeitung wird über die Marker `granola-sync:<Notiz-ID>` und
  `granola-reply:<Notiz-ID>` verhindert.
- Läuft ein Lauf leer (keine neuen Granola-Notizen), passiert nichts und es wird nicht gemeldet.

## Routine-Prompt (Referenz)

Der folgende Prompt ist 1:1 in beiden Routinen hinterlegt:

```
Führe einen Lauf der Routine "Granola-Notiz-Sync und Antwortvorschlag" aus, genau wie in
GRANOLA_SYNC.md auf dem Branch claude/granula-note-automation-rnawt0 beschrieben. Lies die Datei
zuerst, falls du sie nicht mehr im Kontext hast (bei Bedarf: git fetch und git reset --hard
origin/claude/granula-note-automation-rnawt0).

Du läufst ohne menschliche Aufsicht. Moritz Lienert (moritz@hivebuy.de) hat diese Operationen
dauerhaft genehmigt: Verwende bei manage_crm_objects confirmationStatus=CONFIRMED und stelle keine
Rückfragen. Führe ausschließlich die beschriebenen Aktionen aus: Kontakt-Properties setzen, Lead in
der Lead-Pipeline anlegen oder bewegen, Log-Notiz anlegen, Antwortvorschlag als Notiz anlegen,
Slack-DM an den Kontakt-Owner. Keine E-Mails an Kunden, keine anderen CRM-Änderungen, keine
Nachrichten in Slack-Channels.

Ablauf pro Lauf:

1. Neue Granola-Einträge finden
- Suche in ZWEI Objekttypen, beide sind Pflicht:
  a) notes mit hs_createdate GTE (jetzt minus 3 Stunden) UND hs_note_body CONTAINS_TOKEN
     "*notes.granola.ai*"
  b) meetings mit hs_createdate GTE (jetzt minus 3 Stunden) UND hs_meeting_body CONTAINS_TOKEN
     "*notes.granola.ai*"
  Die Wildcards sind Pflicht, ohne sie findet HubSpot Einträge nicht.
- Nutze dafür die HubSpot-REST-API per curl mit HUBSPOT_PRIVATE_APP_TOKEN und fordere nur die
  benötigten Properties an, damit die Antwort klein bleibt.
- Überspringe: eigene Log-Notizen (granola-sync:), eigene Antwortvorschläge (granola-reply:),
  Notizen ohne Kontakt, Notizen am internen Kontakt Hivebuy GmbH (#365219269839) und Notizen ohne
  echten notes.granola.ai-Link.

2. Pro Eintrag: Kontakt und Kontext laden
- Kontakt über GET /crm/v4/objects/{notes|meetings}/{objectId}/associations/contacts, je nach
  Objekttyp des Eintrags.
- Kontakt-Properties, Firma, Deals, weitere Notizen, Calls, Meetings und E-Mails laden, soweit für
  einen guten Vorschlag nötig.

3. Duplikat-Check
- Notizen des Kontakts prüfen: existiert bereits granola-sync:<Objekt-ID>, ist der Eintrag verarbeitet
  und wird übersprungen. Die Objekt-ID ist die ID der Notiz bzw. des Meetings.

4. Properties übertragen
- Mapping, Textbereinigung und Konfliktregel exakt wie in GRANOLA_SYNC.md.
- Schreiben per manage_crm_objects updateRequest.

5. Lead anlegen bzw. bewegen
- Über die REST-API wie in GRANOLA_SYNC.md beschrieben. Statusänderung nur bei QUALIFIZIERT: JA.

6. Log-Notiz anlegen
- Struktur und Marker wie in GRANOLA_SYNC.md.

7. Antwortvorschlag anlegen (nur bei Erstgesprächen)
- Nur wenn der Meeting-Titel "Kennenlernen" enthält. Bei der Meeting-Variante steht der Titel in
  hs_meeting_title, ein Präfix wie "[Granola]" wird ignoriert.
- Aufbau, Tonalität und der Along-Board-Satz mit Platzhalter wie in GRANOLA_SYNC.md.
- Granola-Notiz hat Vorrang vor den HubSpot-Daten, Widersprüche als Prüfpunkt nennen.

7b. Impact Ladder PDF erzeugen (immer direkt nach dem Antwortvorschlag)
- Skill impact-ladder-pdf ausführen: JSON schreiben, dann node scripts/render.js.
- PDF-Pfad im Antwortvorschlag am Kontakt vermerken und in der Slack-DM nennen.

8. Slack-DM an den Kontakt-Owner
- Owner-E-Mail über /crm/v3/owners/{id}, Slack-User über slack_search_users, Fallback Moritz
  (U071B33N4LQ). Inhalt wie in GRANOLA_SYNC.md, inklusive PDF-Pfad.

9. Abschluss
- Keine neuen Granola-Notizen: Lauf still beenden, nichts anlegen, nichts melden.
- Sonst: kurz zusammenfassen, welche Kontakte verarbeitet wurden und was passiert ist.
```
