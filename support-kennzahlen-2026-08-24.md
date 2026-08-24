# Support-Kennzahlen, Stand 24.08.2026

Pipeline: `hs_pipeline = '0'` (Support). Onboarding, Punchout und Feature Requests sind ausgeschlossen.
Leitkennzahl ist der Median, der Durchschnitt steht daneben als Ausreisser-Indikator.

## Befund: Massenschliessung am 13.08.2026 verfaelscht die August-Zahl

Am 13.08. wurden an einem Tag **269 Tickets** geschlossen, Median Time to Close **95,3 Tage**.
Zum Vergleich: an allen anderen Augusttagen liegen die Abschluesse zwischen 0 und 17 pro Tag.

Damit ist die August-Zeile als Trendwert unbrauchbar:

| August | Geschlossen | Median TTC | Ø TTC |
|---|---|---|---|
| gesamt (1.–24.08.) | 383 | 56,3 Tage | 75,2 Tage |
| davon 13.08. allein | 269 | 95,3 Tage | – |
| ohne 13.08. (14.–24.08.) | 55 | **5,8 Std.** | 1,5 Tage |

Das Tagesgeschaeft im August ist also so schnell wie nie gemessen (5,8 Std. Median).
Wer die August-Zeile ungefiltert ins Dashboard nimmt, meldet einen Einbruch, den es nicht gab.
**Empfehlung: den 13.08. im Monatstrend als Bereinigungsereignis annotieren oder ausschliessen.**

## Monatstrend 2026

| Monat | Geschlossen | Median TTC | Ø TTC | Median First Reply | Ø First Reply |
|---|---|---|---|---|---|
| Januar | 130 | 1,8 Tage | 19,1 Tage | 2,0 Std. | 2,0 Tage |
| Februar | 136 | 7,7 Tage | 31,4 Tage | 2,0 Std. | 2,7 Tage |
| Maerz | 165 | 2,1 Tage | 21,6 Tage | 3,5 Std. | 4,0 Tage |
| April | 142 | 1,0 Tage | 12,7 Tage | 1,4 Std. | 11,6 Std. |
| Mai | 161 | 1,0 Tage | 9,3 Tage | 7,4 Std. | 2,3 Tage |
| Juni | 115 | 9,4 Std. | 5,5 Tage | 3,9 Std. | 22,8 Std. |
| Juli | 165 | 1,0 Tage | 17,1 Tage | 22,9 Std. | 2,0 Tage |
| August (bereinigt) | 55 | 5,8 Std. | 1,5 Tage | 6,8 Std. | – |
| August (roh, inkl. 13.08.) | 383 | 56,3 Tage | 75,2 Tage | 7,3 Std. | 2,4 Tage |

Januar bis Juli decken sich exakt mit der Definition, die Query ist damit validiert.

## Offener Bestand

| Stage | Definition (12.08.) | jetzt (24.08.) | Delta |
|---|---|---|---|
| Neu | 21 | 1 | −20 |
| Warten auf Kontakt | 299 | 70 | −229 |
| **Wartet auf uns** | **151** | **161** | **+10** |
| Geschlossen | 2.255 | 2.584 | +329 |

Die Bereinigung hat die Warteschlange auf Kundenseite geleert. Die eigentliche CS-Kennzahl,
"Wartet auf uns", ist im selben Zeitraum **gewachsen**. Der Rueckstand wurde nicht abgebaut,
sondern nur der Teil weggeraeumt, der ohnehin nicht bei uns lag.

## Aging-Liste: Tickets in "Wartet auf uns", aelter als 14 Tage

**152 von 161 Tickets (94 %)** in "Wartet auf uns" liegen laenger als 14 Tage bei uns.
Median-Alter: **117 Tage**. Aeltestes Ticket: 350 Tage.

| Altersklasse | Anzahl |
|---|---|
| 180–364 Tage | 33 |
| 90–179 Tage | 56 |
| 30–89 Tage | 56 |
| 14–29 Tage | 7 |

Kein Ticket ist aelter als ein Jahr, weil die aeltesten inzwischen 350 Tage erreicht haben.
Ohne Eingriff wandern die ersten im September ueber die Jahresgrenze.

### Verteilung nach Kunde

| Anzahl | Unternehmen |
|---|---|
| 21 | rebuy |
| 15 | Hydrogenious LOHC |
| 13 | Securitas Deutschland |
| 11 | Hivebuy (intern) |
| 10 | Oberlinhaus |
| 8 | Borussia Dortmund |
| 7 | A.S. Création Tapeten |
| 7 | LGI |
| 6 | Nfon AG |
| 6 | Unassigned |
| 5 | PIMA Health Group |

Fuenf Kunden halten 70 der 152 Tickets. Ein gezielter Durchgang pro Kunde ist wirksamer
als eine Abarbeitung nach Alter.

### Die zehn aeltesten

| Alter | Erstellt | Unternehmen | Betreff |
|---|---|---|---|
| 350 d | 2025-09-08 | Hydrogenious LOHC | Priorität Urgent – Rechnungen als Neu hinterlegt, keine Vorschau |
| 346 d | 2025-09-12 | Hydrogenious LOHC | Ticket HT – High – Wiederkehrende Kosten "Von" Datum einfügen |
| 314 d | 2025-10-14 | Hydrogenious LOHC | Ticket HT – Mittel |
| 301 d | 2025-10-27 | Hydrogenious LOHC | Liste aller Rechnungen zur Übersicht |
| 300 d | 2025-10-28 | Hivebuy | Wareneingang in Hivebuy |
| 298 d | 2025-10-30 | DaVita Deutschland AG | Buchhaltungstab: Filter für Rechnung |
| 287 d | 2025-11-10 | Hydrogenious LOHC | AW: [EXTERN] Re: Ticket HT – Urgent |
| 277 d | 2025-11-20 | Hydrogenious LOHC | Ticket HT – Low – Rechnungsbetrag wird nicht dagegengerechnet |
| 265 d | 2025-12-02 | STAUB & CO. – SILBERMANN | Automatisierter PO Name |
| 265 d | 2025-12-02 | Nfon AG | Rückmeldung zum Termin 2.12.25 |

Vollstaendige Liste inklusive HubSpot-Links: `support-aging-2026-08-24.csv`

## Nicht gepflegt

`hs_last_csat_rating` und `hs_feedback_last_nps_rating_number` sind weiterhin leer.
Sobald CSAT erhoben wird, gehoert es in dieselbe Routine.

## Queries

Monatstrend:

```sql
SELECT DATE_TRUNC(closed_date, 'MONTH'),
       COUNT(*),
       MEDIAN(time_to_close),
       AVG(time_to_close),
       MEDIAN(time_to_first_agent_reply),
       AVG(time_to_first_agent_reply)
FROM TICKET
WHERE hs_pipeline = '0'
  AND closed_date BETWEEN '2026-01-01' AND '2026-08-24'
GROUP BY DATE_TRUNC(closed_date, 'MONTH')
```

Aging-Liste:

```sql
SELECT hs_object_id, subject, createdate, hs_pipeline_stage, COMPANY.name
FROM TICKET
WHERE hs_pipeline = '0'
  AND hs_pipeline_stage = '3'
  AND createdate < '2026-08-10'
ORDER BY createdate ASC
```

Millisekunden: `/ 3.600.000` fuer Stunden, `/ 86.400.000` fuer Tage.

Hinweis zur Aging-Query: Tickets mit mehreren zugeordneten Unternehmen kommen mehrfach
zurueck (155 Zeilen, 152 eindeutige `hs_object_id`). Vor dem Zaehlen nach `hs_object_id`
deduplizieren.

Tagesaufloesung zur Erkennung von Bereinigungsereignissen:

```sql
SELECT DATE_TRUNC(closed_date, 'DAY'), COUNT(*), MEDIAN(time_to_close)
FROM TICKET
WHERE hs_pipeline = '0' AND closed_date BETWEEN '{monatsanfang}' AND '{today}'
GROUP BY DATE_TRUNC(closed_date, 'DAY')
ORDER BY DATE_TRUNC(closed_date, 'DAY') ASC
```
