# Support-Ticket-Kennzahlen: Lauf vom 2026-08-31

Erste Ausführung der monatlichen Trend-Routine und der wöchentlichen Aging-Liste
gemäß Definition. Query direkt gegen HubSpot (`hs_pipeline = '0'`, Support Pipeline).

---

## 1. Monatstrend Januar bis Juli 2026: Werte bestätigt

Die per Query ermittelten Werte für Januar bis Juli decken sich exakt mit den in der
Definition genannten Zahlen. Die Methodik (Median vor Durchschnitt) ist damit verifiziert.

| Monat 2026 | Geschlossen | Median Time to Close | Ø Time to Close |
|---|---|---|---|
| Januar | 130 | 1,8 Tage | 19,1 Tage |
| Februar | 136 | 7,7 Tage | 31,4 Tage |
| März | 165 | 2,1 Tage | 21,6 Tage |
| April | 142 | 1,0 Tage | 12,7 Tage |
| Mai | 161 | 1,0 Tage | 9,3 Tage |
| Juni | 115 | 9,4 Stunden | 5,5 Tage |
| Juli | 165 | 1,0 Tage | 17,1 Tage |

## 2. August 2026 komplett: eine Auffälligkeit

Mit dem vollständigen Monat (statt Stand 12.8.) kippt das Bild:

| Zeitraum | Geschlossen | Median Time to Close | Ø Time to Close |
|---|---|---|---|
| August, Stand 12.8. (aus Definition) | 54 | 21,3 Stunden | 2,9 Tage |
| **August, komplett (1. bis 31.8.)** | **419** | **45,0 Tage** | **68,7 Tage** |

Das ist keine allmähliche Verschlechterung, sondern ein einzelner Tag. Aufschlüsselung
nach Schließdatum zeigt einen isolierten Ausreißer:

| Datum | Geschlossen | Median Time to Close | Ø Time to Close |
|---|---|---|---|
| 12.08. | 7 | 1,0 Tage | 1,8 Tage |
| **13.08.** | **269** | **93,8 Tage** | **106,2 Tage** |
| 14.08. | 8 | 0,1 Tage | 3,2 Tage |

Am 13. August wurden 269 Tickets auf einmal geschlossen, mit einer typischen Laufzeit
von gut drei Monaten. Das sieht nach einer gezielten Bulk-Aktion aus (Aufräumen alter
Bestände), nicht nach organischem Tagesgeschäft. Für den Trend-Report bedeutet das:

- Ohne Herausrechnen dieses einen Tages ist die August-Zahl für Median und Durchschnitt
  unbrauchbar, und zwar für beide Kennzahlen, nicht nur für den Durchschnitt. Der Median
  ist gegen viele kleine Ausreißer robust, aber nicht gegen einen Tag, an dem über 60 %
  des Monatsvolumens auf einmal fällt.
- Empfehlung: Bulk-Schließungen als eigene Kategorie taggen oder aus der Time-to-Close-
  Kennzahl herausfiltern, sonst verzerrt jede künftige Aufräumaktion den Monat, in dem
  sie stattfindet.

## 3. Bestand der Support-Pipeline, aktueller Stand

| Stage | Definition (Stand offen) | Jetzt (31.8.) | Differenz |
|---|---|---|---|
| Neu | 21 | 7 | -14 |
| Warten auf Kontakt | 299 | 79 | -220 |
| Wartet auf uns | 151 | 165 | +14 |
| Geschlossen | 2.255 | 2.620 | +365 |

Der Rückgang bei "Warten auf Kontakt" und "Neu" bei gleichzeitigem Sprung bei
"Geschlossen" passt zur Bulk-Schließung vom 13.8.: der Aufräumdurchgang traf offenbar
überwiegend alte Tickets in diesen beiden Stufen. "Wartet auf uns" (die eigentliche
CS-Kennzahl) ist von der Aktion unberührt geblieben und sogar leicht gestiegen.

## 4. Aging-Liste: "Wartet auf uns" seit über 14 Tagen

159 von 165 Tickets in "Wartet auf uns" sind älter als 14 Tage, das sind 96 % des
Bestands in dieser Stage. Vollständige Liste: `aging-wartet-auf-uns-2026-08-31.csv`.

Älteste offene Fälle:

| Ticket-ID | Betreff | Erstellt | Unternehmen |
|---|---|---|---|
| 222980445411 | Priorität Urgent - Rechnungen werden in Hivebuy zwar als Neu hinterlegt, aber es wird nichts in der Vorschau angezeigt | 2025-09-08 | Hydrogenious LOHC Technologies |
| 225118684355 | Ticket HT - High - Wiederkehrende Kosten "Von" Datum einfügen! | 2025-09-12 | Hydrogenious LOHC Technologies |
| 251383690479 | Ticket HT - Mittel | 2025-10-14 | Hydrogenious LOHC Technologies |
| 265115578557 | Liste aller Rechnungen zur Übersicht | 2025-10-27 | Hydrogenious LOHC Technologies |
| 266395998447 | Wareneingang in Hivebuy | 2025-10-28 | Hivebuy |

Der älteste Fall liegt seit fast 12 Monaten bei uns, mit der Priorität "Urgent". Sieben
der ältesten Fälle in der Liste gehören zu Hydrogenious LOHC Technologies, das Konto ist
im Aging-Bestand deutlich überrepräsentiert.

## 5. CSAT / NPS

`hs_last_csat_rating` und `hs_feedback_last_nps_rating_number` liefern aktuell keine
Werte, wie in der Definition vermerkt. Kein Änderungsbedarf an der Routine, bis die
Erhebung startet.

---

*Cadence: Monatlicher Trend (Abschnitt 1-3) und wöchentliche Aging-Liste (Abschnitt 4)
laut Definition. Nächster Lauf der Aging-Liste in 7 Tagen.*
