---
name: competitor-scan
description: Wettbewerbs-Scan für Hivebuy ausführen - Wettbewerber-Websites crawlen, mit dem letzten Snapshot vergleichen, Bericht gegen hivebuy.com schreiben. Nutzen, wenn nach Wettbewerbsanalyse, Competitor-Monitoring, Änderungen bei simple system / Onventis / Precoro oder einem Vergleich mit hivebuy.com gefragt wird.
---

# Wettbewerbs-Scan

Führe den Scan gemäß `competitor-monitoring/PROMPT.md` aus. Kurzform:

1. `competitor-monitoring/competitors.json` lesen.
2. Pro Site: `node competitor-monitoring/scripts/crawl.mjs --site <id> --max-pages 150`.
   Bei `EGRESS_BLOCKED` abbrechen und dem Nutzer sagen, dass die Netzwerk-Policy
   der Umgebung die Zieldomains freigeben muss (siehe `competitor-monitoring/README.md`).
3. Pro Site mit Vorlauf: `node competitor-monitoring/scripts/diff.mjs --site <id>`.
4. Websuche für Presse, Finanzierung, Reviews, Vergleichsartikel.
5. Bericht nach `competitor-monitoring/reports/<YYYY-MM-DD>-monitoring.md`
   in der Struktur von `REPORT_TEMPLATE.md`, jede Aussage mit Quelle.
6. Snapshots und Bericht committen und pushen.

Argument `$1` (optional): einzelne Site-ID, dann nur diese scannen.
