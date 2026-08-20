# Blog: genaue Anweisung

Stand: 2026-08-20. Alle Befunde per Live-Crawl der 180 Sitemap-URLs verifiziert.

## Ausgangslage

52 Blogposts mit sauberem Themencluster, aber kein einzelner Post in den Top 100
nach Views. Der `/blog`-Hub selbst hatte 170 Views im Halbjahr, die Autorenseite
`/blog/author/bettina-fischer` 185. Eine Autorenarchivseite schlägt also den Hub,
zu dem sie gehört.

Das ist kein Qualitätsproblem der Texte. Es sind vier technische Ursachen.

---

## Schritt 1: Canonical auf den Listing-Seiten ergänzen

**Betroffen sind vier Seiten, nicht nur `/blog`:**

```
/blog
/en/blog
/webinare
/whitepaper-blog
```

**Befund:** Diese vier Seiten haben **keinen** Canonical-Tag. Blogposts selbst haben
einen. Der übrige Standard-Head ist auf den Listing-Seiten vorhanden, geprüft sind
`og:url`, `og:title`, `twitter:*`, JSON-LD und auf `/blog` zusätzlich `rel="next"`.
Es fehlt also gezielt nur der Canonical, nicht der ganze Head.

**Warum das hier besonders zählt:** `/blog` ist paginiert (`rel="next"` ist gesetzt).
Paginierte Übersichten ohne Canonical erzeugen für Google beliebig viele
Beinah-Duplikate derselben Seite.

**Vorgehen im Design Manager:**

1. Öffne das Listing-Template des Blogs (Marketing, Website, Blog, dann das
   verwendete Listing-Template, nicht das Post-Template).
2. Prüfe zuerst, ob `{{ standard_header_includes }}` im `<head>` steht. Da og:url und
   JSON-LD ausgeliefert werden, steht es sehr wahrscheinlich dort. Dann wird der
   Canonical an anderer Stelle unterdrückt oder überschrieben. Suche im Template und
   in den zugehörigen Modulen nach `canonical`.
3. Falls kein Canonical erzeugt wird, setz ihn explizit im `<head>`:

```html
<link rel="canonical" href="{{ canonical_url }}">
```

4. Wiederhole das für die Listing-Templates von `/webinare` und `/whitepaper-blog`,
   falls diese ein eigenes Template nutzen. Nutzen sie dasselbe, ist der Fix damit
   schon erledigt.

**Kontrolle nach dem Publish:**

```bash
curl -sS -A "Mozilla/5.0" https://www.hivebuy.com/blog | grep -i canonical
```

Erwartet wird genau eine Zeile mit `rel="canonical"`.

---

## Schritt 2: Title der Listing-Seiten ersetzen

**Befund:** Der Title von `/blog` lautet wörtlich `blog`, klein geschrieben, vier
Zeichen. `/webinare` heißt `Webinare`, `/whitepaper-blog` heißt `Whitepaper`. Alle drei
sind Platzhalter ohne Keyword.

**Wo:** Einstellungen, Content, Blog. Dort den jeweiligen Blog auswählen und das
Titel-Feld setzen. Der Listing-Title kommt aus den Blog-Einstellungen, nicht aus einem
Seitenobjekt, deshalb findest du ihn nicht im Seiten-Editor.

**Vorschläge:**

| Seite | aktuell | Vorschlag | Zeichen |
|---|---|---|---|
| `/blog` | `blog` | `Einkauf & Beschaffung: Blog für den Mittelstand \| Hivebuy` | 56 |
| `/webinare` | `Webinare` | `Webinare zu Einkauf und Beschaffung \| Hivebuy` | 45 |
| `/whitepaper-blog` | `Whitepaper` | `Whitepaper für Einkauf und Beschaffung \| Hivebuy` | 48 |

Die passenden Meta-Descriptions für diese drei Seiten stehen in
`meta-descriptions-vorschlaege.md`, alle drei sind aktuell zu kurz.

---

## Schritt 3: Englischen Blog entscheiden

**Befund, und das ist der unangenehmste Teil:**

```
/blog                          200   deklariert hreflang="en" auf /en/blog
/en/blog                       200   existiert
/en/blog/ki-im-einkauf         404
/en/blog/beschaffungsprozess-optimieren   404
```

Der englische Blog-Hub existiert, hat aber keine Artikel. `/blog` bewirbt per
`hreflang="en"` eine Sprachvariante, hinter der auf Artikelebene nichts liegt.

Im HubSpot-Bestand liegen zwei englische Post-Objekte, aber beide mit
`hs_publish_date` 1970-01-01, also unveröffentlicht:

```
/en/blog/beschaffungsprozess-optimieren   Titel noch deutsch: "Beschaffungsprozess optimieren: Tipps & Strategien"
/en/blog/bedarfsanforderung-banf          Titel englisch, Slug deutsch
```

**Zwei Optionen, bitte eine wählen:**

**A, wenn Englisch strategisch ist:** die beiden Drafts fertig übersetzen, Slugs auf
Englisch ziehen (`/en/blog/optimise-procurement-process`,
`/en/blog/purchase-requisition`), veröffentlichen, dann weitere Posts nachziehen.
Erst ab etwa 10 Artikeln lohnt der englische Hub überhaupt.

**B, wenn Englisch vorerst nicht bedient wird, empfohlen:** den `hreflang="en"`
Verweis aus dem Listing-Template entfernen und `/en/blog` auf `/blog` weiterleiten.
Ein leerer Hub, der als Sprachvariante angekündigt wird, kostet Vertrauen und bringt
nichts.

Ich empfehle B, bis der deutsche Blog Traffic zieht. Zwei Sprachen zu bedienen, von
denen die erste noch nicht funktioniert, verteilt den Aufwand auf die falsche Achse.

---

## Schritt 4: hreflang-Werte vereinheitlichen

**Befund:** Die Seitenvorlagen nutzen `de` und `en`. Der Blog nutzt `de-de` und `en`.

`de` und `de-de` sind für Google nicht dasselbe: `de` gilt für alle
deutschsprachigen Regionen, `de-de` nur für Deutschland. Da Hivebuy den DACH-Raum
adressiert, also auch Österreich und die Schweiz, ist `de` die richtige Wahl und der
Blog ist derzeit zu eng ausgezeichnet.

**Wo:** Einstellungen, Content, Blog, Spracheinstellung des Blogs von
Deutsch (Deutschland) auf Deutsch ändern. Danach mit dem Befehl aus Schritt 1 prüfen,
dass `hreflang="de"` ausgeliefert wird.

Zusätzlich: Blogposts liefern derzeit **gar kein** `hreflang` aus, nur der Hub tut es.
Das löst sich automatisch, sobald es echte Sprachvarianten der Posts gibt, also über
Option A in Schritt 3. Bei Option B ist nichts zu tun, weil es dann korrekt keine
Alternative gibt.

---

## Schritt 5: interne Verlinkung, die eigentliche Arbeit

Die vier Schritte oben sind Hygiene. Sie machen den Blog auffindbar, aber sie machen
ihn nicht relevant. Der Cluster hängt momentan ohne eingehende interne Links von den
kommerziellen Seiten.

**Konkret zu setzen:**

| Von | Nach | Ankertext-Richtung |
|---|---|---|
| `/produkt` | `/blog/purchase-to-pay` | Purchase-to-Pay Prozess |
| `/produkt` | `/blog/eprocurement` | eProcurement |
| `/lösungen` | `/blog/indirekter-einkauf` | indirekter Einkauf |
| `/lösungen` | `/blog/beschaffungsstrategien` | Beschaffungsstrategien |
| `/preise-hivebuy` | `/blog/die-besten-einkaufssoftwares` | Einkaufssoftware im Vergleich |
| `/preise-hivebuy` | `/blog/wie-waehle-ich-die-richtige-einkaufssoftware-5-wichtige-kriterien-zur-auswahl` | Auswahlkriterien |
| `/rechnungsmanagement` | `/blog/bedarfsanforderung-banf` | Bedarfsanforderung |
| `/analysen-reportings` | `/blog/kennzahlen-im-einkauf` | Kennzahlen im Einkauf |
| `/vertragsmanagement` | `/blog/lieferantenmanagement-definition-ziele-prozesse-und-software-der-komplette-überblick` | Lieferantenmanagement |
| `/industrien/logistik` | `/blog/lieferkettengesetz-deutschland` | Lieferkettengesetz |

Und in die andere Richtung: jeder Post im Cluster sollte genau einen klaren Link auf
die passende kommerzielle Seite tragen, nicht drei. Aktuell zeigen die Posts vor allem
auf sich selbst und auf die Startseite.

---

## Reihenfolge und Aufwand

| Schritt | Aufwand | Wirkung |
|---|---|---|
| 1, Canonical | 30 min, einmalig im Template | Hoch, verhindert Duplikate über die Pagination |
| 2, Titles | 15 min | Mittel, drei Hub-Seiten werden überhaupt erst anklickbar |
| 3, EN-Blog entscheiden | 15 min für Option B | Mittel, beendet ein falsches Signal |
| 4, hreflang | 10 min | Niedrig bis mittel, korrigiert die DACH-Ausrichtung |
| 5, Verlinkung | 2 bis 3 h | Hoch, das ist der Hebel für die 52 vorhandenen Posts |

Schritt 5 ist der einzige, der die vorhandenen Inhalte wirklich aktiviert. Die
Schritte 1 bis 4 sind die Voraussetzung dafür, dass sich der Aufwand aus Schritt 5
auszahlt.

---

## Was ich nicht prüfen konnte

- Ob die Listing-Templates von `/webinare` und `/whitepaper-blog` dasselbe Template
  nutzen wie `/blog`. Das ist nur im Design Manager sichtbar.
- Warum der Canonical fehlt, obwohl der restliche Standard-Head vorhanden ist. Dafür
  müsste ich in das Template sehen. Der explizite Canonical aus Schritt 1 behebt das
  Symptom in jedem Fall.
- Organischer Anteil am Blog-Traffic. Der HubSpot-Report, den ich gezogen habe, liefert
  keine Aufschlüsselung nach Quelle, die 170 Views auf `/blog` sind also alle Quellen
  zusammen.
