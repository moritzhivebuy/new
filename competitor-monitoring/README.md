# Wettbewerbs-Monitoring

Wiederholbarer Scan von Wettbewerber-Websites, Vergleich mit hivebuy.com,
Änderungsverfolgung über Zeit.

## Was das Setup kann

| Fähigkeit | Status |
|---|---|
| Seiten einer Domain systematisch erfassen (Sitemap + Link-Crawl) | ✅ Skript vorhanden |
| Pro Seite Title, Meta, H1/H2, Wortzahl, Schema.org, hreflang, Preisnennungen, Text-Hash | ✅ |
| Änderungen zwischen zwei Läufen als Diff (neu / entfernt / geändert) | ✅ |
| Screenshots: ganze Seiten und einzelne Ausschnitte per Selektor | ✅ getestet, benötigt Playwright |
| Screenshots in Notion ablegen | ⚠️ implementiert, Upload braucht erreichbares `api.notion.com` |
| robots.txt auswerten und gesperrte Pfade auslassen | ✅ |
| Bewertung und Vergleich mit Hivebuy, Handlungsempfehlungen | ✅ durch Claude, Basis sind die Snapshots |
| Presse, Finanzierung, Reviews, Vergleichsartikel | ✅ per Websuche |
| Traffic-, Keyword- und Backlink-Zahlen der Wettbewerber | ❌ nur mit Semrush/Ahrefs-API (nicht angebunden) |
| Inhalte hinter Login, Demo-Umgebungen, Preise auf Anfrage | ❌ bewusst nicht |

## Voraussetzung: Netzwerkzugang

Der Crawler braucht ausgehenden Netzwerkzugang auf die Zieldomains. Ist die
Netzwerk-Policy der Umgebung zu eng, scheitern alle Abrufe mit `EGRESS_BLOCKED`.

Einstellen auf [claude.ai/code](https://claude.ai/code): über dem Eingabefeld auf
das Cloud-Symbol mit dem Umgebungsnamen klicken, in der Liste über die Umgebung
fahren, das Zahnrad rechts anklicken. Im Dialog **Network access** auf **Custom**
stellen, die Domains unten in **Allowed domains** einfügen und
**Also include default list of common package managers** aktivieren, sonst
schlägt `npm install` fehl und es gibt keine Screenshots.

Die Routine läuft in der Umgebung `env_01UiCq4EiQcZ6ZrjiHm5mR52` ("Hubspot"),
diese Umgebung muss die Freigabe bekommen.

```text
hivebuy.com
*.hivebuy.com
simplesystem.com
*.simplesystem.com
onventis.com
*.onventis.com
precoro.com
*.precoro.com
procure.ai
*.procure.ai
lio.ai
*.lio.ai
asklio.ai
*.asklio.ai
omr.com
*.omr.com
capterra.com
*.capterra.com
capterra.com.de
*.capterra.com.de
trusted.de
*.trusted.de
g2.com
*.g2.com
gartner.com
*.gartner.com
getapp.com
*.getapp.com
api.notion.com
```

Ein führendes `*.` deckt nur Subdomains ab, deshalb steht jede Domain zweimal in
der Liste. `api.notion.com` wird für den Screenshot-Upload nach Notion gebraucht:
der läuft über das Netzwerk der Session. Der normale Notion- und Slack-Zugriff
über die Connectors läuft daran vorbei und braucht keine Freigabe.

Änderungen greifen erst für **neu gestartete** Sessions, eine laufende Session
behält ihre Policy. Der nächste Routine-Lauf zieht sie also automatisch, für einen
sofortigen Test eine neue Session öffnen und dort `/competitor-scan` aufrufen.

Doku: https://code.claude.com/docs/en/cloud-environments#access-levels

Ohne Freigabe bleibt nur suchmaschinenbasiertes Monitoring: deutlich gröber,
keine Diffs, keine Screenshots, keine Preis- oder Title-Verfolgung.

## Playwright (empfohlen)

Einige Zielseiten (u. a. hivebuy.com selbst) blocken Nicht-Browser-User-Agents
über Cloudflare mit 403. Mit Playwright läuft der Abruf über echtes Chromium und
kommt durch, außerdem wird JS-gerendertes Markup erfasst.

```bash
npm install        # installiert playwright, Chromium liegt bereits unter /opt/pw-browsers
```

Ist `playwright` nicht installiert, fällt der Crawler automatisch auf `fetch()`
mit Browser-User-Agent zurück und protokolliert das im Snapshot (`fetchMode`).
Dann gibt es allerdings keine Screenshots.

Passt die Chromium-Build-Nummer von Playwright nicht zu der in der Umgebung
vorhandenen (kommt vor, weil beide unabhängig aktualisiert werden), sucht der
Crawler die vorhandene Binary selbst unter `$PLAYWRIGHT_BROWSERS_PATH` und
protokolliert, welche er nutzt. Über `PLAYWRIGHT_CHROMIUM_PATH` lässt sich ein
Pfad erzwingen.

## Screenshots

Pro Site definiert `shots` in `competitors.json`, was aufgenommen wird:

```json
{ "name": "preis-tabelle", "url": "https://…/preise", "selector": "table" }
```

- ohne `selector`: ganze Seite, mit `selector`: nur dieser Ausschnitt
- erlaubt sind CSS-Selektoren und Playwright-Selektoren wie `text=Preise` oder
  `text=/pro Nutzer/i`
- `hideSelectors` blendet vor der Aufnahme Elemente aus, etwa Cookie-Banner
- ohne `shots` wird von jeder `keyPage` die ganze Seite aufgenommen

Ablage: `snapshots/<site>/screenshots/<datum>/<name>.png`, dazu ein Eintrag pro
Shot im Snapshot-JSON. Abschalten mit `--no-screenshots`.

Selektoren gegen fremde Seiten sind nicht dauerhaft verlässlich, ein Redesign
bricht sie. Ein fehlgeschlagener Shot ist im Snapshot als `error` vermerkt und
stoppt den Lauf nicht. Die aktuell hinterlegten Ausschnitts-Selektoren
(`table`, `h1`, Text-Anker) sind ungetestet, weil in dieser Umgebung kein
Netzwerkzugang bestand: beim ersten echten Lauf prüfen und nachziehen.

## robots.txt

Der Crawler lädt robots.txt pro Origin, wertet die Blöcke für `*` aus und ruft
gesperrte Pfade nicht ab. Übersprungene URLs stehen als `robotsSkipped` im
Snapshot, die erkannten Regeln unter `robots`. Crawl-Pause: 700 ms, anpassbar
über `--delay-ms`.

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

### Connectors der Routine

Erledigt: die Routine hat Notion, Slack und HubSpot angebunden (Stand 2026-08-18,
bestätigt über `mcp_connections` der Routine). Damit kann der geplante Lauf die
Notion-Seite anlegen und die Slack-DM schicken.

Hinweis für später: Connectors lassen sich nur von einem Menschen in den
Routines-Einstellungen auf claude.ai setzen. Der `connectors`-Parameter beim
Anlegen per Werkzeug ist für diese Organisation nicht freigegeben.

## Grenzen, bewusst so gesetzt

- Nur öffentlich zugängliche Seiten, keine Logins, keine Umgehung von
  Zugangsbeschränkungen, moderate Crawl-Rate, robots.txt wird respektiert.
- Kein Abruf von Preisen, die nur nach Kontaktaufnahme sichtbar sind.
- Zahlen aus Marketingtexten der Wettbewerber werden als Behauptung zitiert,
  nicht als Fakt.

## Was noch fehlt

| Lücke | Was es bräuchte |
|---|---|
| Netzwerkzugang auf die Zieldomains | Netzwerk-Policy der Environment anpassen. Ohne das: keine Crawls, keine Diffs, keine Screenshots |
| Traffic, Keyword-Rankings, Backlinks der Wettbewerber | Semrush- oder Ahrefs-API-Key. Ohne das bleibt Sichtbarkeit qualitativ |
| Eigene Ranking- und Klickdaten als Gegenstück | Search Console anbinden. Der Google-Ads-Connector in diesem Setup ist unautorisiert und liefert nichts |
| Review-Zeitreihen (OMR, Capterra, G2, Gartner) | Diese Portale blocken Crawler oft. Erst nach dem ersten echten Lauf beurteilbar, notfalls manuell pflegen |
| Vertriebssicht: gegen wen wird verloren und warum | HubSpot ist angebunden, Deal- und Verlustgründe ließen sich pro Lauf gegen die Website-Signale stellen. Bisher nicht Teil des Scans |
| Wettbewerber-Besuche auf hivebuy.com | Leadfeeder ist angebunden und könnte zeigen, welche Wettbewerber die eigene Seite ansehen. Bisher nicht Teil des Scans |
| Repo-Größe über die Zeit | Snapshots und PNGs wachsen pro Lauf. Nach etwa einem Jahr aufräumen oder ältere Läufe ausdünnen |
