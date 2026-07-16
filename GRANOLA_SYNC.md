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

| Überschrift in der Notiz | Kontakt-Property (intern) |
|---|---|
| Pain Points | `problem` |
| Aktueller Einkaufsprozess (und Status Quo im Einkauf) | `situation` |
| Umsetzung in Hivebuy (Pain Killer) | `rational_need` |

Weitere Abschnitte werden nur übertragen, wenn ihre Überschrift exakt dem Label einer existierenden Kontakt-Property entspricht (Prüfung zur Laufzeit über die Property-Definitionen). Kandidaten im Portal: `budget`, `need`, `emotional_need`, `erp_system_used`, `next_step`. Keine erfundenen Zuordnungen; nicht zuordenbare Abschnitte werden im Log vermerkt.

## Lead-Logik

- Kein Lead am Kontakt: Lead wird angelegt und mit dem Kontakt assoziiert. Bei `QUALIFIZIERT: JA` wird die Pipeline-Phase mit Label "Qualifiziert" gesetzt, sonst die Standard-Anfangsphase.
- Lead vorhanden: Bei `QUALIFIZIERT: JA` wird die Phase auf "Qualifiziert" gesetzt (außer der Lead ist bereits dort oder in einer späteren Phase, dann keine Änderung, Begründung im Log). Bei NEIN oder fehlender Zeile keine Phasenänderung, Begründung im Log.

**Offener Punkt:** Die HubSpot-MCP-Integration hat aktuell keine Berechtigung auf das Lead-Objekt ("User does not have permissions to view leads"). Bis das in HubSpot freigeschaltet ist (Benutzer-/App-Berechtigung für CRM > Leads), überspringt die Routine den Lead-Schritt und vermerkt das im Log. Property-Sync und Log funktionieren bereits.

## Log-Notiz

Jede verarbeitete Granola-Notiz erzeugt genau eine Log-Notiz am Kontakt:

- Zeile 1: `🤖 Granola-Sync-Log (granola-sync:<Notiz-ID>)` (der Marker verhindert Doppelverarbeitung)
- Verarbeitete Notiz (ID, Erstelldatum) und Qualifizierungsergebnis
- Übertragene Properties mit gekürztem neuen Wert und Hinweis, ob ein alter Wert überschrieben wurde
- Lead-Aktion (angelegt / Phase gesetzt / unverändert) mit kurzer Begründung
- Fehler oder übersprungene Schritte

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
- Zerlege die Granola-Notiz in Abschnitte anhand der Überschriften.
- Übertrage nur Abschnitte, deren Überschrift (Groß-/Kleinschreibung egal) exakt dem Label einer
  Kontakt-Property entspricht. Bestätigte Zuordnungen: "Pain Points" -> problem, "Aktueller
  Einkaufsprozess (und Status Quo im Einkauf)" -> situation, "Umsetzung in Hivebuy (Pain Killer)"
  -> rational_need. Prüfe weitere Überschriften per search_properties (objectType contacts) auf ein
  exakt passendes Label. Erfinde keine Zuordnungen; nicht zuordenbare Abschnitte nur im Log nennen.
- Formatiere Werte als Klartext, Bullet-Punkte als einzelne Zeilen. Bestehende Werte werden immer
  überschrieben (Vorgabe von Moritz); vermerke im Log, wenn ein vorhandener Wert ersetzt wurde.
- Schreibe die Werte per manage_crm_objects updateRequest auf den Kontakt.

5. Lead anlegen bzw. bewegen
- Lies die Qualifizierung aus der Notiz: "QUALIFIZIERT: JA" oder "QUALIFIZIERT: NEIN" (in der Regel
  die erste Zeile). Fehlt die Zeile, gilt "unbekannt".
- Suche leads mit associatedWith zum Kontakt (Properties hs_pipeline_stage, hs_lead_name). Lies die
  verfügbaren Phasen über get_properties(objectType "leads", ["hs_pipeline_stage"]) und finde die
  Phase, deren Label "Qualifiziert" entspricht.
- Kein Lead vorhanden: Lege per manage_crm_objects createRequest einen Lead an (hs_lead_name =
  "Vorname Nachname" des Kontakts, Association zum Kontakt). Bei JA setze hs_pipeline_stage auf die
  Qualifiziert-Phase, bei NEIN oder unbekannt die Standard-Anfangsphase.
- Lead vorhanden: Bei JA setze hs_pipeline_stage auf die Qualifiziert-Phase, außer der Lead steht
  bereits dort oder in einer späteren Phase (dann nichts ändern und im Log begründen). Bei NEIN oder
  unbekannt keine Phasenänderung; begründe das im Log (Statusänderung nur bei JA).
- Scheitert der Leads-Zugriff mit einem Berechtigungsfehler: Lead-Schritt überspringen und im Log
  vermerken: "Lead-Schritt übersprungen: Die HubSpot-Integration hat keine Berechtigung für das
  Lead-Objekt."

6. Log-Notiz anlegen
- Lege per manage_crm_objects createRequest eine Notiz an (objectType notes, hs_note_body,
  hs_timestamp = jetzt in Millisekunden, Association zum Kontakt und, falls vorhanden, zum Lead).
- Aufbau des Bodys (Deutsch):
  Zeile 1: "🤖 Granola-Sync-Log (granola-sync:<Notiz-ID>)"
  Danach: verarbeitete Granola-Notiz (ID, Erstelldatum), Qualifizierungsergebnis, Liste der
  übertragenen Properties mit neuem Wert (je Property auf ca. 200 Zeichen kürzen) und Hinweis, ob
  ein alter Wert überschrieben wurde, die Lead-Aktion mit kurzer Begründung, sowie Fehler oder
  übersprungene Schritte. Der Marker granola-sync:<Notiz-ID> ist Pflicht.

7. Abschluss
- Keine neuen Granola-Notizen: Lauf still beenden, nichts anlegen.
- Sonst: kurz zusammenfassen, wie viele Notizen verarbeitet wurden und was passiert ist.
```
