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

- Notiz (objectType `notes`) enthält im Body einen Link auf `notes.granola.ai`.
- Qualifizierung steht meist in der ersten Zeile bzw. im Fazit: `QUALIFIZIERT: JA` bzw. `QUALIFIZIERT: NEIN`.

**Wichtig, Suchsyntax:** Die Suche muss mit Wildcards arbeiten: `CONTAINS_TOKEN` mit dem Wert
`*notes.granola.ai*`. Ohne Wildcards (`granola`) findet HubSpot einen Teil der Notizen nicht. Das ist
beim Testlauf aufgefallen: die ungenaue Suche lieferte als "neueste" Notiz den 08.07., tatsächlich
existierten Notizen bis zum 17.08.

## Auszuschließende Notizen

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

- Kein Lead am Kontakt: Lead wird angelegt und mit dem Kontakt assoziiert. Bei `QUALIFIZIERT: JA` wird die Pipeline-Phase "Qualified" gesetzt, sonst die Anfangsphase "New".
- Lead vorhanden: Bei `QUALIFIZIERT: JA` wird die Phase auf "Qualified" gesetzt (außer der Lead ist bereits dort oder in einer späteren Phase, dann keine Änderung, Begründung im Log). Bei NEIN oder fehlender Zeile keine Phasenänderung, Begründung im Log.
- Lead in Phase "Lost": wird nie automatisch verändert.

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

Der Pfad des PDFs wird im Antwortvorschlag am Kontakt als eigener Abschnitt genannt und in der
Slack-DM mitgeschickt. Das PDF liegt im Container, es wird nicht automatisch an den Kunden gesendet.

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

1. Neue Granola-Notizen finden
- Suche notes mit hs_createdate GTE (jetzt minus 3 Stunden) UND hs_note_body CONTAINS_TOKEN
  "*notes.granola.ai*". Die Wildcards sind Pflicht, ohne sie findet HubSpot Notizen nicht.
- Nutze dafür die HubSpot-REST-API per curl mit HUBSPOT_PRIVATE_APP_TOKEN und fordere nur die
  benötigten Properties an, damit die Antwort klein bleibt.
- Überspringe: eigene Log-Notizen (granola-sync:), eigene Antwortvorschläge (granola-reply:),
  Notizen ohne Kontakt, Notizen am internen Kontakt Hivebuy GmbH (#365219269839) und Notizen ohne
  echten notes.granola.ai-Link.

2. Pro Notiz: Kontakt und Kontext laden
- Kontakt über GET /crm/v4/objects/notes/{noteId}/associations/contacts.
- Kontakt-Properties, Firma, Deals, weitere Notizen, Calls, Meetings und E-Mails laden, soweit für
  einen guten Vorschlag nötig.

3. Duplikat-Check
- Notizen des Kontakts prüfen: existiert bereits granola-sync:<Notiz-ID>, ist die Notiz verarbeitet
  und wird übersprungen.

4. Properties übertragen
- Mapping, Textbereinigung und Konfliktregel exakt wie in GRANOLA_SYNC.md.
- Schreiben per manage_crm_objects updateRequest.

5. Lead anlegen bzw. bewegen
- Über die REST-API wie in GRANOLA_SYNC.md beschrieben. Statusänderung nur bei QUALIFIZIERT: JA.

6. Log-Notiz anlegen
- Struktur und Marker wie in GRANOLA_SYNC.md.

7. Antwortvorschlag anlegen (nur bei Erstgesprächen)
- Nur wenn der Meeting-Titel "Kennenlernen" enthält.
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
