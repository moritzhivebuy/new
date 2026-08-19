---
name: impact-ladder-pdf
description: Erstellt aus Gesprächsnotizen automatisch eine kundenspezifische Impact Ladder als PDF im Hivebuy-Design. Diese Skill wird IMMER automatisch ausgeführt, nachdem die Follow-up-E-Mail aus Gesprächsnotizen erstellt wurde. Sie triggert auch, wenn der Nutzer "Impact Ladder", "Impact Letter", "Kunden-PDF" oder "Gesprächs-Follow-up mit PDF" erwähnt. Das PDF-Design ist fest vorgegeben und darf nicht verändert werden: Inhalte kommen aus einer JSON-Datei, das Layout aus einem fixen HTML-Template.
---

# Skill: Impact Ladder PDF (Hivebuy)

## Zweck

Nach jedem Kundengespräch entsteht zusätzlich zur Follow-up-E-Mail eine Impact Ladder als PDF im Hivebuy-Design. Das PDF zeigt dem Kunden, welche konkreten Vorteile Hivebuy auf vier Ebenen bringt: Mitarbeitende, Einkauf, Finance, Management.

**Grundprinzip für identisches Design:** Claude erzeugt NIEMALS eigenes Layout, eigene Farben oder eigene CSS-Anpassungen. Claude erzeugt ausschließlich eine JSON-Datei mit Inhalten. Das Rendering übernimmt ein fixes Template plus Skript. So ist jedes PDF designidentisch.

## Ordnerstruktur

```
.claude/skills/impact-ladder-pdf/
├── SKILL.md                  (diese Datei)
├── template/
│   └── template.html         (fixes Layout, NIE inhaltlich anpassen)
├── assets/
│   ├── logo-hivebuy-white.svg
│   └── fonts/
│       ├── FrankRuhlLibre-Regular.woff2
│       ├── DMSans-Regular.woff2
│       ├── DMSans-Medium.woff2
│       └── DMSans-Bold.woff2
├── scripts/
│   └── render.js
└── output/
```

**Setup (einmalig, in diesem Repo bereits erledigt):**

```bash
cd .claude/skills/impact-ladder-pdf && npm install puppeteer handlebars
```

---

## Workflow (immer in dieser Reihenfolge)

1. **Analyse:** Gesprächsnotizen nach den Analyse-Regeln unten auswerten.
2. **JSON erzeugen:** Inhalte in `output/<kunde-slug>-impact-ladder.json` schreiben (Schema unten).
3. **Rendern:** `node scripts/render.js output/<kunde-slug>-impact-ladder.json`
4. **QA:** Checkliste unten durchgehen, PDF einmal öffnen bzw. rendern und Seitenumbrüche prüfen.
5. **Übergabe:** Pfad des PDFs zusammen mit der Follow-up-E-Mail ausgeben.

---

## Schritt 1: Analyse-Regeln

1. Extrahiere die 4 bis 6 wichtigsten aktuellen Optimierungspotenziale aus Status quo, Pain Points und Prozessbeschreibung.
2. Ordne die passenden Hivebuy-Lösungen den vier Ebenen zu:
   - Mitarbeitende / Bedarfsträger
   - Einkauf / Administration
   - Finance / Controlling
   - Geschäftsführung / Management
3. Formuliere je Ebene ausschließlich konkrete Hivebuy-Vorteile, keine Wiederholung des Status quo.
4. Pro Ebene maximal 2 bis 3 kurze Bulletpoints plus ein prägnanter Business Impact.
5. Übersetze Features immer in Wirkung: Feature, dann Prozessverbesserung, dann wirtschaftlicher oder strategischer Nutzen.
6. Priorisiere nach den im Gespräch genannten Pain Points. Keine generischen Vorteile ergänzen, die nicht zum Kunden passen.
7. Nutze vorhandene Zahlen (Bestellvolumen, Standorte, Rechnungen, Nutzer, Zeitaufwand), um den Management-Impact zu konkretisieren.
8. Trenne belegte Fakten von Annahmen. Unbekannte Einsparungen nie als sicher darstellen. Jede Zahl bekommt den Status `belegt` (aus den Notizen) oder `annahme`.
9. Schreibe kurz, verständlich und präsentationstauglich: ein Gedanke pro Bullet, keine langen Nebensätze.

### Sprach- und Markenregeln (verbindlich)

- Sprache: Deutsch, professionelles "Sie".
- Keine Gedankenstriche (em dash, en dash, Doppelbindestrich). Stattdessen Komma, Punkt oder Doppelpunkt.
- Keine Boilerplate-Claims ohne Datenbasis (z. B. pauschale ROI- oder Prozentwerte). Nur Zahlen aus den Gesprächsnotizen oder klar als Annahme markiert.
- Keine Querverweise auf andere Hivebuy-Kunden im PDF.
- Keine namentlichen Lieferanten wie Amazon. Stattdessen generisch: "Punch-out-Kataloge".
- Keine Buzzwords ("revolutionär", "next-gen", "Synergien").

### Offizielle Hivebuy-Agentennamen (bei Lösungszuordnung verwenden)

**Bedarfsanforderung:** Intake Agent, Recommendation Agent, Category Agent, Contract Agent, Savings Agent, Slack Agent, MS Teams Agent, Comparison Agent, Status Agent, Customer Support Agent, Parsing Agent.

**Backoffice:** Approval Agent, Analytics Agent, Data Enrichment Agent.

**Rechnungsmanagement:** Invoice Agent, Compliance Agent, Accounting Agent.

Regel: Agenten nur nennen, wenn sie zum jeweiligen Pain Point passen. Im Bullet zuerst der Nutzen, der Agentenname in Klammern oder als Halbsatz.

---

## Schritt 2: JSON-Schema

Datei: `output/<kunde-slug>-impact-ladder.json`. Alle Felder sind Pflicht, außer als optional markiert.

```json
{
  "customer": {
    "name": "Beispiel GmbH",
    "ansprechpartner": "Max Mustermann",
    "gespraechsdatum": "12.08.2026"
  },
  "date": "19.08.2026",
  "potenziale": [
    {
      "titel": "Kein Echtzeit-Budgetüberblick",
      "beschreibung": "Budgets werden erst nach Rechnungseingang sichtbar, Überschreitungen fallen zu spät auf."
    }
  ],
  "ladder": [
    {
      "nummer": 1,
      "ebene": "Mitarbeitende / Bedarfsträger",
      "bullets": [
        "Bedarfe direkt in MS Teams anfragen, ohne Systemwechsel (MS Teams Agent).",
        "Automatische Statusinfos statt Nachfragen per E-Mail (Status Agent)."
      ],
      "impact": "Schnellere Bestellungen ohne Schulungsaufwand, höhere Akzeptanz im Team."
    },
    {
      "nummer": 2,
      "ebene": "Einkauf / Administration",
      "bullets": ["..."],
      "impact": "..."
    },
    {
      "nummer": 3,
      "ebene": "Finance / Controlling",
      "bullets": ["..."],
      "impact": "..."
    },
    {
      "nummer": 4,
      "ebene": "Geschäftsführung / Management",
      "bullets": ["..."],
      "impact": "..."
    }
  ],
  "executive_summary": "Ein Satz: operative Entlastung, finanzielle Wirkung, strategische Steuerbarkeit.",
  "zahlenbasis": [
    { "text": "ca. 4.000 Rechnungen pro Jahr", "status": "belegt" },
    { "text": "Einsparpotenzial bei Prozesskosten", "status": "annahme" }
  ],
  "annahmen": [
    "Optional: Liste offener Punkte, die im nächsten Gespräch validiert werden."
  ],
  "naechster_schritt": {
    "text": "Gerne zeigen wir Ihnen die genannten Punkte live in Ihrer eigenen Umgebung.",
    "cta": "Folgetermin vereinbaren",
    "link": "https://hivebuy.com/demo"
  }
}
```

Regeln:

- Immer genau 4 Ladder-Einträge in fester Reihenfolge (1 bis 4).
- `zahlenbasis` und `annahmen` dürfen leer sein (`[]`), dann werden die Abschnitte im PDF ausgeblendet.
- Kunde-Slug für Dateinamen: Kleinbuchstaben, Umlaute transkribieren (ä zu ae), Sonderzeichen zu Bindestrich.

---

## Schritt 3: Rendern

```bash
node scripts/render.js output/<kunde-slug>-impact-ladder.json
```

Ergebnis: `output/JJJJ-MM-TT-impact-ladder-<kunde-slug>.pdf`

---

## Design-Spezifikation (fixiert, nicht verhandelbar)

### Farben

| Token | Wert | Verwendung |
|---|---|---|
| `--hb-dark` | `#204540` | Primärflächen, Fließtext, Executive-Summary-Box |
| `--hb-teal` | `#228C7D` | Sekundär: Sektionslabels, Kartenränder, Icons |
| `--hb-neon` | `#F1FF45` | NUR Akzent und CTA: Impact-Chips, Nummern-Badges, CTA-Button |
| `--hb-offwhite` | `#FBFBFB` | Seitenhintergrund, Karten |
| Surface-Gradient | `#228C7D` zu `#204540` (135°) | Kopfband Seite 1 |

Neon-Gelbgrün nie als Textfarbe auf hellem Grund und nie großflächig als Hintergrund für Fließtext.

### Typografie

| Element | Font | Größe |
|---|---|---|
| Dokumenttitel (H1) | Frank Ruhl Libre | 28 pt |
| Ebenen-Titel (H3) | Frank Ruhl Libre | 14 pt |
| Sektionslabel (H2) | DM Sans Bold, Versalien, 1 px Letter-Spacing | 10 pt |
| Fließtext, Bullets | DM Sans Regular | 10 pt, Zeilenhöhe 1,5 |
| Impact-Zeile | DM Sans Medium | 10 pt |
| Kleintext (Zahlenbasis, Annahmen) | DM Sans Regular | 8,5 pt |

Fallback-Kette: Frank Ruhl Libre, dann Georgia. DM Sans, dann Helvetica, Arial.

### Layout

- Format: DIN A4 hochkant, `printBackground: true`.
- Kopfband Seite 1: Surface-Gradient, volle Breite, Hivebuy-Logo (weiß) oben links, Titel "Impact Ladder" plus Kundenname, darunter Meta-Zeile (Ansprechpartner, Gesprächsdatum).
- Innenränder Inhalt: 16 mm links und rechts.
- Fußzeile auf jeder Seite: "Hivebuy GmbH · Invalidenstraße 35 · 10115 Berlin · hivebuy.com" plus Seitenzahl.
- Kartenradius 8 px, Rahmenfarbe `#E3E9E7`.
- Jede Ladder-Karte und die Summary-Box: `break-inside: avoid`.
- Zielumfang: maximal 2 Seiten.

### Verbindliche Quelldateien

Layout und Rendering liegen als eigenständige Dateien vor und sind die einzige Wahrheit. Sie werden
bewusst nicht in dieser SKILL.md dupliziert, damit es keine zwei abweichenden Fassungen gibt:

- `template/template.html`: fixes Layout, Farben, Typografie und Handlebars-Platzhalter.
- `scripts/render.js`: Rendering per Handlebars und Puppeteer, A4, Fußzeile, Dateinamensschema.

Beide Dateien sind inhaltlich unverändert übernommen. Wer das Design anpassen will, ändert das
Template, nicht den Output von Claude.

Hinweis Folgeseiten: Der Seitenrand oben ist 0 mm, damit das Kopfband auf Seite 1 randlos läuft. Falls Inhalte auf Seite 2 zu hoch am Rand kleben, im Template beim ersten Element nach einem Umbruch nichts ändern, sondern in `page.pdf` den `top`-Margin auf `10mm` setzen und im Template das Kopfband um `margin-top: -10mm` kompensieren. Nur eine der beiden Varianten dauerhaft verwenden.

---

## QA-Checkliste (vor Übergabe prüfen)

- [ ] Genau 4 Ladder-Ebenen in fester Reihenfolge, je 2 bis 3 Bullets, je eine Impact-Zeile.
- [ ] Alle Zahlen stammen aus den Gesprächsnotizen oder sind als Annahme markiert.
- [ ] Keine generischen Vorteile, keine Kundenquerverweise, keine namentlichen Lieferanten.
- [ ] Keine Gedankenstriche im gesamten Text.
- [ ] Frank Ruhl Libre und DM Sans korrekt gerendert (kein Fallback sichtbar), Logo vorhanden.
- [ ] Neon-Gelbgrün nur bei Impact-Chips, Nummern-Badges und CTA.
- [ ] Maximal 2 Seiten, keine Karte über einen Seitenumbruch zerschnitten.
- [ ] Dateiname: `JJJJ-MM-TT-impact-ladder-<kunde-slug>.pdf`.
- [ ] Executive Summary ist genau ein Satz mit operativer, finanzieller und strategischer Dimension.

---

## Setup-Status in diesem Repo (Stand 19.08.2026)

| Asset | Status |
|---|---|
| `puppeteer`, `handlebars` | installiert, Puppeteer bringt eigenen Chrome mit |
| `FrankRuhlLibre-Regular.woff2` | vorhanden, Serif fuer H1, Ebenen-Titel und Executive Summary |
| `DMSans-Regular/Medium/Bold.woff2` | vorhanden, Latin-Subset mit deutschen Umlauten |
| `logo-hivebuy-white.svg` | vorhanden, weisse Variante des offiziellen Logos von hivebuy.com |

Frank Ruhl Libre ersetzt IvyOra Display als Serif des Dokuments (Entscheidung Moritz, 19.08.2026).
Die Schrift steht unter der Open Font License und liegt als woff2 im Repo, das PDF ist damit ohne
weitere Lizenzschritte reproduzierbar.

## Integration in die Follow-up-Routine

Die Routine "Granola-Notiz-Sync und Antwortvorschlag" (siehe `GRANOLA_SYNC.md`) führt diese Skill
automatisch aus, sobald sie für ein Erstgespräch (Meeting-Titel enthält "Kennenlernen") einen
Antwortvorschlag erstellt hat. Der PDF-Pfad wird zusammen mit dem E-Mail-Entwurf ausgegeben, im
Antwortvorschlag am Kontakt vermerkt und in der Slack-Nachricht an den Kontakt-Owner genannt.
