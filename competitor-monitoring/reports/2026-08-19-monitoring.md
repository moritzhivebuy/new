# Wettbewerbs-Monitoring: 2026-08-19

**Zeitraum:** Manuell ausgelöster Lauf. Kein Vergleichszeitraum, siehe Abschnitt 6.
**Erfasste Sites:** hivebuy (Referenz), simplesystem, onventis, precoro, procureai, lio
**Datenbasis:** 719 Seiten gecrawlt (150/150/93/150/150/26), 5 Abruffehler, 17 Screenshots, ergänzend Websuche. `fetchMode: playwright` bei allen sechs Sites.

## 1. Kurzfassung

Dieser Lauf korrigiert zwei tragende Aussagen des Berichts vom 2026-08-18. Erstens: simple system unterbietet Hivebuy nicht mit 49-99 €/Monat. Das sind Add-on-Modulpreise; die Pakete kosten 99 / 396 / 594 €/Monat plus 2.500 € bzw. 4.000 € einmalige Integration (`snapshots/simplesystem/screenshots/2026-08-19/preise-vollseite.png`). Zweitens: der "Testsieger"-Vergleich von simple system führt Hivebuy überhaupt nicht auf, sondern Unite, Onventis und Meplato.

Das eigentliche neue Signal ist die Lokalisierung. Nicht nur Precoro, sondern auch Procure Ai fährt inzwischen eine vollständige deutsche Site (50 bzw. 50 deutsche Seiten, korrektes hreflang). Zwei kapitalisierte, KI-native Wettbewerber besetzen damit gleichzeitig Hivebuys Heimmarkt sprachlich. Onventis untermauert seine Souveränitäts-Positionierung mit einer unabhängigen Hackett-Validierung, die Hivebuy nicht hat.

Auf Hivebuys eigener Seite fällt ein konkreter, billig zu behebender Defekt auf: die englische Startseite trägt die Meta-Description "Improve your company" (20 Zeichen), zwei Karriereseiten haben gar keine.

## 2. Signale nach Wettbewerber

### simple system

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Pricing, korrigiert | Pakete Basic 99 €, Growth 396 €*, Enterprise 594 €*/Monat, jährlich abgerechnet (-10 %). Sternchen: einmalig 2.500 € ERP-Integration bzw. 4.000 € SAP-Cockpit. Add-ons je 99 €/Monat, OCI-Punchout und Externe Bestellsysteme je 49 €, SSO 0 € | `snapshots/simplesystem/screenshots/2026-08-19/preise-vollseite.png`, Seite `simplesystem.com/preise` | Der Vergleichspunkt zu Hivebuys 999 € ist 594 € plus Einmalkosten, nicht 99 €. Der Abstand ist real, aber kleiner als bisher angenommen |
| Konfigurationsfehler behoben | `keyPages.pricing` zeigte auf den Magazin-Artikel, nicht auf die echte Preisseite `simplesystem.com/preise` (Status 200, nie gecrawlt). Der Artikel enthält nur "99 €" und "49 €", die Add-on-Preise | Snapshot-Feld `prices` des Artikels vs. Screenshot der Preisseite | Ursache der Fehlaussage im Vorbericht. `competitors.json` korrigiert |
| Positionierung | H1 "Eine Plattform für alle indirekten Bedarfe", Title "simple system \| KI-gestützte Beschaffung \| 30 Tage Kostenlos Testen" | `snapshots/simplesystem/2026-08-19.json`, Startseite | Marktplatz-Modell mit 850+ Lieferanten, anderes Grundmodell als Hivebuys P2P-Software |
| Vergleichsartikel | Eigener Artikel vom 19.05.2026: simple system 94/100, Unite 79, Onventis 70, Meplato 55. **Hivebuy kommt nicht vor** | `simplesystem.com/en/magazin/e-procurement-software-comparison` | Nicht Angriff auf Hivebuy, sondern Abwesenheit: Hivebuy fehlt im Vergleichsset, das dieser Artikel für KMU-Suchende definiert |
| Content/SEO | 543 URLs im Sitemap, größter Fußabdruck der Gruppe | Snapshot-Feld `sitemapUrlCount` | 3x Hivebuys 180 URLs |
| Reviews | OMR 4,5 bei 22 Reviews, davon welche aus den letzten 30 Tagen und letzten 3 Monaten | `omr.com/en/reviews/product/simple-system` | Aktiver Review-Zufluss, siehe Abschnitt 4 |

### Onventis

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Unabhängige Validierung | "SolutionMap Validated" im Hackett Group Spring 2026 Assessment, 118 Anbieter, 16 Source-to-Pay-Kategorien, zusätzlich Customer-Value-Auszeichnung in AP-Automation/Invoice-to-Pay. Datum 13.05.2026 | `onventis.com/news/onventis-earns-validation-spring-2026-solutionmap-technology-assesment-26-05/` | Belastbarer Drittbeleg. Hivebuy hat weder Hackett-, G2- noch Gartner-Peer-Insights-Präsenz |
| Repositionierung | H1 der Startseite "SOVEREIGN PROCUREMENT", sechs Unterseiten: European Company, Customer-Managed Key, Resilience/US Cloud Act, Control over AI, Lead with Compliance | `snapshots/onventis/2026-08-19.json`, Seiten unter `/sovereign-procurement/` | Onventis besetzt EU-Datensouveränität systematisch, Hivebuy hat dazu keine sichtbare Position |
| Partnerschaft | Signicat, eIDAS-konforme E-Signatur direkt im CLM eingebettet, 02.04.2026 | `onventis.com/news/onventis-and-signicat-enter-strategic-partnership-for-legally-compliant-esignatures-26-04/` | Vertragsprozess ohne Fremdtool, relevant für Hivebuys Vertragsmanagement-Agent |
| Personal | Heiko Rumpl als Chief AI Officer, neuer CPO, April 2026 | `onventis.com/news/onventis-expands-management-board-26-04-13/` | Bestätigt strategische Verankerung, nicht nur Marketing |
| Pricing | Keine öffentlichen Preise. Treffer im Snapshot sind Fließtext-Zahlen, keine Preistabelle | Snapshot-Feld `prices`, Seiten `/company/`, `/solutions/education-onv/` | Sales-led, kein direkter Preisvergleich möglich |

### Precoro

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| DACH-Lokalisierung | 50 von 150 gecrawlten Seiten unter `/de/`, inklusive übersetzter Startseite und deutscher Preisseite | `snapshots/precoro/2026-08-19.json`, Feld `lang`; Belege `screenshots/2026-08-19/home-de-vollseite.png`, `preise-de-vollseite.png` | Direkter Vorstoß in den deutschsprachigen Markt |
| Übersetzungsqualität | Deutsche H1: "Verfolgen, steuern und sparen Sie bei zentrale Einkäufen über Projekte, Standorte oder Geschäftsbereiche hinweg" (Grammatikfehler "bei zentrale Einkäufen") | `snapshots/precoro/2026-08-19.json`, Seite `/de/` | Maschinelle Übersetzung ohne Lektorat. Angreifbar über sprachliche Qualität und lokale Nähe |
| Pricing | Core 499 $/Monat, Automation 999 $/Monat, Enterprise auf Anfrage, jährliche Abrechnung. Identische Beträge auf der deutschen Seite, weiterhin in USD | Snapshot-Felder `prices` von `/pricing` und `/de/pricing` | Preise in USD auf einer deutschen Seite sind eine Reibung, die Hivebuy adressieren kann |
| Preismodell gewechselt | Der Screenshot-Selektor `text=/per user\|pro Nutzer/i` findet nichts mehr, Precoro preist heute nach Paket statt pro Nutzer | Snapshot-Feld `screenshots[].error` des Vorlaufs, korrigiert in diesem Lauf | Der defekte Selektor war selbst das Signal |
| Content/SEO | 274 URLs im Sitemap | Snapshot-Feld `sitemapUrlCount` | Mehr als Hivebuys 180 |

### Procure Ai

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Dreisprachige Site, neu erfasst | 50 deutsche, 48 französische, 52 englische Seiten. hreflang korrekt gesetzt für `de-DE`, `fr-FR`, `x-default` | `snapshots/procureai/2026-08-19.json`, Felder `hreflang` und `lang` | **Der Vorbericht führte nur Precoro als DACH-Lokalisierer. Es sind zwei.** Verdoppelt den Druck auf deutschsprachige Suchbegriffe |
| Deutsche Positionierung | H1 `/de`: "Die weltweit erste KI-native Plattform für die Einkaufsautomatisierung." Englische H1: "Create more value with AI agents built for Procurement." | `snapshots/procureai/2026-08-19.json` | Superlativ-Claim direkt auf Deutsch, sprachlich nah an Hivebuys Agenten-Story |
| SEO-Lücke beim Wettbewerber | Die deutschen Seiten tragen weiterhin die englische Meta-Description | Snapshot-Feld `metaDescription` von `/de` | Lokalisierung ist nicht zu Ende geführt, kurzfristig ausnutzbar |
| Content-Volumen | 196 URLs im Sitemap, 107 news-/blog-artige Seiten unter den gecrawlten | Snapshot-Felder `sitemapUrlCount`, `pages[].url` | Auch hier mehr als Hivebuys 180 |
| Pricing | Keine öffentliche Preisliste | Snapshot-Feld `prices` ohne Preisseiten-Treffer | Sales-led |

### Lio (vormals askLio)

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Garantie-Kampagne | "$10M Challenge": Lio garantiert, 10 Mio. USD an Einsparpotenzial zu finden, sonst 100.000 USD Spende an eine Nonprofit-Organisation der Wahl. Ohne Frist | `snapshots/lio/2026-08-19.json`, Seite `/10-million`; Wortlaut geprüft auf `lio.ai/10-million` | Aggressives, quantifiziertes Vertrauensangebot. Direkter Gegenpol zu Hivebuys ROI-Claim |
| Finanzierung | 30 Mio. USD Series A, a16z, 05.03.2026, Gesamtfinanzierung 33 Mio. USD | `snapshots/lio/2026-08-19.json`, Seite `/newsroom/lio-technologies-raises-30m-series-a...`; bestätigt über PR Newswire | Größter Kapitalzufluss der beobachteten KI-nativen Gruppe |
| Personal | Jared Petras als Head of US Growth | `snapshots/lio/2026-08-19.json`, Seite `/newsroom/lio-appoints-jared-petras-as-head-of-us-growth` | US-Expansion personell unterlegt |
| Go-to-Market über Events | Eigene Seiten für CPO-Dinner, BME e-Lösungstage 2026, World Procurement Congress 2026, Bots & Buyers München und New York, zwei Kampagnen-Subdomains | `snapshots/lio/2026-08-19.json`, Feld `pages[].url` | Wachstum über Events und PR statt SEO. Konkurrenz um dieselben DACH-Einkaufsentscheider auf denselben Veranstaltungen |
| Content-Volumen | 42 URLs im Sitemap, 26 gecrawlt, kleinster Fußabdruck der Gruppe | Snapshot-Felder `sitemapUrlCount`, `pageCount` | Kein SEO-Wettbewerb, aber hohe Sichtbarkeit im Fachpublikum |
| Deutsche Rechtsseiten | `/impressum`, `/datenschutz`, deutsche Telefonnummer +49 | `snapshots/lio/2026-08-19.json` | Deutsche Präsenz, ohne lokalisierte Produktseiten |

## 3. Hivebuy im Vergleich

| Dimension | Hivebuy | Wettbewerber | Einschätzung |
|---|---|---|---|
| Preistransparenz | Öffentliche Staffel 899 / 999 / 1599 / 1899 €/Monat, Basic ab 999 € für bis zu 50 Nutzer | simple system 99 / 396 / 594 € plus Einmalkosten; Precoro 499 / 999 $; Onventis, Procure Ai, Lio ohne öffentliche Preise | Hivebuy ist transparent wie Precoro. Der Einstieg liegt über simple system, der Abstand zur Enterprise-Stufe (594 € vs. 999 €) ist aber deutlich kleiner als der Vorbericht nahelegte |
| DACH-Lokalisierung | Deutschsprachiger Content, deutscher Sitz, 100 deutsche von 149 Seiten | Precoro 50 deutsche Seiten, Procure Ai 50 deutsche plus 48 französische, Onventis DACH-nativ, Lio mit deutscher Rechtspräsenz | Von Einzelvorstoß zu Normalfall: vier von fünf Wettbewerbern sind deutschsprachig sichtbar |
| Content/SEO-Fußabdruck | 180 URLs im Sitemap | simple system 543, Precoro 274, Procure Ai 196, Lio 42 | Kleinster Fußabdruck außer Lio, unverändert struktureller Nachteil |
| KI-Agenten-Positionierung | H1 "Indirect purchasing on autopilot", Agenten für Intake, Chat, Vergleich, Status, Rechnung, Vertrag, Savings, Analysen | Lio "world's first multi agent system for procurement", Procure Ai "Die weltweit erste KI-native Plattform" | Beide Konkurrenten führen einen "weltweit erste"-Superlativ, Hivebuy einen Nutzenclaim. Sprachlich enges Feld |
| Unabhängige Belege | Capterra DE 4,7 bei 36 Reviews, OMR 4,5 bei 25. Keine G2-, Gartner- oder Hackett-Präsenz | Onventis Hackett SolutionMap Validated plus Customer Value; simple system selbstpublizierter Testsieg | Hivebuy hat die besseren Nutzerbewertungen, aber keinen Analystenbeleg |
| Werbeversprechen | ROI-Claim 521 % in 9 Monaten, Kennzahlen 60 %, 100 %, 3,4 Monate auf der Startseite | Lio garantiert 10 Mio. USD Fund oder 100.000 USD Spende | Lios Garantie ist überprüfbar formuliert und riskiert eigenes Geld, das wiegt schwerer als eine Prozentzahl |

## 4. Lücken und Risiken

- **Zwei DACH-Lokalisierer statt einem.** Precoro (50 deutsche Seiten) und Procure Ai (50 deutsche, 48 französische) sind beide im deutschsprachigen Suchraum sichtbar, beide frisch kapitalisiert. Der Vorbericht sah nur Precoro. Beleg: `lang`- und `hreflang`-Felder beider Snapshots.
- **Kein Analystenbeleg.** Onventis führt Hackett SolutionMap Validated (13.05.2026). Für Hivebuy fand die Websuche weder G2- noch Gartner-Peer-Insights-Profil. Verschärfend: G2 hat im Januar 2026 die Übernahme von Capterra, Software Advice und GetApp von Gartner vereinbart (PR Newswire), also genau der Plattformen, auf denen Hivebuys Reviews liegen.
- **Review-Zufluss stockt.** Capterra DE zeigt als jüngste Reviews Oktober und Dezember 2025. simple system hat auf OMR Reviews aus den letzten 30 Tagen. Hivebuy führt bei Menge und Note (4,7 bei 36), verliert aber an Aktualität.
- **Fehlen im entscheidenden Vergleichsartikel.** Der KMU-Vergleich von simple system (19.05.2026) bewertet Unite, Onventis und Meplato, nicht Hivebuy. Wer über diesen Artikel sucht, sieht Hivebuy nicht.
- **Eigener SEO-Defekt.** 8 von 149 Seiten ohne brauchbare Meta-Description, darunter die englische Startseite mit "Improve your company" (20 Zeichen) und beide Karriereseiten mit leerem Feld. Beleg: Feld `metaDescription` in `snapshots/hivebuy/2026-08-19.json`.
- **Nicht beobachtete Wettbewerber.** Unite (ehemals Mercateo) und Meplato tauchen im Vergleichsset auf, stehen aber nicht in `competitors.json`. Unite wird dort mit 79/100 vor Onventis geführt.

## 5. Handlungsempfehlungen

1. **DACH-Verteidigung gegen zwei Fronten** (Aufwand M, Effekt hoch): Precoros deutsche Seiten enthalten Grammatikfehler und führen USD-Preise, Procure Ais deutsche Seiten tragen englische Meta-Descriptions. Beides sind Qualitätslücken, gegen die native Sprache, EUR-Preise und lokale Referenzen kurzfristig wirken.
2. **Analysten- und Review-Präsenz aufbauen** (Aufwand M, Effekt hoch): G2-Profil anlegen, da G2 künftig auch Capterra hält, und Hackett SolutionMap prüfen. Parallel den Review-Zufluss reaktivieren, der jüngste Capterra-Eintrag ist von Dezember 2025.
3. **Preis-Story auf korrigierter Grundlage schärfen** (Aufwand S, Effekt mittel): Nicht gegen 99 € argumentieren, sondern gegen 594 € plus 2.500-4.000 € Einmalkosten. Hivebuys 999 € ohne Setup-Gebühr ist gegen diese Gesamtkosten verteidigbar, das gehört sichtbar gemacht.
4. **Meta-Descriptions reparieren** (Aufwand S, Effekt gering, aber sofort): 8 Seiten, darunter die englische Startseite. Konkrete Liste im Snapshot.
5. **Beobachtungsliste erweitern** (Aufwand S, Effekt mittel): Unite und Meplato in `competitors.json` aufnehmen. Unite wird im maßgeblichen KMU-Vergleich vor Onventis geführt und fehlt bisher vollständig.

## 6. Datenlücken

- **Kein Historienvergleich.** `diff.mjs` wurde für keine Site ausgeführt, weil keine zwei Snapshots existieren: die Snapshots des Laufs vom 2026-08-18 wurden nie committet und sind verloren. Verifiziert durch Aufruf, Ausgabe "Mindestens zwei Snapshots nötig (gefunden: 1)". Dieser Lauf ist die Baseline; der nächste liefert erstmals echte Diffs.
- **`www.onventis.de` ist durch die Egress-Policy gesperrt.** CONNECT wird mit 403 beantwortet, alle 5 Abruffehler dieses Laufs entfallen auf diesen Host (`snapshots/onventis/2026-08-19.json`, Feld `errors`, `ERR_TUNNEL_CONNECTION_FAILED`). Die konfigurierte Sitemap lag ebenfalls dort, deshalb war `sitemapUrlCount` 0; korrigiert auf `www.onventis.com/wpms-sitemap.xml` (Status 200). Da diese Sitemap durchgehend `.de`-URLs listet, bleibt der deutschsprachige Onventis-Baum unerfassbar, bis der Host freigeschaltet wird. Erreicht wurden 87 englische gegen 2 deutsche Seiten. **Freischaltung von `www.onventis.de` erforderlich.**
- **Weitere blockierte Hosts:** `presseportal.de`, `hasepost.de`, `business-on.de`, `thehackettgroup.com` (alle `EGRESS_BLOCKED`), `trusted.de` (403). Betroffen sind damit die Pressemeldungs-Historie von simple system und zwei Vergleichsartikel, in denen Hivebuy laut Suchtreffer vorkommt.
- **Crawl-Kappung.** simple system (543 URLs), Precoro (274) und Procure Ai (196) wurden bei 150 Seiten abgeschnitten (`truncated: true`). Die Sitemap-Zahlen sind vollständig, die Seiteninhalte nicht.
- **Zwei Screenshot-Selektoren waren defekt** und wurden korrigiert: `simplesystem/preis-tabelle` (Selektor `table` auf einer Seite ohne Tabelle) und `precoro/preis-tabelle` (Selektor auf "per user", Preismodell gewechselt). Beide Shots einmal wiederholt, jetzt 17 von 17 Screenshots fehlerfrei.
- **Zurückgewiesene Suchtreffer.** Zwei Ergebnisse wurden geprüft und nicht übernommen: Precoros "Mobile AI Expense Automation" ist laut Pressemitteilung vom 12.08.**2025**, nicht 2026; simple systems "Digital jetzt"-Kampagne und Prozesskostenrechner stammen aus 2020/2021. Beide wurden von Suchzusammenfassungen als aktuell dargestellt.
- **Widersprüchliche Preisangaben, nicht aufgelöst.** OMR nennt für Hivebuy 999 / 1899 €, die eigene Preisseite 899 / 999 / 1599 / 1899 €. OMR nennt für Precoro 35 $ pro Nutzer und Monat, Precoros Preisseite 499 / 999 $ pro Monat. Die Abweichungen bleiben als Widerspruch stehen.
