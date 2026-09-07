# Support-Ticket-Kennzahlen: Median-Report, Stand 2026-09-07

Leitkennzahl ist der Median der Time to Close, nicht der Durchschnitt. Begründung:
die Verteilung ist rechtsschief, weil einzelne Tickets monatelang offen liegen und
den Mittelwert um den Faktor 15 bis 20 verzerren. Beide Werte gehören ins Dashboard,
aber der Median gehört nach vorn.

Filter zwingend: `hs_pipeline = '0'` (Support-Pipeline). Onboarding, Punchout und
Feature Requests haben andere Laufzeitlogiken und würden die Zahl unbrauchbar machen.

Umrechnung: HubSpot liefert `time_to_close` und `time_to_first_agent_reply` in
Millisekunden. Geteilt durch 3.600.000 für Stunden, durch 86.400.000 für Tage.

---

## 1. Monatlicher Trend (geschlossene Tickets, Pipeline Support)

| Monat 2026 | Geschlossen | Ø Time to Close | Median Time to Close | Ø First Reply | Median First Reply |
|---|---|---|---|---|---|
| Januar | 130 | 19,1 Tage | 1,8 Tage | 2,0 Tage | 1,9 Std. |
| Februar | 136 | 31,4 Tage | 7,7 Tage | 2,7 Tage | 2,0 Std. |
| März | 165 | 21,6 Tage | 2,1 Tage | 4,0 Tage | 3,5 Std. |
| April | 142 | 12,7 Tage | 1,0 Tage | 0,5 Tage | 1,4 Std. |
| Mai | 161 | 9,3 Tage | 1,0 Tage | 2,3 Tage | 7,4 Std. |
| Juni | 115 | 5,5 Tage | 9,4 Std. | 0,9 Tage | 3,9 Std. |
| Juli | 165 | 17,1 Tage | 1,0 Tage | 2,0 Tage | 22,9 Std. |
| **August (vollständig)** | **431** | **66,8 Tage** | **42,8 Tage** | 2,2 Tage | 6,8 Std. |
| September (bis 07.09.) | 39 | 0,9 Tage | 1,0 Tage | 0,4 Tage | 3,9 Std. |

**Abweichung von der bisherigen Annahme:** Der ursprüngliche Referenzwert für August
("bis 12.": 54 geschlossen, Ø 2,9 Tage, Median 21,3 Std.) war ein Teilmonat. Der
vollständige August zeigt ein anderes Bild: 431 statt 54 Geschlossene, Median 42,8
Tage statt 21,3 Stunden. Das ist ein Ausreißer weit außerhalb aller anderen Monate,
in denen der Median nie über 7,7 Tage lag. Wahrscheinlichste Erklärung: eine
Aufräumaktion, die im August viele alte, lange offene Tickets gebündelt geschlossen
hat. Das erhöht sowohl die Zahl der Abschlüsse als auch deren Laufzeit gleichzeitig.
Sollte gegen das CS-Team verifiziert werden, ist aber keine Datenanomalie: die
Rohwerte wurden direkt per SQL-Query gegen `TICKET` gezogen.

September (bis 07.09., 39 Tickets) liegt wieder im Normalbereich wie April bis Juli.

---

## 2. Offener Bestand nach Stage (Pipeline Support, Stand 2026-09-07)

| Stage | Anzahl |
|---|---|
| Neu | 17 |
| Warten auf Kontakt | 85 |
| Wartet auf uns | 166 |
| Geschlossen | 2.671 |
| **Gesamt** | **2.940** |

"Wartet auf uns" ist die eigentliche CS-Kennzahl: hier liegt die Verantwortung
für die nächste Aktion bei uns, nicht beim Kunden.

## 3. Aging-Liste: "Wartet auf uns" seit über 14 Tagen (Stichtag 2026-08-24)

**161 von 166** Tickets in "Wartet auf uns" sind älter als 14 Tage (97 %). Die
ältesten 35 (von 161, sortiert nach `createdate` aufsteigend):

| Erstellt | Ticket-ID | Betreff | Firma |
|---|---|---|---|
| 2025-09-08 | 222980445411 | Priorität Urgent - Rechnungen... | Hydrogenious LOHC Technologies |
| 2025-09-12 | 225118684355 | Ticket HT - High - Wiederkehrende Kosten... | Hydrogenious LOHC Technologies |
| 2025-10-14 | 251383690479 | Ticket HT - Mittel | Hydrogenious LOHC Technologies |
| 2025-10-27 | 265115578557 | Liste aller Rechnungen zur Übersicht | Hydrogenious LOHC Technologies |
| 2025-10-28 | 266395998447 | Wareneingang in Hivebuy | Hivebuy |
| 2025-10-30 | 269724592322 | Buchhaltungstab: Filter für Rechnung | DaVita Deutschland AG |
| 2025-11-10 | 286039366898 | AW: [EXTERN] Re: Ticket HT -Urgent | Hydrogenious LOHC Technologies |
| 2025-11-20 | 297064530123 | Ticket HT – Priorität Low... | Hydrogenious LOHC Technologies |
| 2025-12-02 | 313078728892 | Automatisierter PO Name | STAUB & CO. / Tabel Group |
| 2025-12-02 | 312262597868 | Rückmeldung zum Termin 2.12.25 | Nfon AG |
| 2025-12-03 | 313674035392 | Fwd: ext: Re: ext: Re: Übernahme Angebote | Hamberger Industriewerke GmbH |
| 2025-12-05 | 314049401021 | Ticket HT – Priorität Low - Anforderer... | Hydrogenious LOHC Technologies |
| 2025-12-12 | 322787762406 | Ticket Nr. 322787762406 | Tabel Group |
| 2025-12-12 | 322796768456 | Fwd: Zahlungsbedigungen -> Info von DATEV | Hydrogenious LOHC Technologies |
| 2025-12-16 | 327019109588 | WG: [External] ... Ticket geschlossen | Hivebuy |
| 2025-12-29 | 334898688237 | Kontierungsänderungen sichtbar machen | A.S. Création Tapeten |
| 2026-01-05 | 336509437133 | Mittel - Varianten müssen separat aktiviert werden | Securitas Deutschland |
| 2026-01-09 | 344933740736 | Ticket HT – Priorität Urgent... | Hydrogenious LOHC Technologies |
| 2026-01-12 | 347530354880 | offene Anfrage | LGI |
| 2026-01-13 | 349417913579 | Budget Owners Cannot See Budgets... | Oberlinhaus |
| 2026-01-14 | 351732272314 | Total Budget Not Summed for Parent Categories | Oxyle |
| 2026-01-14 | 352038708426 | Medium - Bestellstatus und Email... | Securitas Deutschland |
| 2026-01-22 | 360677864655 | Re: Uvex - Kosten... | Hivebuy |
| 2026-01-22 | 358667320550 | Add field "Delivery Recipient"... | Mathias Wiemann GmbH & Co. KG |
| 2026-01-23 | 361581015232 | AW: [External] ... Ticket geschlossen | Securitas Deutschland |
| 2026-01-26 | 366329720034 | Improve purchase request search capabilities | Tabel Group |
| 2026-01-29 | 369140643028 | WG: [External] Genehmigt zum Einkauf... | Hivebuy |
| 2026-01-30 | 370403544253 | Blend out Login option with Username/PW | Securitas Deutschland |
| 2026-02-05 | 376058157243 | "Legal Entity" nicht gefüllt... | LGI |
| 2026-02-05 | 376253487296 | WG: Fleecejacken mit speziellem Aviation Logo | Securitas Deutschland |
| 2026-02-10 | 382123959499 | Fwd: Tempworker Samson Personal Team GmbH... | rebuy |
| 2026-02-17 | 388237057211 | Anfrage Nutzer Rolle - Wareneingang/Lager | Oberlinhaus |
| 2026-02-23 | 393221832909 | Info wenn Bestellung komplett | AUMÜLLER AUMATIC GmbH |
| 2026-02-26 | 395705943271 | Integrierte Lieferanten | GWK GmbH - Arbeiten + Wohnen |
| 2026-02-26 | 395583987954 | Änderungswunsch HiveBuy – Excel-Download... | Borussia Dortmund |

Rest (126 weitere Tickets, jüngste davon vom 2026-08-21) nicht im Detail aufgeführt,
aber in der Gesamtzahl (161) enthalten. Auffällig: fünf Tickets von Hydrogenious LOHC
Technologies sind über 300 Tage alt (älteste vom 2025-09-08, seit fast einem Jahr
unbeantwortet in "Wartet auf uns").

---

## 4. CSAT / NPS (ergänzend, aktuell kaum gepflegt)

| Property | Befüllt | von | Anteil |
|---|---|---|---|
| `hs_last_csat_rating` | 140 | 2.940 | 4,8 % |
| `hs_feedback_last_nps_rating_number` | 0 | 2.940 | 0 % |

CSAT wird kaum erhoben, NPS gar nicht. Sobald CSAT künftig systematisch erfasst wird,
gehört es in denselben Report.

---

## Cadence

Monatlicher Trend (Abschnitt 1) und wöchentliche Aging-Liste (Abschnitt 3) laufen
als wiederkehrende Routine. Datenquelle: HubSpot `TICKET`-Objekt, live per SQL-Query
(`hs_pipeline = '0'`), keine manuelle Pflege nötig außer für CSAT/NPS.
