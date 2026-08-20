# Umsetzungsplan: was zu tun ist, und wer es macht

Stand: 2026-08-20. Entscheidungen bis hierher: Redirects umgesetzt, Konversion
depriorisiert, `/ki-beschaffungsplattform` gilt als Landing Page und geht auf `noindex`.

---

## Meine Schreibrechte, damit die Aufteilung klar ist

Ich habe im HubSpot-Portal geprüft, was ich per API tatsächlich ändern kann:

| Objekttyp | Lesen | Schreiben | Konsequenz |
|---|---|---|---|
| `BLOG_POST` | ja | **ja** | Titel und Meta-Description kann ich setzen |
| `LANDING_PAGE` | ja | **ja** | Metadaten inklusive Title, Meta, Slug, Sprache |
| `SITE_PAGE` | ja | **nein** | 72 Seiten kann ich nicht anfassen |
| Templates, Blog-Einstellungen, Redirects, Spracheinstellungen | nein | nein | nur über die HubSpot-Oberfläche |

`SITE_PAGE` steht im Portal auf `writeAccess: NOT_AVAILABLE`, und es existiert kein
Site-Page-Werkzeug. Das ist keine Berechtigungsfrage, die man mir erteilen könnte,
sondern eine Grenze der Schnittstelle.

**Realistische Aufteilung der 88 Meta-Descriptions:**

| Gruppe | Anzahl | Wer |
|---|---|---|
| Blogposts | 14 | **ich** |
| Site Pages | 72 | **du** |
| Listing-Seiten `/webinare`, `/whitepaper-blog` | 2 | **du**, sitzt in den Blog-Einstellungen |

---

## Phase 1: blockiert, ich kann es doch nicht ausführen

**Korrektur vom 2026-08-20, nach dem Versuch.** Ich hatte zugesagt, die 14
Blogpost-Metas und die Meta von `/ki-beschaffungsplattform` selbst zu setzen. Das geht
nicht.

Beide Content-Werkzeuge, `manage_blog_post` und `manage_landing_page`, antworten in
meiner Session mit `requires approval`, und die Freigabe kommt nicht durch. Das gilt
auch für die reinen Lesezugriffe wie `GET_POST`. Die Analytics- und CRM-Abfragen liefen
dagegen ohne Freigabe, deshalb war die Grenze vorher nicht sichtbar.

Praktisch heißt das: **ich kann in HubSpot nichts schreiben, auch nicht bei Blogposts
und Landing Pages.** Meine Einschätzung in der Tabelle oben war zu optimistisch, sie
beschrieb die Rechte des Objekttyps, nicht die Freigabe des Werkzeugs.

Damit verschieben sich die 14 Blogpost-Metas und die Landing-Page-Meta nach Phase 2,
also zu dir. Fertig aufbereitet mit Editor-Links liegen sie in:

- `blogpost-metas-zum-einsetzen.md` und `.csv`, 14 Posts, nach Ist-Länge sortiert,
  jeweils mit direktem Link in die HubSpot-Einstellungen des Posts

Falls die Freigabe in einer neuen Session erteilt wird, kann ich es übernehmen. Bis
dahin ist es Handarbeit.

### Was ursprünglich hier stand, als Referenz

### 1.1 Meta-Descriptions der 14 Blogposts

Betroffen sind die Posts mit 226 bis 480 Zeichen, wo HubSpot den Text automatisch
aus dem Artikelkörper zieht. Texte liegen fertig in
`meta-descriptions-vorschlaege.csv`.

```
/blog/einkaufssoftware-4-bereiche-fuer-optimierung                    480 -> 133
/blog/einkaufssoftware-vorteile-unternehmen                           477 -> 138
/blog/hivebuy-im-procurement-summit-magazin                           468 -> 129
/blog/3-herausforderungen-bei-der-einfuehrung-von-einkaufssoftware    440 -> 132
/blog/wie-waehle-ich-die-richtige-einkaufssoftware-...                407 -> 128
/blog/beschaffung-aktuell-wir-sind-in-tausende-...                    313 -> 139
/blog/amazon-business-integration-is-live                             274 -> 134
/blog/die-kosten-eines-schlechten-einkaufsprozesses                   273 -> 140
/blog/die-besten-einkaufssoftwares                                    226 -> 135
/blog/procurementheroes-folge-1                                       226 -> 137
/blog/procurementheroes-folge-2                                       226 -> 134
/blog/lieferkettengesetz-deutschland                                  169 -> 134
/blog/software-beschaffung-hr-bereich                                 169 -> 136
/blog/ki-im-einkauf                                                   168 -> 131
```

**Ein Vorbehalt:** die Posts sind veröffentlicht. Eine Änderung per API erzeugt
möglicherweise eine Entwurfsversion, die separat publiziert werden muss. Ich teste
das am ersten Post und sage dir, ob du danach noch publizieren musst.

### 1.2 Meta-Description von `/ki-beschaffungsplattform`

236 Zeichen, wird abgeschnitten. Kann ich per `SET_METADATA` setzen.

### 1.3 Optional: `noindex` per `headHtml`

Ich **kann** technisch `<meta name="robots" content="noindex,follow">` über das
`headHtml`-Feld der Landing Pages injizieren. **Ich empfehle es nicht.** Es gibt keine
Lesefunktion für das Feld, ich würde also blind schreiben und riskieren, vorhandenes
`headHtml` zu überschreiben, etwa Tracking-Skripte oder Kampagnen-Pixel.

Der `noindex` gehört über die native Einstellung, siehe Phase 2.1. Wenn du es trotzdem
per API willst, sag es, dann mache ich es, aber du solltest vorher in einer der Seiten
nachsehen, ob dort eigenes `headHtml` liegt.

---

## Phase 2: nur du, HubSpot-Oberfläche

### 2.1 `noindex` auf alle Landing Pages, höchste Priorität

Pro Seite: Landing Page öffnen, Einstellungen, Erweiterte Optionen, Häkchen bei
"Suchmaschinen anweisen, diese Seite nicht zu indexieren".

```
/ki-beschaffungsplattform      <- entschieden, klar eine Landing Page
/lp_kostenlose_demo            /lp_kostenlose_demo_v2
/lp_kostenlose_demo_v3         /lp_kostenlose_demo_v3-0
/lp_kostenlose_demo_0825       /lp_beschaffung
/lp_testzugang                 /lp_video_integrationen
/lp_video_implementierung      /lp_video_bedarfsanforderungen
```

11 Seiten, etwa 20 Minuten. `follow` bleibt aktiv, HubSpots Häkchen setzt nur
`noindex`, die internen Links geben weiter Linkkraft weiter.

**Danach unbedingt:** in der Search Console eine Entfernung für
`/lp_kostenlose_demo_0825` beantragen, die Seite ist nachweislich im Index. Die
anderen prüfen mit `site:hivebuy.com/lp_`.

### 2.2 Die drei `&amp;`-Titles

Seite öffnen, Einstellungen, Feld "Seitentitel", `&amp;` durch `&` ersetzen.

```
/en/management                      Cost control &amp; scaling in management | Hivebuy
/en/industrien/dienstleistungen     ... Manage Purchasing &amp; Costs | Hivebuy
/en/case_study_tennis-point         Tennis-Point Case Study: ... with Hivebuy &amp; SAP
```

10 Minuten. Achtung: nur diese drei. Andere Seiten mit einem normalen `&` sind korrekt
und dürfen nicht angefasst werden.

### 2.3 Die beiden Money-Page-Titles

```
/preise-hivebuy   "Preise"  ->  "Einkaufssoftware Preise & Pakete | Hivebuy"
/en/pricing       "Prices"  ->  "Pricing & Plans | AI Procurement Software | Hivebuy"
```

5 Minuten.

### 2.4 Meta-Description der englischen Startseite

`/en/` hat 20 Zeichen. Text liegt in der CSV.

### 2.5 Die 72 Site-Page-Meta-Descriptions

Das ist die größte Handarbeit. Aus `meta-descriptions-vorschlaege.csv` abarbeiten,
Spalte `vorschlag` in das Feld "Meta-Beschreibung".

Reihenfolge nach Wirkung:

1. **Zuerst die 9 Seiten mit über 250 Zeichen**: `/webinar-tennispoint`,
   `/kundenbericht-thermondo`, `/webinar-produktdemo`, `/en/customer-review-thermondo`,
   `/webinar-hiveiq`, `/whitepaper_100d`, `/whitepaper_automation`,
   `/anbindungsanleitung-sap-business-one`, `/webinar-schaefershop`
2. **Dann die 11 zu kurzen**, darunter `/hilfecenter`, `/en/helpcenter`, `/en/resources`
3. **Dann die 2 fehlenden**: `/en/career`, `/deine-karriere-bei-hivebuy`
4. **Dann der Rest**

Grob 3 bis 4 Stunden für alle 72. Realistisch auf zwei Sitzungen verteilen.

### 2.6 Spracheinstellungen vereinheitlichen

45 Seiten liefern `html lang="de-de"`, während ihr hreflang `de` sagt. Das hängt an
einer Domain- oder Seitengruppen-Spracheinstellung, nicht an einzelnen Seiten. In den
Content-Einstellungen unter Domains und Sprachen von Deutsch (Deutschland) auf Deutsch
umstellen.

Dazu die drei Seiten, deren Sprache schlicht falsch ist:

```
/webinare          lang="en"    -> de
/whitepaper-blog   lang="en"    -> de
/en/blog           lang="de-de" -> en
```

### 2.7 `/en/helpcenter` neu verknüpfen

Aktuell verknüpft mit `/hilfecenter-videos`, richtig wäre `/hilfecenter`. In der
Sprachvarianten-Verwaltung der Seite umhängen. Dazu `/hilfecenter-videos` einen eigenen
Title geben, etwa `Video-Anleitungen | Hivebuy Hilfecenter`, aktuell tragen beide
deutschen Seiten denselben.

### 2.8 Blog-Listing-Titles

```
/blog             "blog"        ->  "Einkauf & Beschaffung: Blog für den Mittelstand | Hivebuy"
/webinare         "Webinare"    ->  "Webinare zu Einkauf und Beschaffung | Hivebuy"
/whitepaper-blog  "Whitepaper"  ->  "Whitepaper für Einkauf und Beschaffung | Hivebuy"
```

Sitzt in den Blog-Einstellungen, nicht im Seiten-Editor.

---

## Phase 3: Template-Arbeit, du oder eine Entwicklerin

Hier komme ich nicht heran, und es ist auch nichts, was man im Seiten-Editor klickt.

### 3.1 Canonical auf den Listing-Templates

Fehlt auf `/blog`, `/en/blog`, `/webinare`, `/whitepaper-blog`. Der restliche
Standard-Head ist vorhanden, es fehlt gezielt der Canonical. Details und
Prüfbefehl in `blog-fix-anleitung.md`, Schritt 1.

### 3.2 H1-Struktur in vier Templates

56 Seiten sind betroffen, aber es sind rund vier Templates:

| Template | H1 aktuell | Seiten |
|---|---|---|
| Integrationsseiten | 2 | 14 |
| Case Studies, `/lösungen`, `/kundenreferenzen` | 0 | 25 |
| `ki-agenten`-Seiten | 4 | 6 |
| Listing-Template | 2 | 4 |

Zuerst die 25 Seiten ohne jedes H1, darunter `/lösungen` und `/kundenreferenzen`.

### 3.3 `x-default` ergänzen

Auf allen 118 Seiten mit hreflang einen dritten Eintrag, der auf die englische Fassung
zeigt. Eine Template-Änderung, keine 118 Einzeleingriffe. Beispiel in
`language-variants-anweisung.md`, Defekt 3.

---

## Phase 4: Entscheidungen, die du treffen musst

Keine Umsetzung, sondern Weichenstellungen. Die erste blockiert Arbeit in Phase 2 und 3.

### 4.1 Englischer Blog: fertigstellen oder abschalten

`/en/blog` antwortet mit 200, jedes `/en/blog/<slug>` mit 404. Zwei englische Drafts
liegen unveröffentlicht im Portal. Solange das offen ist, weiß niemand, ob
`hreflang="en"` auf dem Blog bleibt oder weg muss.

Meine Empfehlung: abschalten, bis der deutsche Blog Traffic zieht.

### 4.2 Englische Slugs: 41 von 59 tragen deutsche Slugs

Meine Empfehlung ist der kleine Schnitt, nicht der Vollumzug: nur `/en/lösungen`,
die sechs `/en/industrien/*`, `/en/analytics-reportings` und `/en/workflows-einkauf`.
Neun Seiten plus Redirects.

### 4.3 Grundsatzfrage Englisch

Der englische Baum deckt die Entscheidungsphase ab, nicht die Informationsphase. Drei
Haltungen sind vertretbar, ausformuliert in `language-variants-anweisung.md`. Das
sollte vor 4.1 und 4.2 geklärt sein, weil beide daran hängen.

### 4.4 Nur zur Kenntnis, nicht mein Thema

Wenn auf `/ki-beschaffungsplattform` bezahlter Traffic läuft, und davon gehen wir jetzt
aus, dann sind 26.715 Klicks für 16 Formulare eine Conversion Rate von 0,06 Prozent.
Das ist eine Frage für dein Ads-Budget, nicht für SEO. Ich erwähne es, weil die Zahl
sonst untergeht.

---

## Reihenfolge und Aufwand

| # | Was | Wer | Aufwand | Wirkung |
|---|---|---|---|---|
| 1 | `noindex` auf 11 Landing Pages | du | 20 min | hoch |
| 2 | 14 Blogpost-Metas | **ich** | auf Zuruf | mittel |
| 3 | Meta `/ki-beschaffungsplattform` | **ich** | auf Zuruf | mittel |
| 4 | 3 `&amp;`-Titles, 2 Money-Titles, `/en/` Meta | du | 20 min | hoch |
| 5 | Canonical im Listing-Template | Dev | 30 min | hoch |
| 6 | Spracheinstellung `de`, 3 falsche Seiten | du | 1 h | hoch |
| 7 | `/en/helpcenter` umhängen | du | 15 min | mittel |
| 8 | Blog-Listing-Titles | du | 15 min | mittel |
| 9 | H1-Templates | Dev | 2 bis 3 h | mittel |
| 10 | 72 Site-Page-Metas | du | 3 bis 4 h | mittel, in Summe hoch |
| 11 | `x-default` | Dev | 1 h | mittel |
| 12 | Interne Verlinkung Blog-Cluster | du | 2 bis 3 h | hoch |
| 13 | Entscheidungen 4.1 bis 4.3 | du | Diskussion | blockiert 4.1, 4.2 |

Schritte 1 bis 4 sind an einem Vormittag erledigt und decken die Punkte mit dem besten
Verhältnis von Aufwand zu Wirkung ab. Schritt 10 ist der lange Brocken, aber
unkritisch in der Reihenfolge, die Texte liegen fertig vor.

---

## Was ich konkret als nächstes machen kann

Ausführen kann ich in HubSpot nichts, siehe Phase 1. Was ich beitragen kann, ist
Vorbereitung und Kontrolle:

- **Werte fertig aufbereiten**, wie bei den Metas und Titles bereits geschehen. Sag,
  welche Gruppe du als nächstes angehst, dann liefere ich die Liste im gleichen Format.
- **Nach deiner Umsetzung gegenprüfen.** Das kann ich zuverlässig, es sind reine
  HTTP-Abrufe. Bei den Redirects hat das funktioniert, alle sechs habe ich verifiziert.
  Sag Bescheid, wenn eine Charge steht, dann crawle ich die betroffenen Seiten und
  melde, was noch nicht greift.
- **Search Console kann ich nicht einsehen.** Für Index-Status arbeite ich mit
  `site:`-Abfragen, das ist gröber, reicht aber um zu sehen, ob eine Seite raus ist.

Alles andere in dieser Liste kann ich nicht ausführen, nur vorbereiten. Wo es hilft,
schreibe ich dir die konkreten Werte vorab auf, wie bei den Titles und Metas schon
geschehen.
