# Wettbewerbs-Monitoring

Wiederholbarer Scan von Wettbewerber-Websites, Vergleich mit hivebuy.com,
Änderungsverfolgung über Zeit.

## Was das Setup kann

| Fähigkeit | Status |
|---|---|
| Seiten einer Domain systematisch erfassen (Sitemap + Link-Crawl) | ✅ Skript vorhanden |
| Pro Seite Title, Meta, H1/H2, Wortzahl, Schema.org, hreflang, Preisnennungen, Text-Hash | ✅ |
| Änderungen zwischen zwei Läufen als Diff (neu / entfernt / geändert) | ✅ |
| Screenshots der Kernseiten | ✅ (`--screenshots`, benötigt Playwright) |
| Bewertung und Vergleich mit Hivebuy, Handlungsempfehlungen | ✅ durch Claude, Basis sind die Snapshots |
| Presse, Finanzierung, Reviews, Vergleichsartikel | ✅ per Websuche |
| Traffic-, Keyword- und Backlink-Zahlen der Wettbewerber | ❌ nur mit Semrush/Ahrefs-API (nicht angebunden) |
| Inhalte hinter Login, Demo-Umgebungen, Preise auf Anfrage | ❌ bewusst nicht |

## Voraussetzung: Netzwerkzugang

Der Crawler braucht ausgehenden Netzwerkzugang auf die Zieldomains. In einer
Claude-Code-Umgebung mit restriktiver Netzwerk-Policy schlagen alle Abrufe mit
`EGRESS_BLOCKED` fehl. Dann in den Environment-Einstellungen die Netzwerk-Policy
so setzen, dass mindestens diese Hosts erreichbar sind:

```
hivebuy.com, www.hivebuy.com,
simplesystem.com, company.simplesystem.com,
onventis.com, precoro.com,
omr.com, capterra.com.de, trusted.de, g2.com
```

Doku: https://code.claude.com/docs/en/claude-code-on-the-web

Ohne Egress bleibt nur suchmaschinenbasiertes Monitoring: deutlich gröber,
keine Diffs, keine Preis- oder Title-Verfolgung.

## Playwright (empfohlen)

Einige Zielseiten (u. a. hivebuy.com selbst) blocken Nicht-Browser-User-Agents
über Cloudflare mit 403. Mit Playwright läuft der Abruf über echtes Chromium und
kommt durch, außerdem wird JS-gerendertes Markup erfasst.

```bash
npm install playwright        # Chromium liegt in Claude-Code-Umgebungen bereits unter /opt/pw-browsers
```

Ist `playwright` nicht installiert, fällt der Crawler automatisch auf `fetch()`
mit Browser-User-Agent zurück und protokolliert das im Snapshot (`fetchMode`).

## Nutzung

```bash
# Einzelne Site erfassen
node competitor-monitoring/scripts/crawl.mjs --site simplesystem --max-pages 150

# Alle Sites aus der Registry, mit Screenshots der Kernseiten
node competitor-monitoring/scripts/crawl.mjs --all --screenshots

# Änderungen seit dem letzten Lauf
node competitor-monitoring/scripts/diff.mjs --site simplesystem

# Bestimmte Läufe vergleichen, maschinenlesbar
node competitor-monitoring/scripts/diff.mjs --site simplesystem --from 2026-08-18 --to 2026-09-01 --json
```

Optionen von `crawl.mjs`: `--site <id>` | `--all`, `--max-pages` (Default 120),
`--delay-ms` (Default 700), `--screenshots`, `--out <dir>`, `--config <file>`,
`--date <YYYY-MM-DD>`.

## Dateien

```
competitors.json      Registry: Domains, Hosts, Sitemaps, Kernseiten, Review-Profile
scripts/crawl.mjs     Crawler, schreibt snapshots/<site>/<datum>.json
scripts/diff.mjs      Vergleich zweier Snapshots als Markdown oder JSON
PROMPT.md             Standing Prompt für den geplanten Lauf (Routine/Cron)
REPORT_TEMPLATE.md    Struktur der Berichte
snapshots/<site>/     Rohdaten pro Lauf (versioniert, damit Diffs möglich sind)
reports/              Berichte pro Lauf
```

## Wettbewerber ergänzen

Eintrag in `competitors.json` anlegen: `id`, `name`, `hosts` (alle Subdomains,
die zur Site gehören), `bases` (Startpunkte), `sitemaps`, `keyPages`
(Home/Pricing/Produkt, werden immer erfasst und für Screenshots genutzt),
`reviewProfiles`, `excludePatterns`.

## Regelmäßiger Lauf

Der Zeitplan läuft als Routine (serverseitig, überlebt das Session-Ende) mit dem
Prompt aus `PROMPT.md`. Empfehlung: 14-tägig, Montagvormittag. Wöchentlich
lohnt sich nur, wenn die Wettbewerber ihre Seiten wirklich häufig ändern, sonst
sind die Berichte leer.

Alternativ ad hoc in einer laufenden Session: `/competitor-scan`.

## Grenzen, bewusst so gesetzt

- Nur öffentlich zugängliche Seiten, keine Logins, keine Umgehung von
  Zugangsbeschränkungen, moderate Crawl-Rate.
- Kein Abruf von Preisen, die nur nach Kontaktaufnahme sichtbar sind.
- Zahlen aus Marketingtexten der Wettbewerber werden als Behauptung zitiert,
  nicht als Fakt.
