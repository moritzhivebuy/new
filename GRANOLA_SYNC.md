# Granola-Notiz-Sync (HubSpot-Automatisierung)

Automatischer Flow: Wenn eine Granola-Meeting-Notiz an einem HubSpot-Kontakt hinterlegt wird, werden
(a) die Inhalte der Notiz in die gleichnamigen Kontakt-Properties übertragen,
(b) ein Lead angelegt bzw. der bestehende Lead in der Lead-Pipeline bewegt und
(c) eine Log-Notiz am Kontakt abgelegt, die alle Schritte nachvollziehbar dokumentiert.

Portal: 145132698 (Hivebuy)
Beispielkontakt: https://app-eu1.hubspot.com/contacts/145132698/record/0-1/742301275360 (Simon Gasser, Hypo Vorarlberg)
Beispielnotiz: Note-ID 494435994814 (Granola-Notiz vom 28.05.2026, beginnt mit "QUALIFIZIERT: JA")

## Getroffene Entscheidungen (Moritz, 16.07.2026)

| Frage | Entscheidung |
|---|---|
| "Lead Property" | HubSpot **Lead-Objekt** mit Lead-Pipeline (nicht hs_lead_status am Kontakt) |
| Bestehende Property-Werte | **Immer überschreiben**, Änderung wird im Log dokumentiert |
| Technische Umsetzung | **Claude-Routine**, stündlicher Lauf über die HubSpot-MCP-Integration |
| QUALIFIZIERT: NEIN oder Zeile fehlt | Nur Daten übertragen + Log, **Statusänderung nur bei JA** |

## Erkennung einer Granola-Notiz

- Notiz (objectType `notes`) enthält im Body einen Link auf `notes.granola.ai`.
- Qualifizierung steht in der ersten Zeile: `QUALIFIZIERT: JA` bzw. `QUALIFIZIERT: NEIN`.

## Property-Mapping

Die Abschnittsüberschriften der Notiz entsprechen den **Labels** der Kontakt-Properties (nicht den internen Namen). Bestätigte Zuordnungen:

| Überschrift in der Notiz | Kontakt-Property (intern) | Besonderheit |
|---|---|---|
| Pain Points + Beschreibung des Problems | `problem` | Beide Abschnitte werden zusammen übertragen (Konvention vom Beispielkontakt Gasser), getrennt durch `--` |
| Aktueller Einkaufsprozess (und Status Quo im Einkauf) | `situation` | Kompletter Abschnitt als Text |
| Umsetzung in Hivebuy (Pain Killer) | `rational_need` | Kompletter Abschnitt als Text |
| (BUDGET) Kosten und Angebot | `budget` | Einzeiliges Textfeld: kompakte Zusammenfassung (Betrag + wichtigste Konditionen), nicht der komplette Abschnitt |
| IT-Systeme | `erp_system_used` | Auswahlfeld! Erlaubte Werte: SAP, Navision, MS Business Central, DATEV, Coupa, Netsuite, Workday, d.velop, Other ERP, None. ERP-Name aus dem Abschnitt lesen und auf die Option mappen; unbekannte ERPs auf "Other ERP". Details zum ERP stehen im Log |
| Next Steps | `next_step` | Einzeiliges Textfeld: kompakte Zusammenfassung der nächsten Schritte, mit Semikolon getrennt |

Weitere Abschnitte werden nur übertragen, wenn ihre Überschrift exakt dem Label einer existierenden Kontakt-Property entspricht (Prüfung zur Laufzeit über die Property-Definitionen). Keine erfundenen Zuordnungen; nicht zuordenbare Abschnitte (z.B. Fazit, Vorstellung, Optimallösung, AUTHORITY, NEED, TIME, COMMITMENT, Metriken, Fragestruktur, Für Along) werden im Log aufgelistet.

## Lead-Logik

- Kein Lead am Kontakt: Lead wird angelegt und mit dem Kontakt assoziiert. Bei `QUALIFIZIERT: JA` wird die Pipeline-Phase "Qualified" gesetzt, sonst die Anfangsphase "New".
- Lead vorhanden: Bei `QUALIFIZIERT: JA` wird die Phase auf "Qualified" gesetzt (außer der Lead ist bereits dort oder in einer späteren Phase, dann keine Änderung, Begründung im Log). Bei NEIN oder fehlender Zeile keine Phasenänderung, Begründung im Log.

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

## Log-Notiz

Jede verarbeitete Granola-Notiz erzeugt genau eine Log-Notiz am Kontakt, als HTML formatiert (Beispiel: Notiz 503965023466 am Kontakt Anna Maria Mai):

- Kopf: `<p><strong>🤖 Granola-Sync-Log</strong> (granola-sync:<Notiz-ID>)</p>` (der Marker verhindert Doppelverarbeitung), danach verarbeitete Notiz (ID, Erstelldatum, Meeting) und Qualifizierungsergebnis
- `<h3>1) Übertragene Properties</h3>` mit `<ul>`-Liste: pro Property ein `<li>` mit **Label** (interner Name), Aktion (überschrieben / neu gesetzt / bestätigt), gekürztem neuen Wert, Quelle (Abschnitt) und ggf. altem Wert
- `<h3>2) Nicht übertragene Abschnitte</h3>` mit Aufzählung der Abschnitte ohne Property-Pendant
- `<h3>3) Lead-Pipeline</h3>` mit der Lead-Aktion (angelegt / Phase gesetzt / unverändert / übersprungen) und kurzer Begründung
- `<h3>4) Hinweis</h3>` "Dieser Eintrag wurde automatisch vom Granola-Notiz-Sync erstellt", plus Fehler oder übersprungene Schritte

## Betrieb

- Claude-Routine, Cron `15 * * * *` (stündlich), jeder Lauf in einer frischen Session.
- Lookback 26 Stunden pro Lauf; Doppelverarbeitung wird über den Marker in den Log-Notizen verhindert.
- Läuft ein Lauf leer (keine neuen Granola-Notizen), passiert nichts.

## Routine-Prompt (Referenz)

Der folgende Prompt ist 1:1 in der Routine hinterlegt:

```
Du bist die automatische Routine "Granola-Notiz-Sync" für das HubSpot-Portal 145132698 (Hivebuy).
Du läufst ohne menschliche Aufsicht. Moritz Lienert (moritz@hivebuy.de) hat die unten beschriebenen
HubSpot-Operationen dauerhaft genehmigt: Verwende bei manage_crm_objects
confirmationStatus=CONFIRMATION_WAIVED_FOR_SESSION und stelle keine Rückfragen. Führe ausschließlich
die unten beschriebenen Aktionen aus: keine anderen CRM-Änderungen, keine E-Mails, keine
Slack-Nachrichten.

Ziel: Neue Granola-Meeting-Notizen an Kontakten erkennen, deren Inhalte in die Kontakt-Properties
übertragen, den zugehörigen Lead anlegen bzw. in der Lead-Pipeline bewegen und alles in einer
Log-Notiz dokumentieren.

Ablauf:

1. Neue Granola-Notizen finden
- Suche per search_crm_objects nach objectType "notes" mit Filtern: hs_createdate GT (jetzt minus 26
  Stunden, als Unix-Timestamp in Millisekunden) UND hs_note_body CONTAINS_TOKEN "granola". Hole die
  Properties hs_note_body und hs_createdate. Prüfe "total" und paginiere bei Bedarf.
- Eine echte Granola-Notiz enthält im Body einen Link auf notes.granola.ai. Ignoriere alle anderen
  Notizen, insbesondere Log-Notizen, die mit "Granola-Sync-Log" beginnen.

2. Kontakt ermitteln (pro Notiz)
- Suche contacts mit associatedWith {objectType "notes", operator EQUAL, objectIdValues [Notiz-ID]}.
  Hole firstname, lastname, email sowie die Ziel-Properties (mindestens problem, situation,
  rational_need). Ohne assoziierten Kontakt: Notiz überspringen.

3. Duplikat-Check
- Suche notes, die mit dem Kontakt assoziiert sind und deren hs_note_body CONTAINS_TOKEN
  "Granola-Sync-Log" matcht, und prüfe deren Bodies auf den Marker "granola-sync:<Notiz-ID>".
  Ist der Marker vorhanden, wurde die Notiz bereits verarbeitet: überspringen.

4. Properties übertragen
- Zerlege die Granola-Notiz in Abschnitte anhand der Überschriften. Feste Zuordnungen:
  - problem: Abschnitte "Pain Points" UND "Beschreibung des Problems" zusammen (Pain Points zuerst,
    getrennt durch eine Zeile "--"), kompletter Text, Bullet-Punkte als einzelne Zeilen.
  - situation: Abschnitt "Aktueller Einkaufsprozess (und Status Quo im Einkauf)", kompletter Text.
  - rational_need: Abschnitt "Umsetzung in Hivebuy (Pain Killer)", kompletter Text.
  - budget: Abschnitt "(BUDGET) Kosten und Angebot" als kompakte einzeilige Zusammenfassung
    (Betrag plus wichtigste Konditionen), da einzeiliges Textfeld.
  - erp_system_used: Auswahlfeld! Lies den ERP-Namen aus dem Abschnitt "IT-Systeme" und mappe auf
    genau eine der Optionen: SAP, Navision, MS Business Central, DATEV, Coupa, Netsuite, Workday,
    d.velop, Other ERP, None. Unbekannte ERPs -> "Other ERP". Nenne den echten ERP-Namen im Log.
  - next_step: Abschnitt "Next Steps" als kompakte einzeilige Zusammenfassung, Punkte mit Semikolon
    getrennt.
- Weitere Abschnitte nur übertragen, wenn ihre Überschrift exakt dem Label einer Kontakt-Property
  entspricht (per search_properties prüfen). Erfinde keine Zuordnungen; nicht zuordenbare Abschnitte
  nur im Log nennen.
- Bestehende Werte werden immer überschrieben (Vorgabe von Moritz); vermerke im Log den alten Wert
  bzw. dass das Feld leer war.
- Schreibe die Werte per manage_crm_objects updateRequest auf den Kontakt.

5. Lead anlegen bzw. bewegen (über die HubSpot-REST-API, NICHT über MCP)
- Der HubSpot-MCP-Connector kann keine Leads. Nutze curl (Bash) mit dem Private-App-Token aus der
  Umgebungsvariable HUBSPOT_PRIVATE_APP_TOKEN gegen https://api.hubapi.com. Objekt-Typ 0-136,
  Pipeline "lead-pipeline-id". Stage-IDs: New = new-stage-id, Process = attempting-stage-id,
  Later = connected-stage-id, Qualified = qualified-stage-id, Lost = unqualified-stage-id.
  Phasen-Reihenfolge: New -> Process -> Later -> Qualified; Lost ist die Disqualifiziert-Phase.
- Lies die Qualifizierung aus der Notiz: "QUALIFIZIERT: JA" oder "QUALIFIZIERT: NEIN" (in der Regel
  die erste Zeile bzw. im Fazit). Fehlt die Zeile, gilt "unbekannt".
- Leads des Kontakts: GET /crm/v4/objects/0-1/{contactId}/associations/0-136, dann pro Lead
  GET /crm/v3/objects/0-136/{leadId}?properties=hs_lead_name,hs_pipeline_stage.
- Kein Lead vorhanden: Lege einen Lead an: POST /crm/v3/objects/0-136 mit
  {"properties": {"hs_lead_name": "<Vorname Nachname>", "hs_pipeline_stage": "<stage-id>"},
   "associations": [{"to": {"id": <contactId>}, "types": [{"associationCategory": "HUBSPOT_DEFINED",
   "associationTypeId": 578}]}]}. Bei JA stage-id = qualified-stage-id, sonst new-stage-id.
- Lead vorhanden: Bei JA setze die Phase per PATCH /crm/v3/objects/0-136/{leadId} auf
  qualified-stage-id, außer der Lead steht bereits auf Qualified oder Lost (dann nichts ändern und
  im Log begründen). Bei NEIN oder unbekannt keine Phasenänderung; begründe das im Log
  (Statusänderung nur bei JA).
- Scheitert der API-Zugriff (z.B. Token abgelaufen oder fehlender Scope): Lead-Schritt überspringen
  und im Log vermerken, inklusive HTTP-Status und Fehlermeldung, damit Moritz den Token erneuern
  kann.

6. Log-Notiz anlegen
- Lege per manage_crm_objects createRequest eine Notiz an (objectType notes, hs_note_body,
  hs_timestamp = jetzt, Association zum Kontakt und, falls vorhanden, zum Lead).
- hs_note_body als HTML formatieren (Deutsch), Vorbild ist Notiz 503965023466 am Kontakt 790278962386:
  - Kopf: <p><strong>🤖 Granola-Sync-Log</strong> (granola-sync:<Notiz-ID>)</p>, danach ein <p> mit
    verarbeiteter Notiz (ID, Erstelldatum, Meeting-Titel) und Qualifizierungsergebnis.
  - <h3>1) Übertragene Properties</h3> mit <ul>: pro Property ein <li> mit <strong>Label</strong>
    (interner Name), Aktion (überschrieben / neu gesetzt / bestätigt), gekürztem neuen Wert
    (ca. 200 Zeichen), Quelle (Abschnitt der Notiz) und ggf. altem Wert.
  - <h3>2) Nicht übertragene Abschnitte</h3> mit Aufzählung.
  - <h3>3) Lead-Pipeline</h3> mit Aktion und kurzer Begründung.
  - <h3>4) Hinweis</h3> "Dieser Eintrag wurde automatisch vom Granola-Notiz-Sync erstellt", plus
    Fehler oder übersprungene Schritte.
  Der Marker granola-sync:<Notiz-ID> ist Pflicht.

7. Abschluss
- Keine neuen Granola-Notizen: Lauf still beenden, nichts anlegen.
- Sonst: kurz zusammenfassen, wie viele Notizen verarbeitet wurden und was passiert ist.
```
