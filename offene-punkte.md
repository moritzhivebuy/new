# Offene Punkte, Schritt für Schritt

Stand: 2026-08-20, alle Angaben live geprüft, nicht aus dem Gedächtnis.

Erledigt und hier nicht mehr aufgeführt: 6 Redirects, 83 Meta-Descriptions,
3 `&amp;`-Titles, Meta von `/ki-beschaffungsplattform`.

---

## Schritt 1: `noindex` auf die restlichen 9 Landing Pages

**Status:** 2 von 11 sind erledigt, `/lp_kostenlose_demo` und `/lp_kostenlose_demo_v2`
liefern schon `noindex`.

**Noch offen:**

```
/ki-beschaffungsplattform          /lp_kostenlose_demo_v3
/lp_kostenlose_demo_v3-0           /lp_kostenlose_demo_0825
/lp_beschaffung                    /lp_testzugang
/lp_video_integrationen            /lp_video_implementierung
/lp_video_bedarfsanforderungen
```

**Wo:** Landing Page öffnen, Einstellungen, Erweiterte Optionen, Häkchen bei
"Suchmaschinen anweisen, diese Seite nicht zu indexieren".

**Wer:** du. Über die API nicht möglich, das Objekt hat kein Robots-Feld.

**Aufwand:** 15 Minuten.

---

## Schritt 2: Search Console, Entfernung beantragen

`/lp_kostenlose_demo_0825` ist nachweislich im Google-Index. Nach Schritt 1 eine
Entfernung beantragen, sonst bleibt die Seite noch Wochen sichtbar.

Danach mit `site:hivebuy.com/lp_` prüfen, ob weitere Landing Pages im Index stehen.

**Wer:** du. Ich habe keinen Search-Console-Zugang.

**Aufwand:** 5 Minuten.

---

## Schritt 3: Die zwei Money-Page-Titles

**Status:** unverändert, `/preise-hivebuy` heißt `Preise`, `/en/pricing` heißt `Prices`.

```
/preise-hivebuy   ->  Einkaufssoftware Preise & Pakete | Hivebuy
/en/pricing       ->  Pricing & Plans | AI Procurement Software | Hivebuy
```

**Wer: ich, wenn du zustimmst.** Es ist dasselbe `htmlTitle`-Feld, das ich bei den drei
`&amp;`-Korrekturen schon geschrieben habe. Ich habe es bisher gelassen, weil es eine
Marketing-Entscheidung ist und keine Fehlerkorrektur. Ein Wort von dir und es ist
in einer Minute erledigt.

---

## Schritt 4: Blog-Einstellungen, vier Werte

Alles an einer Stelle: Einstellungen, Content, Blog, dann je Blog auswählen.
Über die API nicht möglich, der Endpoint antwortet mit `allow: HEAD,GET,OPTIONS`.

### 4a Titles

| Blog | ist | soll |
|---|---|---|
| `/blog` | `blog` | `Einkauf & Beschaffung: Blog für den Mittelstand \| Hivebuy` |
| `/en/blog` | `blog` | `Procurement & Purchasing Blog \| Hivebuy` |
| `/webinare` | `Webinare` | `Webinare zu Einkauf und Beschaffung \| Hivebuy` |
| `/whitepaper-blog` | `Whitepaper` | `Whitepaper für Einkauf und Beschaffung \| Hivebuy` |

### 4b Descriptions

`/webinare` hat 8 Zeichen, `/whitepaper-blog` hat 10.

```
/webinare
Webinare zu Einkauf und Beschaffung: Praxisberichte, Produktneuheiten und KI im Einkauf. Kostenlos anmelden oder Aufzeichnungen ansehen.

/whitepaper-blog
Whitepaper zu Einkauf und Beschaffung: Leitfäden zu KI, Automatisierung, Softwareauswahl und Einführung. Kostenlos zum Download.

/en/blog
The Hivebuy blog on procurement and purchasing: practical guides, benchmarks and advice for mid-sized companies. Free to read.
```

### 4c Sprachwerte, das ist der wichtige Teil

| Blog | ist | soll | Begründung |
|---|---|---|---|
| `/blog` | `de-de` | `de` | `de-de` gilt nur für Deutschland, ihr adressiert DACH |
| `/webinare` | **`en`** | `de` | deutsche Seite, falsch ausgezeichnet |
| `/whitepaper-blog` | **`en`** | `de` | deutsche Seite, falsch ausgezeichnet |
| `/en/blog` | `en` | `en` | korrekt, nicht anfassen |

**Das ist die Ursache des Sprachproblems.** Es sind drei Werte, nicht 45 Einzelseiten.
Damit lösen sich zugleich das `de-de` im hreflang des Blogs und die drei Listing-Seiten,
deren `html lang` dem eigenen Sprachbaum widersprach.

**Vorsicht:** eine Änderung an `language` kann in HubSpot hreflang-Gruppierungen
verschieben. Bitte einmal in der Vorschau prüfen, bevor du speicherst.

**Aufwand für Schritt 4 gesamt:** 20 Minuten.

---

## Schritt 5: Metas der Hilfecenter-Seiten

Beide haben 19 Zeichen. Nicht über die Pages-API erreichbar, das Hilfecenter ist eine
Knowledge Base, und `cms/v3/knowledge-base/settings` gibt 404.

```
/hilfecenter
Hivebuy Hilfecenter: Anleitungen zu Bedarfsanforderung, Freigaben, Katalogen und Rechnungsprüfung. Antworten und Videos an einem Ort.

/hilfecenter/kb-search-results
Suchergebnisse im Hivebuy Hilfecenter: Anleitungen und Antworten zu Bedarfsanforderung, Freigaben, Katalogen und Rechnungsprüfung.
```

**Aufwand:** 5 Minuten.

---

## Schritt 6: `/en/helpcenter` richtig verknüpfen

**Ist:** `/en/helpcenter` ist per hreflang mit `/hilfecenter-videos` gepaart.
**Soll:** mit `/hilfecenter`, der eigentlichen Startseite des Hilfecenters.

Zusätzlich `/hilfecenter-videos` einen eigenen Title geben, aktuell tragen beide
deutschen Seiten `Hivebuy Hilfecenter`:

```
/hilfecenter-videos  ->  Video-Anleitungen | Hivebuy Hilfecenter
```

**Aufwand:** 15 Minuten.

---

## Schritt 7: Canonical im Listing-Template

**Betroffen, live geprüft:** `/blog`, `/en/blog`, `/webinare`, `/whitepaper-blog` haben
**keinen** Canonical. `/hilfecenter` und `/hilfecenter/kb-search-results` haben einen,
die sind in Ordnung.

Der übrige Standard-Head ist vorhanden, geprüft sind `og:url`, JSON-LD und auf `/blog`
zusätzlich `rel="next"`. Es fehlt gezielt der Canonical.

**Warum es zählt:** `/blog` ist paginiert. Ohne Canonical wird jeder Paginierungszustand
zum Beinah-Duplikat.

**Wer:** Entwicklerin, Design Manager, Listing-Template. Details und Prüfbefehl in
`blog-fix-anleitung.md`, Schritt 1.

**Aufwand:** 30 Minuten.

---

## Schritt 8: H1 in vier Templates

Live geprüfte Stichprobe, bestätigt das Muster:

| Seite | H1 | Template |
|---|---|---|
| `/lösungen` | **0** | Lösungen und Case Studies |
| `/kundenreferenzen` | **0** | dito |
| `/integration-datev` | 2 | Integrationsseiten, 14 Seiten |
| `/ki-agenten-finance` | **4** | KI-Agenten, 6 Seiten |
| `/workflows-einkauf` | 2 | Abteilungsseiten |
| `/blog` | 2 | Listing |

56 Seiten betroffen, aber rund vier Templates. **Zuerst die 25 Seiten ohne jedes H1**,
darunter `/lösungen` und `/kundenreferenzen`, beide kommerziell relevant.

**Wer:** Entwicklerin.

**Aufwand:** 2 bis 3 Stunden.

---

## Schritt 9: `x-default` ergänzen

Live geprüft: auf **keiner** Seite gesetzt. Auf allen 118 Seiten mit hreflang einen
dritten Eintrag ergänzen, der auf die englische Fassung zeigt.

```html
<link rel="alternate" hreflang="de"        href="…/preise-hivebuy">
<link rel="alternate" hreflang="en"        href="…/en/pricing">
<link rel="alternate" hreflang="x-default" href="…/en/pricing">
```

Eine Template-Änderung, keine 118 Einzeleingriffe.

**Wer:** Entwicklerin.

**Aufwand:** 1 Stunde.

---

## Schritt 10: Interne Verlinkung des Blog-Clusters

Das ist der einzige Punkt, der die 52 vorhandenen Posts wirklich aktiviert. Alles
davor ist Voraussetzung dafür.

Zehn konkrete Link-Paare stehen in `blog-fix-anleitung.md`, Schritt 5. Kurzform: aus
`/produkt`, `/lösungen`, `/preise-hivebuy`, `/rechnungsmanagement`,
`/analysen-reportings` und `/vertragsmanagement` in den passenden Post verlinken, und
jeder Post trägt genau einen klaren Link zurück auf die passende kommerzielle Seite.

**Aufwand:** 2 bis 3 Stunden.

---

## Schritt 11: Entscheidung englischer Blog

`/en/blog` antwortet mit 200, jedes `/en/blog/<slug>` mit 404. Zwei englische Drafts
liegen unveröffentlicht im Portal.

Meine Empfehlung: **abschalten**, bis der deutsche Blog Traffic zieht. Also
`hreflang="en"` aus dem Listing-Template entfernen und `/en/blog` auf `/blog`
weiterleiten. Zwei Sprachen zu bedienen, von denen die erste noch nicht funktioniert,
verteilt den Aufwand auf die falsche Achse.

Wenn Englisch strategisch ist, dann umgekehrt: die zwei Drafts fertig übersetzen, Slugs
auf Englisch ziehen, veröffentlichen, und auf mindestens zehn Artikel aufbauen.

**Blockiert:** Schritt 4a und 4b für `/en/blog` sind sinnlos, solange das offen ist.

---

## Schritt 12: Service Key aufräumen

Der Token trägt jetzt `content`, also Lese-, Änderungs- und Löschrechte auf alle
Website-Inhalte des Portals. Die Meta-Arbeit ist abgeschlossen.

Wenn Schritt 3 erledigt ist und keine weiteren API-Änderungen geplant sind: **Token
löschen oder rotieren.** Wenn du die Private App eigens dafür angelegt hast, kannst du
sie ersatzlos entfernen.

---

## Zusammenfassung nach Zuständigkeit

| Wer | Schritte | Aufwand |
|---|---|---|
| **du, Oberfläche** | 1, 2, 4, 5, 6, 10 | etwa 4 Stunden, davon 3 für die Verlinkung |
| **du, Search Console** | 2 | 5 min |
| **ich, auf Zuruf** | 3 | 1 min |
| **Entwicklerin** | 7, 8, 9 | 4 Stunden |
| **Entscheidung** | 11 | Diskussion, blockiert Teile von 4 |
| **Aufräumen** | 12 | 2 min |

**Empfohlene Reihenfolge:** 1 und 2 zuerst, das ist der schnellste Effekt. Dann 3 und 4
zusammen, weil beides Einstellungen sind. Dann 11 entscheiden, weil es 4 betrifft.
Danach 7 bis 9 an die Entwicklung geben und parallel 5, 6 und 10 abarbeiten. 12 zum
Schluss.

---

## Kontrolle

Sag Bescheid, wenn eine Charge steht, dann prüfe ich sie live. Das funktioniert
zuverlässig, es sind reine HTTP-Abrufe. Bei den Redirects und den 83 Metas hat es
gehalten.

Für den Index-Status arbeite ich mit `site:`-Abfragen. Die Search Console kann ich
nicht einsehen.
