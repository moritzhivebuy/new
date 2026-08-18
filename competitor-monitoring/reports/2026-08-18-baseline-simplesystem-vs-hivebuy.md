# Baseline: simple system vs. Hivebuy

**Datum:** 2026-08-18
**Erfasste Sites:** simplesystem.com, hivebuy.com, dazu Kurzprofile procure.ai und lio.ai
**Datenbasis:** ⚠️ Ausschließlich Websuche und öffentliche Drittquellen. **Kein direkter
Seitenabruf**, weil die Netzwerk-Policy dieser Umgebung ausgehende Verbindungen
blockt (`EGRESS_BLOCKED` für simplesystem.com, hivebuy.com und omr.com). Damit
gibt es für diesen Lauf keine Snapshots, keine Titles/Metas, keine Diffs.
Das ist die Baseline auf Basis dessen, was ohne Crawl belegbar war.

---

## 1. Kurzfassung

simple system und Hivebuy konkurrieren im DACH-Mittelstand um indirekte
Beschaffung, greifen das Problem aber von zwei Seiten an: simple system kommt
vom **Lieferanten-Netzwerk und Katalog** (C-Teile-Marktplatz, über 750 Lieferanten
laut Eigenangabe), Hivebuy von der **Prozess- und Workflow-Seite**
(Freigaben, Budget, Rechnung, KI-Agenten, "in einer Stunde live"). Beide haben
2025/2026 in Richtung des jeweils anderen ausgebaut: simple system hat zum
01.01.2025 auf ein transparentes, modulares SaaS-Preismodell umgestellt und
Dashboard-/Controlling-Funktionen ergänzt, Hivebuy hat KI-Agenten (Intake,
Recommendation, Category) eingeführt.

Zwei Punkte sind unmittelbar relevant: simple system **zeigt Preise öffentlich**
(99 € pro Modul und Monat) und bewirbt das aktiv als Differenzierung, und simple
system betreibt mit `/magazin/` ein sichtbar größeres Content-Asset inklusive
eigener Vergleichsartikel ("E-Procurement Software Comparison 2026"), in denen es
sich selbst als Testsieger positioniert.

## 2. Signale simple system

| Signal | Beobachtung | Quelle | Relevanz für Hivebuy |
|---|---|---|---|
| Positionierung | "Beschaffungsplattform für C-Teile", browserbasiertes E-Procurement für geringwertige Artikel mit hohem Volumen | [simplesystem.com/de](https://www.simplesystem.com/de/) | Andere Klammer: Katalog/Marktplatz statt Prozess. Hivebuys Workflow-Story kollidiert nur teilweise |
| Netzwerkgröße | über 750 Lieferanten, über 80 Mio. Artikel; an anderer Stelle "über 380 Lieferanten" | [nexoma](https://nexoma.de/simple-system/), [company.simplesystem.com](https://en.company.simplesystem.com/), [windmuehlenbauer](https://windmuehlenbauer.com/simple-system/) | ⚠️ Widersprüchliche Zahlen, per Crawl zu verifizieren. Netzwerkgröße ist ihr stärkstes Argument |
| Kundenbasis | über 2.000 Kunden, 46.300 Nutzer; Referenzen KNORR-BREMSE, VULKAN, Gerresheimer, SIG | [company.simplesystem.com](https://en.company.simplesystem.com/) | Größenordnung deutlich über Hivebuys öffentlich sichtbarer Referenzliste |
| Pricing | Seit 01.01.2025 SaaS-Baukasten: Module Basis / Marktplatz / Controlling je 99 €/Monat, ERP-Integration +99 €, OCI-Punchout bzw. externe Bestellsysteme +49 €. Explizit "keine versteckten Gebühren, keine Staffelpreise" | [simplesystem.com/magazin/preise-bei-simple-system](https://simplesystem.com/magazin/preise-bei-simple-system) | Direkter Angriff auf "Preis auf Anfrage". Hivebuy wird laut Drittquelle ab 399 €/Monat gelistet, also im Einstieg teurer wirkend |
| Lieferantenmodell | Lieferanten zahlen Umsatzanteil, Provisionsmodell transparent ausgewiesen | [simplesystem.com/magazin/preise-bei-simple-system](https://simplesystem.com/magazin/preise-bei-simple-system) | Zweiseitiges Modell, das Hivebuy nicht hat. Erklärt auch die Kritik "nicht kostenlos, Kosten für beide Seiten" |
| Produkt 2025/26 | Erweitertes Dashboard für indirekte Beschaffung, interner Katalog für kleinere Lieferanten ohne Schnittstelle, neue Plattform-Features im Herbst angekündigt, Prozesskostenrechner | [beschaffung-aktuell](https://beschaffung-aktuell.industrie.de/c-teile-management/simple-system-bietet-erweitertes-dashboard-fuer-indirekte-beschaffung/), [Presseportal](https://www.presseportal.de/nr/146850) | Sie bauen Controlling und Katalogflexibilität aus, also genau Richtung Hivebuy |
| Content/SEO | Eigenes Magazin unter `/magazin/` (DE) und `/en/magazin/` (EN), zusätzlich `company.simplesystem.com` und `en.company.simplesystem.com`. Ranking-relevante Money-Keywords direkt bedient: "Beschaffungsplattform", "B2B Handelsplattform", "C-Teile-Management Definition", "E-Procurement Software Comparison 2026" | Suchergebnisse, siehe Quellen unten | ⚠️ Größter Hebel und größte Lücke. Saubere Sprachtrennung (`/de/`, `/en/`), die Hivebuy laut SEO-Analyse fehlt |
| Vergleichs-Content | "E-Procurement Software Comparison 2026": simple system als Testsieger mit 94/100, "einziger Anbieter, der alle Kriterien erfüllt", Go-live 1-2 Wochen, stärkste SAP-Integration | [simplesystem.com/en/magazin/e-procurement-software-comparison](https://simplesystem.com/en/magazin/e-procurement-software-comparison) | Selbst erstellter Vergleich, der Kaufentscheidungen beeinflusst. Prüfen, ob Hivebuy darin auftaucht und wie |
| Marketing-Programme | Digitalisierungskampagne im Umfeld von "Digital jetzt", Referenzprojekt DR. KADE | [Presseportal](https://www.presseportal.de/nr/146850) | Fördermittel-Angle als Vertriebsargument, bei Hivebuy nicht sichtbar |
| Reviews | OMR: gelobt werden Einfachheit, Preisvergleich über mehrere Lieferanten, hinterlegte Adressen, Konfigurierbarkeit von Nutzergruppen/Freigaben/Limits und ERP-Anbindung. Kritik: Kosten fallen auf Kunden- **und** Lieferantenseite an | [OMR Reviews](https://omr.com/en/reviews/product/simple-system) | Die Kostenkritik ist eine konkrete Angriffsfläche |

## 3. Hivebuy im Vergleich

| Dimension | Hivebuy | simple system | Einschätzung |
|---|---|---|---|
| Kernversprechen | Indirekter Einkauf "intelligent, intuitiv, schlanke Prozesse", Start in unter einer Stunde ohne IT-Projekt | Zentrale Plattform für C-Teile-Beschaffung mit direkter ERP-Anbindung | Hivebuy gewinnt bei Time-to-Value, simple system bei Sortiment |
| Zielgruppe | Mittelstand/KMU, "zu komplex für manuelle Prozesse, zu agil für Konzern-Suites" | KMU bis Industrie, C-Teile-lastige Beschaffung | Starke Überlappung im Mittelstand |
| Funktionsumfang | Eigene Marktplätze, automatisierte Freigaben, Lieferanten-, Vertrags- und Rechnungsmanagement, Einkaufscontrolling, KI-Agenten (Intake, Recommendation, Category) | Katalog/Marktplatz, Freigabe-Workflows, Budgetkontrolle, ERP-Integration, Lieferantenmanagement, Reporting, interner Katalog | Hivebuy breiter bei Rechnung/Vertrag und KI, simple system tiefer bei Katalog/Beschaffungsnetzwerk |
| KI | Explizit ausgespielt, drei benannte Agenten | In den Quellen kein KI-Feature-Set gefunden | ✅ Klarer, aktuell verteidigbarer Vorsprung |
| Pricing-Kommunikation | Ab 399 € (Drittquelle), 14 Tage Test | Öffentliche Modulpreise ab 99 €/Modul, aktiv als Fairness-Argument beworben | ❌ Nachteil in der Wahrnehmung, unabhängig vom tatsächlichen Leistungsumfang |
| Social Proof | Über 360 Bewertungen mit 4,7/5 auf Capterra; Referenzen u. a. Tennis-Point, MediaMarktSaturn, LGI; OMR noch ohne ausreichende Reviewzahl | über 2.000 Kunden, 46.300 Nutzer, Industriereferenzen | Hivebuy hat die bessere Review-Dichte, simple system die größeren Zahlen |
| Content/SEO-Struktur | Laut interner SEO-Analyse: deutsche Slugs unter `/en/`, kein `/de/`, Blog ohne Sprachpräfix, fehlendes hreflang | Getrennte `/de/` und `/en/` Pfade plus eigene Company-Subdomains | ❌ Struktureller Nachteil, bereits in `seo-analysis-hivebuy.md` dokumentiert |
| Bot-Zugänglichkeit | Blockt Nicht-Browser-User-Agents (403, vermutlich Cloudflare) | In den Suchergebnissen breit indexiert | Für eigenes Monitoring und für Crawler relevant |

## 4. Lücken und Risiken

1. **Preistransparenz:** simple system nutzt öffentliche Preise als Vertrauensargument und schreibt darüber einen eigenen Artikel. Solange Hivebuy nur über Dritte mit "ab 399 €" auffindbar ist, verliert Hivebuy den Vergleich im Vorfeld des ersten Gesprächs.
2. **Vergleichs-Content:** simple system besetzt "E-Procurement Software Vergleich" mit eigenem Testsieger-Framing. Wer 2026 vergleicht, landet dort, nicht bei Hivebuy.
3. **Content-Volumen und Sprachstruktur:** ein etabliertes Magazin in DE und EN gegen einen Blog ohne Sprachpräfix. Das ist eine Reichweitenlücke, keine Textqualitätsfrage.
4. **Netzwerkargument:** "über 750 Lieferanten, 80 Mio. Artikel" ist im Einkaufsgespräch schwer zu kontern, wenn Hivebuy nicht dagegensetzt, dass bestehende Lieferantenbeziehungen behalten werden können.
5. **Kein eigenes Zahlengerüst:** Hivebuy kommuniziert öffentlich keine Kunden- oder Nutzerzahlen, die sich mit den 2.000/46.300 von simple system vergleichen ließen.

## 5. Handlungsempfehlungen

| # | Maßnahme | Aufwand | Erwarteter Effekt |
|---|---|---|---|
| 1 | Preisseite mit echten Zahlen und Paketlogik öffentlich machen, inklusive Vergleich "Modulpreise vs. Komplettpreis" | M | Entzieht simple systems Fairness-Argument die Grundlage, verbessert Conversion vor dem Erstkontakt |
| 2 | Eigener Vergleichs-Hub `/de/vergleich/...` mit Einzelseiten je Wettbewerber (simple system, Onventis, Coupa, Precoro), sachlich und mit Quellen | L | Besetzt die Vergleichs-Suchintention, statt sie dem Wettbewerber zu überlassen |
| 3 | Zwei Kernzahlen öffentlich festlegen (Kunden, verwaltetes Einkaufsvolumen oder Nutzer) und konsistent überall ausspielen | S | Schließt die Glaubwürdigkeitslücke gegen "2.000 Kunden" |
| 4 | KI-Agenten als eigene Landingpage mit Prozessbeispielen und Zeitersparnis belegen, solange der Vorsprung besteht | M | Verteidigbare Differenzierung, die simple system aktuell nicht bedient |
| 5 | Angle "Sie behalten Ihre Lieferanten" als Battlecard und Website-Modul gegen das Marktplatzmodell mit Lieferantenprovision setzen | S | Direkte Antwort auf die häufigste Kritik am Wettbewerbsmodell |

Die SEO-Strukturfixes (hreflang, `/de/`, Slugs) sind hier nicht wiederholt, sie stehen bereits priorisiert in `seo-analysis-hivebuy.md`.

## 6. Datenlücken

| Lücke | Grund | Auflösung |
|---|---|---|
| Keine Snapshots, keine Diffs | Netzwerk-Egress dieser Umgebung blockt alle Zieldomains (`EGRESS_BLOCKED`) | Netzwerk-Policy der Umgebung für die Hosts in `README.md` öffnen, dann `crawl.mjs` |
| Lieferantenzahl 750 vs. 380 | Unterschiedliche Drittquellen, unterschiedliche Stände | Direkter Abruf der Startseite und Lieferantenseite |
| Hivebuy-Preis nur aus Drittquelle (ab 399 €) | Keine öffentliche Preisseite abrufbar | Intern verifizieren |
| Inhalt des Vergleichsartikels von simple system | Nur Suchsnippet vorhanden | Direkter Abruf, dann prüfen wie Hivebuy dargestellt wird |
| Traffic-, Keyword- und Backlink-Zahlen beider Seiten | Keine Semrush/Ahrefs-Anbindung | API-Key hinterlegen oder Daten manuell exportieren |
| OMR-/Capterra-Reviewstände als Zeitreihe | Kein Abruf der Profile möglich | Review-Profile sind in `competitors.json` hinterlegt und werden mit Egress mitgecrawlt |

## 7. Neu ins Monitoring aufgenommen: Procure Ai und Lio

Beide sind KI-nativ und treffen damit genau die Dimension, in der Hivebuy gegen
simple system aktuell vorne liegt. Der KI-Vorsprung gilt also gegen simple system,
nicht gegen den Gesamtmarkt.

### Procure Ai (procure.ai)

| Signal | Beobachtung | Quelle |
|---|---|---|
| Positionierung | Europäischer Anbieter einer "AI-native Procurement Automation Platform" | [procure.ai/platform](https://www.procure.ai/platform) |
| Bausteine | Unified Analytics, Autonomous Operations, Guided Operations, Generative Intake | [procure.ai/platform](https://www.procure.ai/platform) |
| Funktionsversprechen | Spend- und Lieferantendaten systemübergreifend vereinheitlichen, Intake verbessern, Sparpotenziale in der Spend-Analytics finden, taktische Sourcing-Events und Verhandlungen autonom ausführen | [procure.ai/platform](https://www.procure.ai/platform) |
| Zielgruppe | Enterprise, nicht Mittelstand | [Gartner Peer Insights](https://www.gartner.com/reviews/product/procure-ai) |
| Pricing | Subskription nach Unternehmensgröße, Modulen und Use Cases bzw. Agenten, keine öffentlichen Preise | [Capterra](https://www.capterra.com/p/10016095/Procure-Ai/), [GetApp](https://www.getapp.com/operations-management-software/a/procure-ai/) |
| Relevanz für Hivebuy | ⚠️ Mittel. Segment liegt über Hivebuys Kernzielgruppe, die Sprache ("autonome Beschaffung", "Generative Intake") prägt aber die Erwartung, an der Hivebuy gemessen wird | |

### Lio, vormals askLio (lio.ai)

| Signal | Beobachtung | Quelle |
|---|---|---|
| Positionierung | "AI-powered procurement workforce", ausdrücklich keine Assistenzfunktion, sondern virtuelle Belegschaft, die den Beschaffungsprozess eigenständig abwickelt, gesteuert über Agent Operating Procedures | [Beschaffung aktuell](https://beschaffung-aktuell.industrie.de/artikel/asklio-sammelt-30-mio-usd-ein-und-heisst-jetzt-lio/), [Y Combinator](https://www.ycombinator.com/companies/lio) |
| Agenten | Guided Buying, Invoice Agent, Order Confirmation, Supplier Onboarding, Negotiation Agent, Contract Negotiation Agent, Approvals Agent | [Y Combinator](https://www.ycombinator.com/companies/lio) |
| Finanzierung | 30 Mio. USD Series A (in EUR mit 25,7 Mio. berichtet), München, Umbenennung von askLio zu Lio | [Beschaffung aktuell](https://beschaffung-aktuell.industrie.de/artikel/asklio-sammelt-30-mio-usd-ein-und-heisst-jetzt-lio/), [Munich Startup](https://www.munich-startup.de/en/117802/lio-raises-25-million-euros/), [Yahoo Finanzen](https://de.finance.yahoo.com/nachrichten/m%C3%BCnchner-startup-lio-technologies-sichert-133000786.html) |
| Kunden | über 100 Unternehmen, genannt u. a. Munich Re, Brose, Dormakaba, TÜV Süd, Rehau | [Y Combinator](https://www.ycombinator.com/companies/lio) |
| Technik | Integration in bestehende P2P- und ERP-Systeme, ISO 27001, DSGVO, Microsoft-Partner, Hosting auf Azure Europe | [Y Combinator](https://www.ycombinator.com/companies/lio) |
| Marktargument | Gegenüberstellung von über 180 Mrd. USD Personalkosten im Einkauf zu rund 10 Mrd. USD Softwarekosten, daraus abgeleitet der Anspruch, Arbeit statt Software zu verkaufen | [Beschaffung aktuell](https://beschaffung-aktuell.industrie.de/artikel/asklio-sammelt-30-mio-usd-ein-und-heisst-jetzt-lio/) |
| Relevanz für Hivebuy | 🔴 Hoch. Deutschsprachig, agentenbasiert, gut finanziert, sichtbare Industriereferenzen. Der direkteste Wettbewerber um die KI-Erzählung, und die Referenzliste wirkt im Mittelstandsgespräch |

**Konsequenz für Empfehlung 4:** Die KI-Landingpage bleibt richtig, aber das Framing
"wir haben KI" trägt gegen Lio nicht. Tragfähig ist die Kombination, die Lio und
Procure Ai nicht bedienen: KI-Agenten **plus** vollständiger P2P-Prozess inklusive
Rechnung und Vertrag **plus** Einführung in Stunden statt Wochen, für Unternehmen
ohne eigenes Procurement-Team. Diese drei Punkte gehören zusammen auf eine Seite,
mit Beleg statt Behauptung.

## Quellen

- [simple system Startseite (DE)](https://www.simplesystem.com/de/)
- [simple system Unternehmensseite (EN)](https://en.company.simplesystem.com/)
- [simple system: Warum wir jetzt Preise zeigen](https://simplesystem.com/magazin/preise-bei-simple-system)
- [simple system: Beschaffungsplattform](https://simplesystem.com/magazin/beschaffungsplattform)
- [simple system: E-Procurement Software Comparison 2026](https://simplesystem.com/en/magazin/e-procurement-software-comparison)
- [simple system: B2B Handelsplattform](https://company.simplesystem.com/en/magazin/b2b-handelsplattform)
- [simple system: C-Teile-Management Definition](https://company.simplesystem.com/en/magazin/c-teile-management-definition)
- [OMR Reviews: simple system](https://omr.com/en/reviews/product/simple-system)
- [nexoma: Was ist simple system?](https://nexoma.de/simple-system/)
- [windmuehlenbauer: simple system für Lieferanten](https://windmuehlenbauer.com/simple-system/)
- [beschaffung aktuell: Erweitertes Dashboard für indirekte Beschaffung](https://beschaffung-aktuell.industrie.de/c-teile-management/simple-system-bietet-erweitertes-dashboard-fuer-indirekte-beschaffung/)
- [Presseportal: simple system GmbH & Co. KG](https://www.presseportal.de/nr/146850)
- [Capterra Deutschland: Hivebuy](https://www.capterra.com.de/software/1027395/hivebuy)
- [OMR Reviews: Hivebuy](https://omr.com/en/reviews/product/hivebuy)
- [trusted.de: Hivebuy im Test](https://trusted.de/hivebuy)
- [Softwareabc24: Hivebuy Bewertungen und Preise](https://www.softwareabc24.de/einkauf-und-beschaffung-software/hivebuy)
- [Leipziger Zeitung: Wie Hivebuy den Einkauf im Mittelstand revolutioniert](https://www.l-iz.de/wirtschaft/2026/01/hivebuy-einkaufssoftware-beschaffungsprozesse-einfach-digitalisieren-646259)
- [Wirtschaft in Sachsen: Erfahrungen mit Hivebuy](https://www.wirtschaft-in-sachsen.de/de/hivebuy-erfahrungen-was-steckt-hinter-der-beliebten-einkaufssoftware/)
- [Procure Ai: Agentic Procurement Automation Platform](https://www.procure.ai/platform)
- [Gartner Peer Insights: Procure Ai](https://www.gartner.com/reviews/product/procure-ai)
- [Capterra: Procure Ai](https://www.capterra.com/p/10016095/Procure-Ai/)
- [GetApp: Procure Ai](https://www.getapp.com/operations-management-software/a/procure-ai/)
- [Beschaffung aktuell: askLio sammelt 30 Mio. USD ein und heißt jetzt Lio](https://beschaffung-aktuell.industrie.de/artikel/asklio-sammelt-30-mio-usd-ein-und-heisst-jetzt-lio/)
- [Y Combinator: Lio (formerly askLio)](https://www.ycombinator.com/companies/lio)
- [Munich Startup: Lio raises 25.7 million euros](https://www.munich-startup.de/en/117802/lio-raises-25-million-euros/)
