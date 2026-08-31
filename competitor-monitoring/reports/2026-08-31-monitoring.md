# Wettbewerbs-Monitoring: 2026-08-31

**Zeitraum:** 2026-08-19 bis 2026-08-31
**Erfasste Sites:** hivebuy (Referenz), simplesystem, onventis, precoro, procureai, lio
**Datenbasis:** 719 Seiten gecrawlt (150 hivebuy, 150 simplesystem, 93 onventis, 150 precoro, 150 procureai, 26 lio), 91 Abruffehler (alle onventis.de), Websuche ergänzend

## 1. Kurzfassung

Die auffälligste Veränderung liegt bei Precoro: Die Solution-Seite "accounts payable automation" liefert jetzt in Englisch und Deutsch einen 404-Fehler statt der vorherigen Produktseite, und die Kontaktseiten (`/contact-us`, `/de/contact-us`) haben trotz Status 200 keinen Title und kein H1 mehr. Parallel dazu haben mehrere Precoro-Solution- und Customer-Seiten 400 bis 550 Wörter Inhalt verloren, ein Bild, das zu einem laufenden Website-Umbau passt und ein zeitlich begrenztes Angriffsfenster öffnet. Onventis hat ein neues KI-Feature beworben (PDF-Angebots-Upload für die automatische Angebotsverarbeitung), simple system zeigt jetzt im Crawl-Sample seine dedizierte Preisseite mit den Paketen Basic/Growth/Enterprise. Auf der eigenen Seite hat Hivebuy die im Bericht vom 2026-08-19 bemängelten leeren Meta-Descriptions (englische Startseite, zwei Karriereseiten) inzwischen behoben. Bei Lio und Procure Ai gibt es keine neuen Presse- oder Finanzierungsmeldungen seit dem letzten Lauf, onventis.de bleibt weiterhin durch die Netzwerk-Policy gesperrt.

## 2. Signale nach Wettbewerber

### simple system

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Pricing | Dedizierte Preisseite `/preise` jetzt im Crawl-Sample: Basic ab 99 EUR, Growth ab 396 EUR, Enterprise ab 594 EUR pro Monat, zzgl. 2.500 bzw. 4.000 EUR einmaliger Integrationskosten | `snapshots/simplesystem/2026-08-31.json`, Seite `/preise`, Feld `prices`; Screenshot `screenshots/2026-08-31/preise-vollseite.png` | Bestätigt die im Vorbericht korrigierte Paketstruktur mit Primärdaten aus dem Crawl statt nur aus dem Magazin-Artikel. Der Einstiegspreis bleibt unter Hivebuys Einstiegsstufe |
| Content/SEO | Sitemap wächst von 543 auf 551 URLs (+8), neue Themenseiten u. a. `en/sso` (Single Sign-On), `use-cases/lieferantenstruktur-optimieren`, `angebotsanfragen` (RFQ in 5 Minuten) | `snapshots/simplesystem/2026-08-19.json` und `2026-08-31.json`, Feld `sitemapUrlCount`; Diff-Abschnitt "Neue Seiten" | Moderates organisches Wachstum, kein Sprung. SSO- und RFQ-Themen adressieren Enterprise-Anforderungen, die Hivebuy bisher nicht prominent bespielt |
| Methodik-Hinweis | Die Diff-Liste zeigt 90 "neue" und 90 "entfernte" Seiten, das ist überwiegend ein Sampling-Artefakt: Beide Läufe sind bei 150 von 543 bzw. 551 Sitemap-URLs gekappt (`truncated: true`), die Link-Crawl-Reihenfolge wechselt zwischen den Läufen | `snapshots/simplesystem/2026-08-19.json` und `2026-08-31.json`, Feld `truncated` | Kein echter Beleg für Content-Umbau, nur für Fußabdruck-Größe. Einzelne Titel wie `/preise` sind trotzdem belastbar, da sie im Crawl direkt erfasst wurden |

### onventis

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Produkt/Feature | Neue Webinar-Seite "Onventis AI-Powered PDF Offer Upload: Making Quote Processing Easier Than Ever" | `snapshots/onventis/2026-08-31.json`, Diff-Abschnitt "Neue Seiten", URL `/webinar/onventis-ai-powered-pdf-offer-upload-making-quote-processing-easier-than-ever/` | Weiteres KI-Feature im Sourcing-Bereich (automatische Angebots-/PDF-Verarbeitung), passt zu Onventis' bereits dokumentierter KI-Agenten-Positionierung |
| Datenlücke bestätigt | `www.onventis.de` bleibt gesperrt: 91 von 93 Abrufversuchen scheitern mit `net::ERR_TUNNEL_CONNECTION_FAILED`, curl bestätigt `CONNECT tunnel failed, response 403` | `snapshots/onventis/2026-08-31.json`, Feld `errors`; eigener curl-Test dieses Laufs | Unverändert seit dem Vorbericht (dort bereits als Lücke benannt). Der deutschsprachige Onventis-Baum bleibt für die Beobachtung unzugänglich, bis die Domain in der Allowlist ergänzt wird |
| Übrige Änderungen | Rund 20 Produkt-/Lösungsseiten zeigen +14 Wörter, H2-Struktur und Textende sind aber identisch zum Vorlauf | `snapshots/onventis/2026-08-19.json` und `2026-08-31.json`, Felder `h2`, `textExcerpt` | Boilerplate-Rauschen (vermutlich rotierende Kundenlogos/Karussell), kein inhaltliches Signal |

### precoro

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Technischer Defekt | `/solutions/accounts-payable-automation` und die deutsche Variante liefern jetzt Status 404 ("Precoro — Page Not Found") statt der vorherigen vollständigen Produktseite (vorher 4.111 bzw. 3.769 Wörter, inkl. Schema.org-Markup für Product/Organization) | `snapshots/precoro/2026-08-31.json`, Seite mit `status: 404`; Diff-Zeile `title \| ... \| Precoro — Page Not Found [404 Error]` | Wer aktuell nach "accounts payable automation" zu Precoro sucht, landet auf einer toten Seite. Zeitlich begrenztes Fenster für gezielten Content/SEA-Vorstoß von Hivebuy auf diesen Suchbegriff |
| Technischer Defekt | `/contact-us` und `/de/contact-us` haben trotz Status 200 keinen Title (`null`) und kein H1 mehr | Direkte Prüfung von `snapshots/precoro/2026-08-31.json`, Feld `title`/`h1` der jeweiligen Seite | Hinweis auf unvollständigen Deploy, nicht auf JS-Rendering-Problem des Crawlers (andere Precoro-Seiten im selben Lauf haben vollständige Titles) |
| Content-Rückbau | Mehrere Solution-/Customer-Seiten verlieren deutlich an Wortumfang: `/to/procure-to-pay-software` -556, `/solutions/intake-to-procure-software` -424, `/solutions/supplier-management` -417, `/solutions/spend-management-software` -402, `/product` -537, `/customers/healthcare` -409 Wörter (deutsche Varianten analog) | Diff-Tabellen `snapshots/precoro/2026-08-19.json` vs. `2026-08-31.json`, Feld `bodyText` | Konsistentes Muster über viele Seiten spricht für einen laufenden Website-Relaunch mit Copy-Kürzung, nicht für Einzelfälle. Erklärt vermutlich auch die zwei defekten Seiten oben |
| Partnerschaft (Websuche) | API-Integration mit BILL (NYSE: BILL) für automatisierte Zahlungsabwicklung, angekündigt 02.06.2026 | bill.com/blog/precoro-announces-api-integration-with-bill; precoro.com/blog/precoro-and-bill-integration | Liegt vor dem Beobachtungsfenster, war aber bisher in keinem Bericht erfasst. Schließt bei Precoro die Lücke zwischen Bestellfreigabe und Zahlungsausführung, ein Bereich, in dem Hivebuy öffentlich keine vergleichbare Partnerschaft zeigt |

### procureai

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Kaum Veränderung | Nur geringe Wortzahl-Schwankungen auf den `/company`-Seiten (DE -7, FR -9, EN -8 Wörter), keine neuen oder entfernten Seiten | `snapshots/procureai/2026-08-19.json` vs. `2026-08-31.json` | Kein inhaltliches Signal in diesem Zyklus |
| Finanzierung (bereits bekannt) | 13 Mio. USD Seed-Runde (Headline, C4 Ventures, Futury Capital), angekündigt 26.11.2025 | procure.ai/blog/seed-funding-announcement; tech.eu, 26.11.2025 | Kein neues Ereignis in diesem Zyklus, aber bislang in keinem Bericht mit korrektem Datum dokumentiert. Bestätigt Procure Ai als kapitalisierten KI-nativen Wettbewerber |

### lio (vormals askLio)

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Event/Go-to-Market | `bots-and-buyers-us.lio.ai` zeigt jetzt konkrete Details zu "Bots & Buyers NYC 2026" am 23.09.2026, inklusive FAQ und Anmeldeaufruf ("Apply to attend") | `snapshots/lio/2026-08-31.json`, Diff-Zeile neue H2 "FAQ", "Apply to attend.", "Who is Lio?"; Wortzahl 690 auf 944 (+254) | Lio treibt seine US-Expansion aktiv über Events voran (ergänzt die bereits im Vorbericht dokumentierte Einstellung eines Head of US Growth) |
| Event-Nachbereitung | `bots-and-buyers-eu.lio.ai` (München-Event) verliert 250 Wörter, neue H2 "TAKEAWAYS" und "WHAT'S HAPPENING" deuten auf Nachbereitung eines bereits stattgefundenen Events hin | `snapshots/lio/2026-08-19.json` vs. `2026-08-31.json` | Bestätigt, dass Lio Event-Marketing als durchgängigen Kanal nutzt, nicht nur punktuell |
| Finanzierung (bereits bekannt) | 30 Mio. USD Series A (a16z), angekündigt 05.03.2026, bereits im Bericht vom 2026-08-19 dokumentiert | `snapshots/lio/2026-08-31.json`, Seite `/newsroom/lio-technologies-raises-30m-series-a...` (Wortzahl unverändert) | Kein neues Ereignis in diesem Zyklus |

## 3. Hivebuy im Vergleich

| Dimension | Hivebuy | Wettbewerber | Einschätzung |
|---|---|---|---|
| Technische Seitenqualität | Meta-Description-Defekte aus dem Vorbericht (EN-Startseite, zwei Karriereseiten) sind behoben, 0 Abruffehler bei 150 gecrawlten Seiten | Precoro: neuer 404 auf einer Solution-Seite, zwei Kontaktseiten ohne Title/H1 | Hivebuy hat in diesem Zyklus eine reale Qualitätslücke geschlossen, während bei Precoro eine neue entstanden ist. Kurzfristiger Vorteil für Hivebuy |
| Procure-to-Pay-Zahlungsanbindung | Keine öffentlich kommunizierte Zahlungsausführungs-Partnerschaft in den gecrawlten Seiten gefunden | Precoro verbindet sich seit 02.06.2026 per API mit BILL für automatisierte Zahlungsabwicklung | Lücke, die Hivebuy im Procure-to-Pay-Narrativ schließen könnte, siehe Empfehlung 2 |
| KI-Feature-Kommunikation | Hivebuy kommuniziert KI-Agenten für Finance, Bedarfsanforderung u. a. (siehe eigene Snapshot-Seiten `ki-agenten-finance`, `ki-agenten-bedarfsanforderung`) | Onventis bewirbt neu automatisierte PDF-Angebotsverarbeitung, Lio und Procure Ai führen weiterhin "weltweit erste KI-native Plattform"-Superlative | Wettbewerbsfeld bleibt sprachlich eng, keine Verschiebung gegenüber dem Vorbericht |

## 4. Lücken und Risiken

- **Zahlungsintegration.** Precoros BILL-Partnerschaft deckt den letzten Schritt der Procure-to-Pay-Kette (Zahlungsausführung) ab. In den 150 gecrawlten Hivebuy-Seiten dieses Laufs findet sich keine vergleichbare öffentlich kommunizierte Partnerschaft. Beleg: `snapshots/hivebuy/2026-08-31.json`, keine Treffer für Zahlungsdienstleister-Namen in `pages[].bodyText`.
- **US-Event-Präsenz.** Lio baut mit "Bots & Buyers NYC 2026" (23.09.2026) und der bereits dokumentierten Einstellung eines Head of US Growth eine sichtbare US-Markt-Bearbeitung auf. Für Hivebuy sind in den gecrawlten Seiten keine vergleichbaren eigenen Event-Formate erkennbar.
- **Unveränderte Lücken aus dem Vorbericht.** Kein G2-, Gartner- oder Hackett-Analystenbeleg für Hivebuy, keine Beobachtung von Unite und Meplato in `competitors.json` (siehe Bericht 2026-08-19, Abschnitt 4). Beide Punkte bestehen unverändert fort, da dieser Lauf sie nicht neu geprüft hat.

## 5. Handlungsempfehlungen

1. **Precoros 404-Fenster nutzen** (Aufwand S, Effekt hoch): Solange `precoro.com/solutions/accounts-payable-automation` einen 404 liefert, ist gezielter Content/SEA-Einsatz von Hivebuy auf "accounts payable automation" bzw. "Kreditorenbuchhaltung Automatisierung" besonders wirksam. Zeitkritisch, da Precoro den Defekt vermutlich zeitnah behebt.
2. **Zahlungsausführungs-Partnerschaft prüfen** (Aufwand M, Effekt hoch): Eine BILL-vergleichbare Integration würde die von Precoro geschlossene Lücke zwischen Freigabe und Zahlung auch für Hivebuy adressieren und wäre ein eigenständiges Pressethema.
3. **onventis.de-Sperre beheben** (Aufwand S, Effekt mittel): Die Domain ist seit mindestens zwei Läufen (2026-08-19 und 2026-08-31) durch die Netzwerk-Policy gesperrt. Ergänzung in der Allowlist der Environment würde den deutschsprachigen Onventis-Baum erstmals vollständig beobachtbar machen.
4. **Crawl-Tiefe für große Sites erhöhen** (Aufwand M, Effekt mittel): simple system (551 Sitemap-URLs), Precoro (274) und Procure Ai (196) werden bei 150 Seiten gekappt. Ein höheres `--max-pages` oder gezielte Section-Crawls würden echte Content-Änderungen von Sampling-Rauschen (siehe simple system, Abschnitt 2) unterscheidbar machen.
5. **Lio-US-Kalender im Blick behalten** (Aufwand S, Effekt gering): "Bots & Buyers NYC 2026" am 23.09.2026 als nächsten Meilenstein der Lio-US-Expansion vormerken, für den übernächsten Lauf gezielt auf neue Ergebnisse/PR danach prüfen.

## 6. Datenlücken

- **`www.onventis.de` gesperrt.** Alle 91 Abruffehler dieses Laufs entfallen auf diesen Host (`net::ERR_TUNNEL_CONNECTION_FAILED`), eigener curl-Test bestätigt `CONNECT tunnel failed, response 403`. Die Domain fehlt in der Netzwerk-Policy-Allowlist der Environment (siehe `competitor-monitoring/README.md`, Abschnitt "Voraussetzung: Netzwerkzugang", dort ist nur `onventis.com`/`*.onventis.com` gelistet, nicht `onventis.de`). Unverändert seit dem Vorbericht.
- **Crawl-Kappung bei 150 Seiten.** simple system (551 Sitemap-URLs), Precoro (274) und Procure Ai (196) sind bei 150 Seiten gekappt (`truncated: true` in den jeweiligen Snapshots). Dadurch ist die Diff-Liste "neue/entfernte Seiten" bei simple system teilweise ein Sampling-Artefakt, siehe Abschnitt 2.
- **Keine Traffic-, Keyword- oder Backlink-Daten.** Unverändert strukturelle Lücke ohne Semrush-/Ahrefs-API-Zugang.
- **Review-Zeitreihen (G2, Capterra, OMR, trusted.de, Gartner).** Dieser Lauf hat keine gezielte Erhebung der aktuellen Bewertungszahlen für alle sechs Sites vorgenommen, nur punktuell für Precoro geprüft (G2: 4,7/5 bei 194 Reviews, Capterra: 4,8/5 bei 254 Reviews, Stand der Websuche). Für einen belastbaren Zeitreihenvergleich müsste dies pro Lauf systematisch für alle Sites erhoben werden.
