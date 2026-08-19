# Wettbewerbs-Monitoring: 2026-08-18

> **Nachtrag 2026-08-19: Snapshots dieses Laufs sind verloren.** Der Lauf wurde
> nie committet; wiederhergestellt werden konnten nur dieser Bericht,
> `competitors.json` und `crawl.mjs`. Die unten zitierten Felder aus
> `snapshots/<id>/2026-08-18.json` existieren im Repo nicht mehr und sind damit
> nicht mehr nachprüfbar. Die Aussagen bleiben als Beobachtung stehen, taugen
> aber nicht als Vergleichsbasis. Verbindliche Referenz ist der Lauf vom
> 2026-08-19, dessen Snapshots vollständig im Repo liegen.

**Zeitraum:** Erste vollständige Datenerhebung. Der Lauf vom selben Tag (`2026-08-18-baseline-simplesystem-vs-hivebuy.md`) scheiterte vollständig am Netzwerk-Egress für den Playwright-Browser; dieser Lauf ersetzt ihn mit echten Daten (Ursache siehe Abschnitt 6).
**Erfasste Sites:** hivebuy (Referenz), simplesystem, onventis, precoro, procureai, lio
**Datenbasis:** 724 Seiten gecrawlt (150/150/98/150/150/26), 5 Abruffehler, ergänzend Websuche. Keine Screenshots (siehe Abschnitt 6). Fetch-Modus statt Browser-Modus.

## 1. Kurzfassung

Drei Wettbewerber haben in den letzten Monaten sichtbar investiert: Precoro lokalisiert seine gesamte Website auf Deutsch und baut Payments in den P2P-Flow ein, Onventis positioniert sich komplett neu um "Sovereign Procurement" mit einem neuen Chief AI Officer, und Lio hat 30 Mio. USD Series A eingesammelt und stellt in den USA ein. simple system fährt parallel eine aggressive Content-/Preistransparenz-Kampagne (49-99 €/Monat, Sitemap mit 543 URLs, mehr als das Dreifache von Hivebuys 180). Hivebuy hat mit 521 % ROI-Claim und einer breiten Agenten-Featureliste ein starkes eigenes Story-Fundament, liegt aber im Content-Volumen am unteren Ende der Vergleichsgruppe und lässt DACH-Lokalisierungs-Momentum bei Precoro unwidersprochen. Handlungsbedarf: Preistransparenz-Antwort auf simple system, Content-Investition, und eine klare Abgrenzung zu den beiden frisch finanzierten AI-Agenten-Wettbewerbern (Lio, Procure Ai).

## 2. Signale nach Wettbewerber

### simple system

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Pricing | Magazin-Artikel "Warum simple system jetzt Preise zeigt – und was das bringt", zeigt 99 € und 49 € | `snapshots/simplesystem/2026-08-18.json`, Seite `magazin/preise-bei-simple-system`, Feld `prices` | Deutlich unter Hivebuys Einstiegstarifen (899-1599 €/Monat, siehe Hivebuy-Tabelle); direkte Angriffsfläche im SMB-Segment |
| Content/SEO | 543 URLs im Sitemap, davon 150 gecrawlt | `snapshots/simplesystem/2026-08-18.json`, Feld `sitemapUrlCount` | Größter Content-Fußabdruck der Vergleichsgruppe, mehr als 3x Hivebuy |
| Vergleichsartikel | Eigener Artikel "E-Procurement Software Comparison 2026" positioniert simple system als "Testsieger" mit 94/100 Punkten, "einziger Anbieter, der alle Kriterien erfüllt" | Websuche, `simplesystem.com/en/magazin/e-procurement-software-comparison` | Selbstpubliziert, keine unabhängige Quelle; dennoch aktive SEO-Strategie gegen Vergleichs-Keywords, die auch Hivebuy-Suchanfragen abfängt |
| Referenzen | 182.000 Bestellungen/Kunde, >30 Länder, >140 Mio. € vermitteltes Bestellvolumen (Selbstangabe) | Websuche (simplesystem.com Marketing-Content) | Zahlen aus Eigenwerbung, nicht verifiziert; als Widerspruch/Selbstangabe kennzeichnen |
| Konfigurationsfehler behoben | `keyPages.home` zeigte auf `simplesystem.com/de/`, das inzwischen 404 liefert; echte Startseite liegt auf `simplesystem.com/` (200) | Snapshot-Feld `status` für beide URLs, curl-Verifikation dieser Sitzung | Ohne Fix wäre der Home-Vergleich in jedem künftigen Lauf leer geblieben; `competitors.json` korrigiert |

### Onventis

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Repositionierung | Neuer H1 "SOVEREIGN PROCUREMENT" auf der Startseite, mit Unterseiten zu Customer-Managed-Key, Resilience/US-Cloud-Act, Control-over-AI, Compliance | `snapshots/onventis/2026-08-18.json`, Feld `h1` der Startseite, URLs unter `/sovereign-procurement/` | Onventis besetzt das Thema EU-Datensouveränität/AI-Act aktiv; Hivebuy hat dazu aktuell keine sichtbare eigene Positionierung |
| Personalwechsel | Management-Board erweitert: Heiko Rumpl neu als Chief AI Officer (April 2026), Chief Product Officer bestätigt | Websuche, `onventis.com/news/onventis-expands-management-board-26-04-13` | Bestätigt, dass die Sovereignty-/AI-Positionierung strategisch verankert ist, nicht nur Marketing |
| Referenzen | Kundenlogos: Caterpillar, Engie, Zeppelin, Hermes, Vetter Pharma | `snapshots/onventis/2026-08-18.json`, Seiten `/customer/*` und `/kunde/*` | Enterprise-lastiger als Hivebuys öffentlich gezeigte Referenzen |
| Pricing | Keine öffentlichen Preise gefunden (0 Preis-Treffer auf Kernseiten) | `snapshots/onventis/2026-08-18.json`, Feld `prices` auf Home/Company-Seiten leer | Enterprise-/Sales-led-Modell, kein direkter Preisvergleich möglich |
| Konfigurationsfehler behoben | `bases`/`sitemaps`/`keyPages.home` zeigten auf `onventis.com/de/` und `sitemap_index.xml`, beide 404; echte Startseite `onventis.com/` (200), echte Sitemap unter `onventis.de/wpms-sitemap.xml` laut robots.txt | curl-Verifikation, `onventis.com/robots.txt` Feld `Sitemap:` | `competitors.json` korrigiert; ohne Fix hätte der Crawl 0 Seiten geliefert (wie im vorherigen, gescheiterten Lauf) |

### Precoro

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| DACH-Lokalisierung | 50 von 150 gecrawlten Seiten unter `/de/`, vollständig übersetzte Startseite ("Beschaffungssoftware für zentrale Einkauf") | `snapshots/precoro/2026-08-18.json`, Feld `lang: "de"` auf `/de/`-Seiten | Direkter Vorstoß in Hivebuys deutschsprachigen Heimmarkt |
| Produkterweiterung | "Precoro Launches AI Procurement Feature" (Quote-zu-Requisition, April 2026), "Precoro Completes the Procure-to-Pay Loop with Integrated Payment Automation Powered by Stripe" (Precoro Payments: ACH/Wire/International, Juni 2026) | Websuche, PR Newswire/Newsfilecorp | Precoro erweitert P2P um eingebettete Zahlungen; Hivebuy sollte prüfen, ob Payment-Automatisierung auf der eigenen Roadmap fehlt |
| Pricing | Öffentliche Staffelpreise 499 $/Monat und 999 $/Monat auf `/pricing` | `snapshots/precoro/2026-08-18.json`, Feld `prices` | Vergleichbar transparent wie Hivebuy, aber in USD und niedrigerer Einstieg als Hivebuys Top-Tier |
| Referenzen | >1.000 Kunden in 80+ Ländern (Selbstangabe) | Websuche (Precoro-Produktseite) | Nicht verifiziert, als Selbstangabe kennzeichnen |

### Procure Ai

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Positionierung | H1 "Create more value with AI agents built for Procurement" | `snapshots/procureai/2026-08-18.json`, Feld `h1` Startseite | Nahezu identische Sprache zu Hivebuys eigenem Agenten-Feature-Set |
| Finanzierung | 13 Mio. USD Seed-Runde, angeführt von Headline, mit C4 Ventures, Futury Capital u.a., verkündet 5. November 2025; Mittel für Europa-Expansion | Websuche (pulse2.com, procure.ai/blog/seed-funding-announcement) | Kapitalisierter AI-nativer Wettbewerber mit explizitem Europa-Fokus; Datum liegt vor dem 14-Tage-Fenster, als Hintergrund-Kontext markiert |
| Pricing | Keine öffentliche Preisliste gefunden | `snapshots/procureai/2026-08-18.json`, Feld `prices` nur vereinzelte Zahlen ohne Preistabelle | Enterprise-/Sales-led wie Onventis und Lio |

### Lio (vormals askLio)

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Finanzierung | 30 Mio. USD Series A, angeführt von a16z, mit SV Angels, Harry Stebbings, Y Combinator, verkündet 5. März 2026; Gesamtfinanzierung damit 33 Mio. USD | Websuche (PR Newswire, finsmes.com), bestätigt durch `lio.ai/newsroom/lio-technologies-raises-30m-series-a...` im Snapshot | Größter Kapitalzufluss unter den beobachteten AI-nativen Wettbewerbern in diesem Zeitraum |
| Personal | Jared Petras neu als "Head of US Growth" | `snapshots/lio/2026-08-18.json`, Seite `newsroom/lio-appoints-jared-petras-as-head-of-us-growth` | US-Expansion wird personell unterlegt |
| Positionierung | H1 "The world's first multi agent system for procurement"; CEO-Manifest-Seite "why we built Lio" | `snapshots/lio/2026-08-18.json`, Feld `h1` und Seite `newsroom/why-we-built-lio-a-manifesto-by-ceo-vladimir-keil` | Multi-Agent-Framing überschneidet sich mit Hivebuys Agenten-Sprache, aber mit deutlich frischerem Funding-Rückenwind |
| Content-Volumen | Nur 42 URLs im Sitemap, 26 gecrawlt, zwei neue Kampagnen-Subdomains `bots-and-buyers-eu.lio.ai` / `bots-and-buyers-us.lio.ai` gefunden | `snapshots/lio/2026-08-18.json`, Felder `sitemapUrlCount`, `pages[].url` | Kleiner Content-Fußabdruck, Wachstum läuft über Events/PR statt SEO |

## 3. Hivebuy im Vergleich

| Dimension | Hivebuy | Wettbewerber | Einschätzung |
|---|---|---|---|
| Preistransparenz | Öffentliche Staffelpreise 899-1899 €/Monat auf `/en/pricing` (Snapshot-Feld `prices`) | simple system bewirbt aktiv 49-99 €/Monat; Precoro 499-999 $/Monat; Onventis, Procure Ai, Lio zeigen keine Preise | Hivebuys Einstiegspreis liegt deutlich über simple systems neuer Transparenz-Kampagne |
| DACH-Fokus | Deutschsprachiger Content, deutscher Firmensitz | Precoro jetzt mit 50 deutschen Landingpages inkl. übersetzter Startseite (`snapshots/precoro/2026-08-18.json`); Onventis DACH-nativ mit Sovereignty-Fokus | Precoros Lokalisierung ist ein neuer, direkter Vorstoß in Hivebuys Heimmarkt |
| Content/SEO-Fußabdruck | 180 URLs im Sitemap (Feld `sitemapUrlCount`) | simple system 543, Precoro 274, Procure Ai 196, alle größer als Hivebuy | Hivebuy hat das kleinste indexierte Content-Volumen der sechs Sites |
| KI-Agenten-Positionierung | Feature-Set "AI-Agentes" (Purchase Requisition, Finance Backoffice, Savings-, Contract-, Invoice-, Analytics-, Catalog-Agent) | Lio: "world's first multi agent system for procurement" + 30 Mio. USD Series A; Procure Ai: "AI agents built for Procurement" + 13 Mio. USD Seed | Beide AI-nativen Direktkonkurrenten sind frisch kapitalisiert und sprachlich fast deckungsgleich zu Hivebuys Agenten-Story |
| Social Proof | ROI-Claim "521 % in 9 Monaten" auf Referenzseite (Snapshot-Feld `h2`) | Onventis: Caterpillar, Engie, Zeppelin, Hermes, Vetter Pharma als Logos | Onventis' Logo-Liste ist enterprise-lastiger; Hivebuys Claim ist stärker quantifiziert, aber ohne große Marken-Logos sichtbar |

## 4. Lücken und Risiken

- **Preis-Story:** simple system macht Preistransparenz aktiv zum Content-Thema (eigener Artikel dazu) und unterbietet Hivebuys Einstiegstarif deutlich. Ohne Gegenreaktion wirkt Hivebuy im unteren SMB-Segment teurer und weniger transparent.
- **DACH-Verteidigung:** Precoros vollständige deutsche Lokalisierung (50 Seiten, übersetzte Startseite) ist ein neuer Wettbewerber im deutschsprachigen Suchraum, wo Hivebuy bisher wenig direkte Konkurrenz aus dem US-/Ukraine-Raum hatte.
- **Content-Volumen:** Mit 180 indexierten URLs liegt Hivebuy klar hinter simple system (543), Precoro (274) und Procure Ai (196), ein struktureller SEO-Nachteil bei Nicht-Marken-Suchanfragen.
- **Kapitalisierung der AI-Agenten-Konkurrenz:** Lio (33 Mio. USD Gesamtfinanzierung) und Procure Ai (13 Mio. USD) verwenden nahezu identische "AI-Agenten"-Sprache wie Hivebuy und haben sichtbar mehr Kapital für Go-to-Market.
- **Eigene Konfigurationsfehler:** Hivebuys eigene `keyPages.pricing`-URL in `competitors.json` war veraltet (`/en/preise-hivebuy`, 404) und zeigte nicht auf die echte, aktive Preisseite `/en/pricing`, ein Hinweis darauf, dass auch interne Linkstrukturen/Redirects geprüft werden sollten.

## 5. Handlungsempfehlungen

1. **Preistransparenz-Gegenzug prüfen** (Aufwand M, Effekt hoch): Eigene Einstiegsstaffel sichtbarer machen oder einen Vergleichs-/Preis-Content-Artikel gegen simple systems 49-99-€-Positionierung veröffentlichen.
2. **DACH-Differenzierung gegen Precoro schärfen** (Aufwand M, Effekt hoch): Lokale Referenzen, Support-Sprache und Compliance-Themen (DSGVO/deutsche Rechnungsstellung) prominenter herausstellen, bevor Precoros Lokalisierung an Sichtbarkeit gewinnt.
3. **Content-/SEO-Investition** (Aufwand L, Effekt mittel-hoch): Sitemap-Volumen (aktuell 180 URLs) durch Use-Case- und Vergleichsseiten erhöhen, ähnlich der Struktur, die simple system und Precoro erfolgreich fahren.
4. **Abgrenzung zu AI-Agenten-Wettbewerbern schärfen** (Aufwand S, Effekt mittel): Klare Differenzierung gegenüber Lio/Procure Ai formulieren (z. B. Integrationstiefe, Time-to-Value, ROI-Beleg), da beide mit ähnlicher Sprache, aber frischem Funding werben.
5. **Interne Linkpflege** (Aufwand S, Effekt gering, aber leicht umsetzbar): Eigene Preisseiten-Verlinkung (`/en/preise-hivebuy` → `/en/pricing`) und ggf. weitere veraltete interne Links prüfen.

## 6. Datenlücken

- **Keine Screenshots:** Der Playwright/Chromium-Browser konnte in dieser Umgebung keine der Zielseiten laden (`net::ERR_CONNECTION_RESET` für alle Hosts, auch nach expliziter Proxy-Konfiguration `proxy: { server: HTTPS_PROXY }` im Browser-Launch). Diagnose in dieser Sitzung: `curl` und Node `fetch()` (mit `NODE_USE_ENV_PROXY=1`) erreichen dieselben Hosts über denselben Proxy problemlos (HTTP 200), der lokale Proxy-Statusendpunkt (`/__agentproxy/status`) verzeichnet dabei keine Policy-Ablehnung für diese Hosts. Das deutet auf eine netzwerkseitige Blockade speziell des Chromium-Browser-Datenverkehrs hin (vermutlich TLS-Fingerprinting am Gateway), nicht auf eine fehlende Host-Freigabe. `crawl.mjs` wurde um einen `--no-browser`-Schalter ergänzt, mit dem dieser Lauf komplett auf `fetch()` umgestellt wurde. Ergebnis: voller Textinhalt für alle Seiten, aber keine Screenshots für Notion oder Vergleich.
- **onventis.de-Subdomain:** 5 von 98 Onventis-URLs (die deutschsprachigen Sovereignty-Unterseiten unter `onventis.de/souveraener-einkauf/...`) scheiterten mit `fetch failed` (`snapshots/onventis/2026-08-18.json`, Feld `errors`). Deutschsprachiger Inhalt dieser Seiten fehlt in diesem Bericht.
- **Kein Historienvergleich möglich:** Dies ist der erste vollständig erfolgreiche Snapshot für alle sechs Sites; `diff.mjs` wurde nicht ausgeführt, da keine Site über einen älteren, gültigen Snapshot verfügt (der Lauf vom selben Tag scheiterte komplett am Browser-Egress-Problem oben). Der nächste reguläre Lauf kann erstmals echte Diffs liefern.
- **Konfigurationskorrekturen:** `competitors.json` wurde für drei Sites korrigiert, da die hinterlegten URLs nicht mehr erreichbar waren: Onventis (`bases`, `sitemaps`, `keyPages.home`, Shot-URLs von `/de/` bzw. `sitemap_index.xml` auf die tatsächlich aktiven `onventis.com/` bzw. `onventis.de/wpms-sitemap.xml`), simple system (`keyPages.home` und Shot-URLs von `/de/` auf `/`) und Hivebuy selbst (`keyPages.pricing` und Shot-URL von `/en/preise-hivebuy` auf `/en/pricing`). Ohne diese Korrekturen wären die betroffenen Homepages/Preisseiten mit Status 404 in den Snapshot gegangen.
- **Review-Plattformen:** G2 und Gartner Peer Insights lieferten für Hivebuy in der Websuche keine direkten Treffer in diesem Lauf; Aussagen zu Reviews stützen sich auf Capterra und OMR.
