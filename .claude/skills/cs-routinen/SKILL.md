---
name: cs-routinen
description: Definiert die HubSpot-basierten Customer-Success-Reporting-Routinen (Engagement, Tickets, Renewals), die als datierte Unterseiten in Notion unter "CS-Reports" abgelegt werden. Nutzen, wenn eine dieser Routinen ausgeführt, geändert oder ihre Methodik nachgeschlagen werden soll.
---

# CS-Routinen

Diese Datei ist die maßgebliche Quelle für die drei CS-Reporting-Routinen. Die Notion-Seite "CS-Reports" verweist explizit hierher: Änderungen an Methodik, Schwellenwerten, Filtern oder Cadence gehören in diese Datei, nicht direkt in Notion. Ein Lauf einer Routine liest diese Datei, erzeugt den Report aus HubSpot-Daten und legt ihn als neue datierte Unterseite unter der Notion-Seite "CS-Reports" ab (Pfad: Hivebuy GmbH > New: Customer Success > ... > CS-Reports, Page-ID `3ba6f8c1d67e817984a1ea4630d1087f`).

## Gemeinsame Konventionen aller Routinen

- **Basis:** aktive Kunden = `COMPANY.lifecyclestage = 'customer'` AND `COMPANY.churn_date IS NULL`, abzüglich der bekannten Ausschlüsse (siehe unten). Stand 19.08.2026: 73 aktive Kunden.
- **Bekannte Ausschlüsse aus der Basis:**
  - `d.velop` (HubSpot-ID `401316842690`): kein Kunde laut Moritz Lienert (12.08.2026), `lifecyclestage` im CRM aber noch nicht korrigiert. Bis das im CRM gefixt ist, hängt der Ausschluss an dieser Liste.
- **Bekannte Dubletten** (mehrere COMPANY-Records mit demselben Namen, ein Teil davon ohne eigenen MRR):
  - igus SE & Co. KG.: `188745085157` (aktiv, mit MRR) und `401851610339` (Karteileiche, kein MRR, kein Owner-Aktivität)
  - igus GmbH: `401764367589` (Karteileiche, kein MRR)
  - JMarquardt Audiovisual: `17554843636` (aktiv) und JMarquardt Audiovisual GmbH `49463093489` (Karteileiche)
  - rebuy: `401457651913` (aktiv) und reBuy reCommerce Services GmbH & Co. KG `18622719466`
  - Diese Karteileichen bleiben in der Basis (sie sind formal `lifecyclestage = customer`), tauchen aber in den Reports als datenqualitätsauffällig auf, nicht als echtes Risiko.
- **Nichts wird geschätzt.** Fehlt ein Wert, steht `-` oder "nicht berechenbar", nie `0` oder ein geratener Wert. Vorschläge zur Nachpflege (z. B. Vertragsende aus `contract_start_date` + `contract_duration_months_`) werden explizit als Vorschlag markiert, nie als CRM-Fakt behandelt.
- **Alle Kunden- und Deal-Namen sind auf den HubSpot-Record verlinkt**, auch in Datenqualitäts-Aufzählungen. Link-Format: `https://app-eu1.hubspot.com/contacts/145132698/record/0-2/{company_id}` für Companies, `/0-3/{deal_id}` für Deals.
- **Stil:** Deutsch, keine Gedankenstriche/Halbgeviertstriche/Bindestrich-Ketten als Satzzeichen (Kommas, Punkte oder Doppelpunkte verwenden), keine geschätzten Zahlen, jeder Ausschluss wird benannt statt stillschweigend fallen gelassen.
- **Seitentitel in Notion:** `YYYY-MM-DD — <Routinenname>` (z. B. "2026-08-19 — Engagement"), Icon je Routine konsistent halten (Engagement: 🚦, Renewals: 🔁).
- **Jeder Report hat einen Datenqualitäts-Block**, der mindestens die oben stehenden Ausschlüsse/Dubletten sowie fehlende Owner nennt.

## Routine 1: Engagement

**Cadence:** monatlich. **Ziel-Channel:** Slack `#customer-experience`, mit Erwähnung von Bettina Fischer, Leonard Diemer und Moritz Lienert (Slack-User-IDs unten). **Notion:** CS-Reports, Seitentitel `YYYY-MM-DD — Engagement`, Icon 🚦.

### Definition

Ein Kunde ist "engaged", wenn `last_touch` innerhalb der letzten 30 Tage liegt. `last_touch` ist das Maximum aus fünf Quellen:

1. `TICKET`: `MAX(createdate, hs_lastactivitydate, hs_last_message_sent_at, hs_last_message_received_at)`, verknüpft über `COMPANY.lifecyclestage = 'customer'`. Nicht nur `createdate` nehmen: laufende Korrespondenz in einem alten Ticket sonst untererfasst (gefunden 19.08.2026 bei Kasaero GmbH und IPG Automotive).
2. `CALL.hs_timestamp`, verknüpft über COMPANY.
3. `MEETING_EVENT.hs_meeting_start_time`, verknüpft über COMPANY.
4. `COMPANY.hs_last_sales_activity_timestamp` ("passiv": Tracking-Pixel, Formulare, Meeting-Link-Klicks, tracked E-Mails, keine menschliche Aktion).
5. **Kontakt-Touch:** `MAX(CONTACT.notes_last_contacted)` über alle mit der Company verknüpften Kontakte. Ohne diese Quelle übersieht man Aktivität, die nur am CONTACT hängt und nicht ins COMPANY-Rollup einfließt (gefunden 19.08.2026 bei Securitas Suomi: Meeting nur mit dem Kontakt Tuulia Kivikko verknüpft, nicht mit der Company; COMPANY-Rollup zeigte 288 Tage Stille statt tatsächlich 100).

SQL-Grundmuster (HubSpot-SQL-Dialekt, kein JOIN/UNION/Subquery, max. 2 assoziierte Objekttypen pro Query, daher als separate Queries und in Python zusammengeführt):

```sql
-- Basis
SELECT hs_object_id, name, domain, company_mrr, contract_end_date, hubspot_owner_id,
       hs_last_sales_activity_timestamp, hs_last_logged_call_date, engagements_last_meeting_booked
FROM COMPANY WHERE lifecyclestage = 'customer' AND churn_date IS NULL

-- Ticket-Aktivität
SELECT COMPANY.name, MAX(hs_lastactivitydate), MAX(hs_last_message_sent_at), MAX(hs_last_message_received_at), MAX(createdate)
FROM TICKET WHERE COMPANY.lifecyclestage = 'customer' GROUP BY COMPANY.name

-- Kontakt-Touch
SELECT COMPANY.name, MAX(notes_last_contacted) FROM CONTACT
WHERE COMPANY.lifecyclestage = 'customer' GROUP BY COMPANY.name
```

Firmennamen aus TICKET/CALL/MEETING_EVENT/CONTACT-Queries kommen kleingeschrieben und HTML-entkodiert zurück (z. B. "büfa gmbh & co. kg"), die COMPANY-Basis-Query liefert Original-Schreibweise ("BÜFA GmbH & Co. KG"). Vor dem Join normalisieren über `html.unescape().strip().lower()`.

### Risikostufen

| Stufe | Bedingung |
|---|---|
| Rot | `last_touch` liegt mehr als 60 Tage zurück |
| Gelb | `last_touch` liegt 30 bis 60 Tage zurück |
| Beobachten | `last_touch` liegt weniger als 30 Tage zurück, aber die jüngste Quelle ist ausschließlich "passiv" (kein Call, Meeting, Ticket oder Kontakt-Touch war jüngst der aktivste). Das fängt Kunden ab, deren scheinbares Engagement nur automatisches Tracking ist, kein echter menschlicher Kontakt. |

### Renewal-Filter (seit 19.08.2026, auf Wunsch Moritz)

Nur Kunden mit `contract_end_date` in höchstens 6 Monaten (183 Tage), bereits überschrittenem Vertragsende, oder ganz ohne `contract_end_date` werden im Hauptbild gezeigt. Kunden mit Aktivitätsrisiko, deren Renewal mehr als 6 Monate entfernt liegt, werden nicht stillschweigend fallen gelassen, sondern in einem eigenen Block "Ausgeblendet" mit Summe und Einzelposten aufgeführt, damit die Auslassung nachvollziehbar bleibt.

Report-Struktur (drei Blöcke plus Methodik plus Datenqualität):

1. Aktivitätsrisiko mit Renewal im 6-Monats-Fenster (oder bereits überfällig): Hauptblock, sortiert nach MRR.
2. Aktivitätsrisiko ohne Vertragsdatum: Renewal-Dringlichkeit nicht berechenbar, eigener Block statt in Block 1 vermischt.
3. Ausgeblendet: Renewal mehr als 6 Monate entfernt. Transparenz-Block, kein Handlungsdruck.

### Slack-Benachrichtigung

Nach jedem Lauf eine Nachricht an `#customer-experience` (Channel-ID `C04DAC5AVK9`) mit Kurzfassung (Stufen, Kunden- und MRR-Zahlen je Stufe, die 2 bis 3 auffälligsten Einzelfälle) und Link auf die neue Notion-Unterseite. Erwähnung folgender Personen:

- Bettina Fischer: `<@U01S6546SGM>`
- Leonard Diemer: `<@U03C9DGGDCY>`
- Moritz Lienert: `<@U071B33N4LQ>`

### Änderungshistorie

- **19.08.2026:** Erstfassung nach Korrektur eines Lauf-1-Fehlers (nur COMPANY-Ebene, `createdate` statt Ticket-Aktivität). Von 39 zuvor gemeldeten Kunden blieben nach Fix und 6-Monats-Filter 15 übrig. Cadence von wöchentlich auf monatlich geändert (Wunsch Moritz). Slack-Versand und 6-Monats-Renewal-Filter neu eingeführt.

## Routine 2: Tickets

Noch nicht spezifiziert (Status in CS-Reports: offen). Laut Notion-Übersicht: Trend und Aging-Liste aus der Support-Pipeline, Cadence wöchentlich. Bevor implementiert wird: klären, ob dieselbe Ticket-Aktivitäts-Definition wie in Routine 1 (siehe oben) wiederverwendet werden kann, statt sie zweimal getrennt zu pflegen.

## Routine 3: Renewals

Läuft bereits (erster Report 12.08.2026), war aber vor diesem Eintrag nirgends im Repo festgehalten. Aus dem existierenden Notion-Report rekonstruiert:

- **Fenster:** 90 Tage bis Vertragsende, angenommene Kündigungsfrist 3 Monate zum Laufzeitende (noch nicht verbindlich bestätigt, siehe offener Punkt in CS-Reports).
- **Blöcke:** (1) Vertragsende im 90-Tage-Fenster, (2) Kündigungsfrist läuft im Fenster ab, obwohl Vertragsende dahinter liegt (der eigentlich operativ nutzbare Block, weil die Entscheidung vor dem Fristablauf fällt), (3) abgelaufene Vertragsdaten bei aktiven Kunden (`contract_end_date` in der Vergangenheit, aber `churn_date` leer), (4) aktive Kunden ganz ohne Vertragsdatum, (5) Gegenprobe über offene Deals auf den gelisteten Kunden.
- **Bekannter Fund (19.08.2026, aus Routine 1):** die Spalte "Letzte Aktivität" nutzt aktuell nur COMPANY-Ebene (dieselbe Lücke, die Routine 1 vor der Korrektur hatte). Beispiel Securitas Suomi zeigte im Report vom 12.08. "03.11.2025 (282 T)" statt der tatsächlichen 100 Tage (Kontakt-Touch vom 11.05.2026). Sollte um die Kontakt-Touch-Quelle aus Routine 1 erweitert werden.

## Offene CRM-Themen (siehe auch Notion-Checkliste)

Diese begrenzen den Wert aller drei Routinen unabhängig von der Implementierung:

- `contract_end_date` für Kunden ohne gültiges Datum nachpflegen.
- Owner-Zuordnung der Deals nachziehen (36 der 40 offenen Deals an aktiven Kunden liefen zuletzt auf inaktive Owner).
- Aktive Kunden ohne Owner zuordnen.
- Companies mit `lifecyclestage = customer` und gesetztem `churn_date` auf einen eigenen Lifecycle-Wert setzen.
- Dubletten bereinigen (siehe Liste oben).
- `lifecyclestage` von d.velop korrigieren.
- Standard-Kündigungsfrist verbindlich klären.
- Routine 3 um Kontakt-Ebene erweitern (siehe oben).
