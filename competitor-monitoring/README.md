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

Eingerichtet als Routine (serverseitig, überlebt das Session-Ende) mit dem Prompt
aus `PROMPT.md`:

| Einstellung | Wert |
|---|---|
| Trigger | wöchentlich montags 06:07 UTC (08:07 MESZ, 07:07 MEZ) |
| Effektiver Takt | 14-tägig, über die 10-Tage-Sperre in `PROMPT.md` |
| Beobachtet | simple system, Onventis, Precoro, Procure Ai, Lio, dazu hivebuy.com als Referenz |
| Bericht | `reports/<datum>-monitoring.md`, committet und gepusht |
| Notion | Unterseite unter [Wettbewerbs-Monitoring](https://app.notion.com/p/3c06f8c1d67e810ca8edd264c4139505) |
| Slack | DM an Moritz Lienert (`U071B33N4LQ`), nur bei echten Änderungen |

Routine-ID: `trig_01PQsJdUUmm6U7LXvqG3bkB8`, erster Lauf 2026-08-24 06:07 UTC.

Cron kennt kein "jede zweite Woche". Deshalb feuert der Trigger wöchentlich und
der Lauf bricht selbst ab, wenn der letzte Bericht jünger als 10 Tage ist. Wer
den Takt ändern will, ändert entweder die Cron-Expression der Routine oder die
Sperre in `PROMPT.md`.

### ⚠️ Offen: Connectors für die Routine

Die Routine wurde ohne gespeicherte MCP-Connectors angelegt, weil diese Umgebung
keine Connector-Grants weitergeben darf. Die gefeuerten Sessions haben damit
**keinen Notion- und keinen Slack-Zugriff**: Bericht und Snapshots landen im Repo,
die Kurzfassung in Notion und die Slack-DM bleiben aus.

Zwei Wege, das zu lösen:

1. In den Routines-Einstellungen auf claude.ai die Routine
   "Wettbewerbs-Monitoring Hivebuy (14-tägig)" öffnen und Notion sowie Slack als
   Connectors ergänzen.
2. Oder die Routine dort neu anlegen, mit dem Prompt aus `PROMPT.md` und den
   Connectors Notion und Slack. Dann die bestehende Routine löschen.

Bis dahin bleibt der Bericht im Repo die verlässliche Ausgabe.

Alternativ ad hoc in einer laufenden Session: `/competitor-scan`.

## Grenzen, bewusst so gesetzt

- Nur öffentlich zugängliche Seiten, keine Logins, keine Umgehung von
  Zugangsbeschränkungen, moderate Crawl-Rate.
- Kein Abruf von Preisen, die nur nach Kontaktaufnahme sichtbar sind.
- Zahlen aus Marketingtexten der Wettbewerber werden als Behauptung zitiert,
  nicht als Fakt.
