# LinkedIn Paid Campaign Analyse: Hivebuy

**Datenstand:** 15.07.2026 | **Zeitraum:** Feb 2022 – Jul 2026 | **Währung:** EUR
**Quelle:** LinkedIn Marketing API (adAnalytics, pivot=CAMPAIGN), Account `509511309`
**Datenbasis:** 215 Kampagnen mit Auslieferung (von 224 gesamt); die 3 weiteren Ad-Accounts sind leer/ruhend.

> Rohdaten liegen in `data/` (nicht eingecheckt). Reproduzierbar über `./fetch_linkedin_data.sh`.

---

## 1. Gesamtbild

| Kennzahl | Wert |
|---|---:|
| Gesamt-Spend | **€162.623** |
| Impressions | 3.637.003 |
| Clicks | 19.384 |
| Leads (LinkedIn Lead-Gen-Formulare) | 845 |
| Website-Conversions | 2.087 |
| Ø CTR | 0,53 % |
| Ø CPC | €8,39 |
| Ø CPM | €44,71 |
| Blended CPL (Lead-Gen-Kampagnen) | €137 |
| Blended CPA (Website-Conversions) | €78 |

Alle Kampagnen sind Sponsored Content (Single Image / Carousel / Video). CTR und CPM liegen im typischen DACH-B2B-Rahmen für LinkedIn. Das eigentliche Thema liegt nicht bei den Durchschnittswerten, sondern bei der **Entwicklung über die Zeit** und der **starken Fragmentierung**.

---

## 2. Der zentrale Befund: Effizienz ist seit 2022 stark gesunken

CPL der Lead-Gen-Kampagnen, spend-gewichtet pro Jahr:

| Jahr | Spend | Leads | CPL |
|---|---:|---:|---:|
| **2022** | €94.849 | 675 | **€141** |
| 2023 | €12.944 | 14 | €925 |
| 2024 | €25.685 | 114 | €225 |
| 2025 | €13.698 | 22 | €623 |
| 2026 (bis Jul) | €15.448 | 20 | €772 |

**2022 war das effizienteste Jahr** und trug 80 % aller Leads (675 von 845) bei nur ~58 % des Spends. Danach ist die Lead-Ausbeute eingebrochen: 2025/26 kostet ein Lead das 4- bis 5-fache. Gleichzeitig wurde das Budget von ~€10–15k/Monat (2022) auf oft €1–3k/Monat zersplittert.

**Interpretation:** Es wurde von einem bewährten, eng getargeteten Lead-Gen-Setup auf viele kleine, breitere und teils Top-of-Funnel-Experimente umgestellt. Die neuen Kampagnen sammeln zu wenig Volumen, um zu lernen.

---

## 3. Performance nach Kampagnenziel

| Ziel | Kampagnen | Spend | CTR | CPC | Leads | Conv. | CPL | CPA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LEAD_GENERATION | 162 | €116.128 | 0,49 % | €11,34 | 845 | 353 | **€137** | €329 |
| WEBSITE_VISIT | 21 | €16.231 | 0,46 % | €8,24 | – | 591 | – | €27 |
| ENGAGEMENT | 11 | €9.605 | **1,20 %** | €5,83 | – | 190 | – | €51 |
| VIDEO_VIEW | 4 | €7.412 | 0,20 % | €16,22 | – | 64 | – | €116 |
| BRAND_AWARENESS | 8 | €7.267 | 0,64 % | **€1,88** | – | 108 | – | €67 |
| WEBSITE_CONVERSION | 9 | €5.977 | 0,79 % | €5,00 | – | 781 | – | **€8** |

**Ableitungen:**
- **WEBSITE_CONVERSION** ist mit **€8 CPA extrem günstig** und stark untergewichtet (nur €6k / 4 % des Spends). Hier steckt das beste Verhältnis von Kosten zu Ergebnis.
- **Retargeting (WEBSITE_VISIT)** liefert Conversions zu €27 – ebenfalls effizient.
- **VIDEO_VIEW** als eigenständiges Ziel ist der teuerste Kanal: €16 CPC, 0,2 % CTR. Video funktioniert aber *innerhalb* von Retargeting (siehe unten).
- **ENGAGEMENT** hat die höchste CTR (1,2 %) – die Creatives/Botschaften finden Resonanz.

---

## 4. Was funktioniert (Skalieren)

### 4a. Enges Job-Targeting im Lead-Gen (das 2022er-Rezept)
Die besten Lead-Gen-Kampagnen kombinierten **Jobfunktion (Einkauf/Beschaffung, Finance) + Seniorität + Unternehmensgröße** mit Single Image + Lead-Formular:

| CPL | Spend | Leads | Kampagne |
|---:|---:|---:|---|
| €33 | €632 | 19 | `DE | Int+Skills, JF Finance/Purchasing/BD/Operations` |
| €52 | €3.736 | 72 | `DE | TITEL Einkauf/Beschaffung + SIZE | Freigabericht.` |
| €74 | €1.697 | 23 | `DE | GROUPS + SEN + SIZE | IMAGE | ENG` |
| €80 | €4.613 | 58 | `DE | TITEL Einkauf/Beschaffung + SIZE | IMAGE | ENG` |
| €85 | €4.252 | 50 | `DE | EINKAUF | FUNC + SEN + SIZE | IMAGE` |

Diese lagen bei **€33–88 CPL** – gegenüber €137 blended und €600–900 in 2025/26. Das ist die klare Blaupause.

### 4b. Die „ProcurementHeroes"-Serie (Creative-Gewinner)
| Kampagne | CTR | Spend | Status |
|---|---:|---:|---|
| `0526_ProcurementHeroes` | **2,96 %** | €2.338 | AKTIV |
| `0326_ProcurementHeroes` | 2,69 % | €628 | pausiert |
| `0126_ProcurementHeroes` | 1,39 % | €578 | pausiert |

CTR von 1,4–3,0 % = **3- bis 6-fach über dem Account-Schnitt (0,53 %)**. Dieses Creative-/Botschaftskonzept resoniert deutlich – aber es läuft nur auf Brand-Awareness und wird nicht in Leads/Conversions überführt.

---

## 5. Was Budget verbrennt (Stoppen/Umbauen)

- **Aktive Lead-Gen-Kampagne `0426_TOF_KI-Chatbot`**: €976 Spend, **2 Leads → €488 CPL** auf kalter Top-of-Funnel-Zielgruppe. Lead-Formular auf kaltem TOF-Publikum ist strukturell teuer.
- **Breite „Generic"-Kampagnen** (`LeadGen_..._Generic`, `LeadGen_1405_Handel`): €390–966 CPL. Ohne enges Targeting kein effizienter Lead.
- **Reines Retargeting-Lead-Gen** (`0724_Retargeting`, €389 CPL): Zielgruppe zu klein für Formular-Volumen.
- **VIDEO_VIEW als Ziel** (€7,4k, €16 CPC): als eigenständiges Ziel ineffizient.
- **Zersplitterung:** **119 von 215 Kampagnen haben < €500 ausgegeben**, 32 sogar < €100. Nur 19 Kampagnen (≥ €2k) machen 43 % des Spends aus. Zu viele Mini-Kampagnen kommen nie aus der LinkedIn-Lernphase heraus.

---

## 6. Aktueller Live-Zustand (8 aktive Kampagnen)

| Kampagne | Ziel | Spend | Conv | Leads | CTR |
|---|---|---:|---:|---:|---:|
| 2026_Retargeting_Video | WEBSITE_VISIT | €3.504 | 73 | 0 | 0,56 % |
| 0526_ProcurementHeroes | BRAND_AWARENESS | €2.338 | 31 | 0 | 2,96 % |
| 2026_Retargeting_Single_Image | WEBSITE_VISIT | €2.090 | 77 | 0 | 0,39 % |
| 0426_TOF_KI-Chatbot | LEAD_GENERATION | €976 | 0 | 2 | 0,32 % |
| 2026_TOF_Einkauf_Carousel | BRAND_AWARENESS | €970 | 19 | 0 | 0,43 % |
| 0626_ProcurementHeroes | BRAND_AWARENESS | €308 | 0 | 0 | 1,06 % |
| 2026_Retargeting_Video_Leadfeeder | WEBSITE_VISIT | €278 | 4 | 0 | 0,20 % |
| ProcureConnect HH | LEAD_GENERATION | €191 | 2 | 2 | 1,32 % |

Die aktuelle Struktur ist im Kern gesund: **TOF (Brand) → Retargeting (Conversions)**. Zwei Lücken:
1. Die einzige nennenswerte Lead-Gen-Kampagne (KI-Chatbot) ist mit €488 CPL ineffizient.
2. Der Creative-Gewinner (ProcurementHeroes) wird nicht in eine Lead-/Conversion-Ebene überführt.

---

## 7. Empfehlungen (priorisiert)

**Sofort (diese Woche)**
1. **`0426_TOF_KI-Chatbot` pausieren oder umbauen.** €488 CPL auf kaltem TOF. Entweder auf eine warme Retargeting-Zielgruppe umziehen oder das Ziel auf WEBSITE_CONVERSION wechseln (das günstigste Format im Account, €8 CPA).
2. **ProcurementHeroes in den Funnel verlängern.** Aus den Engagern/Videobetrachtern von ProcurementHeroes eine Retargeting-Audience bauen und mit WEBSITE_CONVERSION- bzw. Lead-Gen-Ebene bespielen. Das beste Creative trifft aktuell nur die oberste Funnel-Stufe.

**Kurzfristig (2–4 Wochen)**
3. **Lead-Gen nach dem 2022-Rezept neu aufsetzen.** Enges Targeting: Jobfunktion (Einkauf/Beschaffung, Finance) + Seniorität + Unternehmensgröße, Single Image + Lead-Formular. Ziel-CPL €50–90 (nachweislich erreicht). „Generic"/breite Zielgruppen vermeiden.
4. **WEBSITE_CONVERSION hochskalieren.** Mit €8 CPA und nur 4 % des Spends klar unterinvestiert. Budget von den teuren Lead-Gen-Experimenten hierher verschieben.
5. **Budget konzentrieren statt zersplittern.** Auf 4–6 gut finanzierte Kampagnen bündeln (Richtwert ≥ €2k Laufzeit-Budget bzw. genug Tagesbudget für die Lernphase), statt vieler Mini-Kampagnen mit < €500.

**Strukturell**
6. **VIDEO_VIEW-Ziel einstellen**, Video weiter *innerhalb* von Retargeting nutzen (dort €48 CPA statt €116).
7. **Retargeting-Pools konsolidieren.** Splitter wie `Retargeting_Video_Leadfeeder` (4 Clicks, €278) sind zu klein – zu größeren Audiences zusammenfassen, um Frequenz-/Lernprobleme zu vermeiden.
8. **Budget-Niveau prüfen.** Wenn Lead-Gen wieder ein Ziel ist, ist das aktuelle Niveau (~€1–3k/Monat, breit gestreut) zu dünn für stabile Ergebnisse. 2022 lieferte Effizienz bei fokussierten €8–12k/Monat.

**Klarer roter Faden:** Zurück zu *engem Job-Targeting im Lead-Gen* + *mehr Budget auf die günstige WEBSITE_CONVERSION-Ebene* + *das ProcurementHeroes-Creative bis in Leads/Conversions durchziehen* – und weg von vielen kleinen, breiten TOF-Experimenten.

---

## Methodik & Grenzen
- Metriken direkt aus `adAnalytics` (LinkedIn Marketing API, Version 202506), Lifetime pro Kampagne + monatliche Granularität, Fenster ~Jan 2021–Jul 2026.
- „Leads" = `oneClickLeads` (LinkedIn-Lead-Gen-Formulare). „Conversions" = `externalWebsiteConversions` (abhängig vom Insight-Tag; frühe Zeiträume ggf. untererfasst).
- CPL/CPA nur dort ausgewiesen, wo Leads/Conversions > 0.
- Spend = `costInLocalCurrency` (EUR). Multi-Touch-/View-Through-Effekte über Kanäle hinweg sind nicht enthalten.
