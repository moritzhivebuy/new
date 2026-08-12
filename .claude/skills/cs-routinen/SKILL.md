---
name: cs-routinen
description: Wiederkehrende Customer-Success-Auswertungen aus HubSpot als Markdown-Brief. Routine 3 (Renewals, Kündigungsfristen, Vertragsdaten-Lücken) ist gebaut; Routine 1 (Engagement) und 2 (Tickets) folgen. Verwenden, wenn nach Renewals, auslaufenden Verträgen, Kündigungsfristen, dem CS-Brief oder Kunden ohne gepflegtes Vertragsende gefragt wird.
---

# CS-Routinen

Auswertungen über die aktive Kundenbasis in HubSpot. Jede Routine ist ein
Skript, das einen Markdown-Block nach `output/` schreibt. Die Blöcke lassen sich
zu einem gemeinsamen `output/YYYY-MM-DD-cs-brief.md` zusammensetzen, sobald mehr
als eine Routine existiert.

## Stand

| Routine | Skript | Status |
|---|---|---|
| 3 — Renewals | `scripts/renewals.py` | gebaut, gegen Live-Daten geprüft |
| 2 — Tickets | `scripts/tickets.py` | offen (Trend + Aging-Liste, reine Aggregation) |
| 1 — Engagement | `scripts/engagement.py` | offen (4 Quellen, Merge, Ampellogik) |

Reihenfolge bewusst so: Routine 3 hat den kleinsten Scope und deckt die
Datenlücken auf, die den Wert der anderen beiden begrenzen. Routine 1 zuletzt,
weil sie Merge-Logik über vier Quellen braucht und davon profitiert, dass die
Owner-Bereinigung bis dahin läuft.

## Routine 3 ausführen

```bash
cd .claude/skills/cs-routinen
python3 scripts/renewals.py                       # heute, 90-Tage-Fenster
python3 scripts/renewals.py --as-of 2026-08-12     # reproduzierbarer Stichtag
python3 scripts/renewals.py --window-days 180      # breiteres Fenster
python3 scripts/renewals.py --stdout --no-state    # Testlauf, ohne zu schreiben
```

Schreibt `output/<Stichtag>-renewals.md` und fortschreibt
`output/.renewals-state.json` (Grundlage für den Neueintritts-Alert).

**Cadence: wöchentlich.** Zusätzlich bei jedem Lauf ein Alert-Block für Kunden,
die neu in das Fenster oder neu in die Kündigungsfrist eingetreten sind. Beim
allerersten Lauf ohne State-Datei gibt es absichtlich keinen Alert, statt die
komplette Liste als "neu" zu melden.

## Nach Notion veröffentlichen

Die Reports liegen in Notion unter
[CS-Reports](https://app.notion.com/p/3ba6f8c1d67e817984a1ea4630d1087f)
(Unterseite von *New: Customer Success*), eine datierte Unterseite pro Lauf.

Notion kennt keine Pipe-Tabellen. `scripts/notion_export.py` übersetzt einen
Brief in Notion-flavored Markdown (`<table>`-Blöcke, Tabs statt Leerzeichen,
`*kursiv*` statt `_kursiv_`):

```bash
python3 scripts/notion_export.py output/2026-08-12-renewals.md --strip-h1
```

Die Ausgabe geht als `content` an `mcp__Notion__notion-create-pages`, Parent ist
die Seite `3ba6f8c1-d67e-8179-84a1-ea4630d1087f`, Titel im Format
`YYYY-MM-DD — Renewals`. `--strip-h1` entfernt die H1, weil Notion den
Seitentitel schon als Überschrift zeigt.

## Datenzugriff

`scripts/hubspot.py` kapselt beides; die Routinen sehen keinen Unterschied.

1. **API-Modus** (bevorzugt): `HUBSPOT_PRIVATE_APP_TOKEN` oder
   `HUBSPOT_ACCESS_TOKEN` gesetzt → CRM-Search-API mit Paging und Retry
   (4 Versuche, 2/4/8/16 s, `Retry-After` beachtet). Für den wöchentlichen Lauf
   der richtige Weg.
2. **MCP-Cache-Modus** (ohne Token): Query `active_customers` aus
   `references/queries.md` per `mcp__HubSpot__query_crm_data` ausführen, die
   Tool-Antwort **unverändert** nach `data/active_customers.json` schreiben,
   dann das Skript starten. `parse_mcp_results` versteht die rohe MCP-Antwort,
   `{"results": [{"properties": …}]}` und eine flache Liste.

Fehlen Token *und* Cache, bricht das Skript mit genau diesem Hinweis ab statt
mit einem Stacktrace.

## Fachliche Festlegungen

* **Basisabfrage**: `lifecyclestage = 'customer' AND churn_date IS NULL`, genau
  einmal implementiert in `hubspot.active_customers()`. Keine Routine formuliert
  sie neu.
* **Ausschlussliste** `hubspot.NON_CUSTOMERS`: Companies, die im CRM als Kunde
  getaggt sind, fachlich aber keine sind (aktuell d.velop). Sie fallen vor jeder
  MRR-Summe heraus und werden im Block *Datenqualität* mit Begründung
  ausgewiesen. Jeder Eintrag ist eine Umgehung falscher CRM-Daten und gehört an
  der Quelle korrigiert, nicht dauerhaft in diese Liste.
* **Kein Zeitfenster in SQL.** Die Fenster entstehen in Python. Filtert man in
  SQL, verschwinden die Kunden mit leerem oder abgelaufenem `contract_end_date`
  aus dem Ergebnis — also ein Drittel der Kundenbasis.
* **`contract_end_date` ist das Vertragsende, nicht der Kündigungsstichtag.**
  Der Entscheidungszeitpunkt ist `contract_end_date` minus
  `hubspot.NOTICE_PERIOD_MONTHS` (aktuell **3**, eine Annahme). Ein Feld für die
  Frist existiert in HubSpot nicht. Sobald die Standardfrist verbindlich
  geklärt ist: Konstante anpassen, sonst nichts.
* Deshalb hat der Brief **zwei** Fensterblöcke: Block 1 (Vertragsende in 90
  Tagen) und Block 1b (Frist läuft in 90 Tagen ab, Vertragsende dahinter).
  Block 1b ist der operativ nutzbare — bei drei Monaten Frist ist die
  Entscheidung für alles in Block 1 längst gefallen. Das ist die
  Fenstererweiterung auf faktisch 180 Tage, ohne die ursprüngliche Liste zu
  verlieren.
* **Blöcke 2 und 3 sind nicht optional.** Abgelaufene und fehlende
  Vertragsdaten gehören in jeden Brief, sonst liest sich Block 1 wie eine
  vollständige Risikoliste.
* Die Spalte *Fortschreibung* (`contract_start_date + n × contract_duration_months_`)
  ist ein Vorschlag zur Nachpflege, kein CRM-Fakt, und wird auch so ausgewiesen.

## Output-Konventionen

* Deutsch, Zahlen deutsch formatiert (`1.110,84`), Datum `TT.MM.JJJJ`.
* Jeder Block: Tabelle, darunter eine Summenzeile mit MRR und Anteil an der
  Gesamtbasis.
* Jeder Brief endet mit **Datenqualität**: wie viele Kunden und wie viel MRR
  ohne belastbares Vertragsende, fehlende MRR-Werte, fehlende und inaktive
  Owner, Dublettenverdacht.
* Kein Wert wird geschätzt. Fehlt etwas, steht `-` oder
  `nicht berechenbar` — nicht `0`.
* Anteilsangaben immer gegen `hubspot.total_mrr()`, damit Prozentwerte über
  Blöcke und Routinen vergleichbar bleiben.
* **Jeder Kunde und jeder Deal wird verlinkt**, auf den HubSpot-Record über
  `hs.company_url()` / `hs.deal_url()`. Auch in den Aufzählungen der
  Datenqualität, damit man von jedem Befund direkt in den Record springt.

## Voraussetzungen außerhalb von Claude Code

Diese Punkte begrenzen den Wert der Routinen unabhängig von der
Implementierung. Die Routine misst sie bei jedem Lauf mit, lösen kann sie sie
nicht.

1. `contract_end_date` für die Kunden ohne gültiges Datum nachpflegen,
   idealerweise per HubSpot-Workflow aus `contract_start_date` +
   `contract_duration_months_` automatisch fortschreiben. Block 2 und 3 des
   Briefs sind die Arbeitsliste dafür, Spalte *Fortschreibung* der Vorschlag.
2. **Teilweise erledigt (12.08.2026):** Die *Company*-Zuordnung liegt jetzt bei
   **Bettina Fischer** (109171979, aktiv) mit 61 aktiven Kunden. Die *Deals*
   sind nicht mitumgezogen: 36 der 40 offenen Deals an aktiven Kunden laufen
   weiter auf Jan Vollers (34) und Kinga Chmurczyk (2). Ebenfalls offen: 8
   Kunden ganz ohne `hubspot_owner_id`. Der Report weist beides aus.
3. Companies mit `lifecyclestage = 'customer'` **und** gesetztem `churn_date`
   auf einen eigenen Lifecycle-Wert setzen, damit die Basisabfrage nicht
   dauerhaft von einem Zusatzfilter abhängt.
4. Dubletten bereinigen (igus, JMarquardt Audiovisual, rebuy / reBuy
   reCommerce). Der Brief listet den Verdacht unter *Datenqualität*.
5. `lifecyclestage` von **d.velop** korrigieren, steht im CRM noch auf
   `customer`. Bis dahin greift `NON_CUSTOMERS`.
6. Standard-Kündigungsfrist verbindlich klären. Aktuell drei Monate angenommen,
   ein Feld dafür existiert in HubSpot nicht.

Punkt 1 vor dem Bau von Routine 1 erledigen, der Rest kann parallel laufen.

## Gemeinsames Modul

`scripts/hubspot.py`:

| Funktion | Zweck |
|---|---|
| `active_customers()` | Basisabfrage, memoisiert, normalisierte Zeilen |
| `run_sql(sql, cache_key)` | API-Modus oder Cache, mit Retry |
| `search_companies(filter_groups)` | gepaginierte Search-API |
| `owner_info()` | Owner-ID → Name + `active`, inkl. archivierter Owner |
| `total_mrr()` | MRR-Basis für alle Anteilsangaben |
| `ms_to_days` / `ms_to_hours` / `ms_to_date` | Millisekunden-Konvertierung |
| `to_float` / `to_int` | robuste Zahlen (leerer String → `None`) |
| `norm_name` | `html.unescape` + Whitespace + `strip` + `lower`, für Joins |
| `dedupe_key` | aggressiver, nur für Dubletten-Erkennung |
| `add_months` / `days_between` | Fristenrechnung |
| `fmt_eur` / `fmt_date` / `fmt_pct` | deutsche Formatierung |
| `SUPPORT_PIPELINE = '0'` | harte Konstante für Routine 2 |
| `NOTICE_PERIOD_MONTHS = 3` | angenommene Kündigungsfrist |
| `NON_CUSTOMERS` | Ausschlussliste falsch getaggter Companies |
| `excluded_non_customers()` | die Ausgeschlossenen samt Begründung |
| `deals()` / `deals_by_company()` | Deals inkl. Company-Verknüpfung |
| `association_company_ids()` | Company-IDs eines Deals, dedupliziert |
| `pipeline_labels()` / `stage_label()` | Stage-IDs in lesbare Labels |
| `company_url()` / `deal_url()` / `md_link()` | Record-Links |

Neue Routinen bauen darauf auf und ergänzen `hubspot.py` statt eigene
Konvertierungen mitzubringen.

## Struktur

```
cs-routinen/
  SKILL.md
  references/
    datenmodell.md      # Properties, Fallen, bekannte Lücken
    queries.md          # alle SQL-Statements, benannt
  scripts/
    hubspot.py          # gemeinsamer Zugriff, Konvertierung, Normalisierung
    renewals.py         # Routine 3
    notion_export.py    # Brief -> Notion-flavored Markdown
  data/                 # MCP-Cache (gitignored), owners.json optional
  output/               # Briefs + Alert-State
```
