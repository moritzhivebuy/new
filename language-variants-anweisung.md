# Sprachvarianten: globale Analyse und Anweisung

Stand: 2026-08-20. Grundlage: zweiter Crawl aller 180 Sitemap-URLs mit vollständiger
Auswertung der `hreflang`-Paare, des `html lang`-Attributs und der Canonicals.

---

## Zusammenfassung

**Die hreflang-Implementierung ist technisch korrekt.** Das ist ungewöhnlich und
sollte nicht angefasst werden. Alle 59 Sprachpaare sind bidirektional verknüpft, jede
Seite referenziert sich selbst, und kein einziges hreflang-Ziel läuft ins Leere.

Die Probleme liegen auf zwei anderen Ebenen: das `html lang`-Attribut widerspricht
dem hreflang, und die englische URL-Struktur ist nur zur Hälfte übersetzt.

| Prüfung | Ergebnis |
|---|---|
| Sprachpaare insgesamt | 59 |
| Selbstreferenz vorhanden | 118 von 118, also 100 % korrekt |
| Reziprozität, A verweist auf B und zurück | 0 Fehler |
| hreflang-Ziele erreichbar und in der Sitemap | 0 Fehler |
| **`x-default` gesetzt** | **0 von 180 Seiten** |
| **`html lang` konsistent** | **drei verschiedene Werte im Einsatz** |
| **Englische Slugs übersetzt** | **18 von 59, die anderen 41 tragen deutsche Slugs** |

---

## Bestandsaufnahme der Struktur

```
121 deutsche Seiten   (Root, ohne Prefix)
 59 englische Seiten  (/en/)
 59 Sprachpaare
 62 deutsche Seiten ohne englisches Gegenstück
  0 englische Seiten ohne deutsches Gegenstück
```

Die 62 unverknüpften deutschen Seiten sind kein Fehler, es gibt dort schlicht keine
englische Fassung. hreflang fehlt dort also korrekterweise. Auffällig ist aber, **welche**
Seiten das sind: es ist praktisch die komplette Content-Marketing-Schicht.

| Bereich | DE-only Seiten |
|---|---|
| Blog inklusive Hub und Podcast | 45 |
| Webinare | 9, weitere 6 haben eine EN-Fassung |
| Whitepaper | 2 plus der Hub `/whitepaper-blog` |
| Case Studies | 2 (`/case_study_brera`, `/case_study_buefa`), 6 andere sind gepaart |
| Hilfecenter | `/hilfecenter` und `/hilfecenter/kb-search-results` |
| Sonstige | `/10_goldene_regeln`, `/anbindungsanleitung-sap-business-one` |

Das Produkt ist also zweisprachig, die Nachfragegenerierung nicht. Wer über englische
Inhalte einsteigt, findet Produktseiten, aber kein Material zum Weiterlesen.

---

## Defekt 1: `/en/helpcenter` zeigt auf die falsche deutsche Seite

**Befund:** `/en/helpcenter` ist per hreflang mit `/hilfecenter-videos` verknüpft, nicht
mit `/hilfecenter`. Die eigentliche deutsche Hilfecenter-Startseite `/hilfecenter` hat
gar kein hreflang und steht damit außerhalb der Sprachstruktur.

Beide deutschen Seiten tragen zusätzlich denselben Title, `Hivebuy Hilfecenter`, was
die Verwechslung erklärt.

**Anweisung:**

1. Entscheide, welche Seite die deutsche Hilfecenter-Startseite ist. Nach Title und
   Struktur ist das `/hilfecenter`, und `/hilfecenter-videos` ist die Unterseite mit
   den Videoanleitungen.
2. Verknüpfe `/en/helpcenter` mit `/hilfecenter`.
3. Gib `/hilfecenter-videos` einen eigenen Title, etwa
   `Video-Anleitungen | Hivebuy Hilfecenter`, damit die beiden Seiten unterscheidbar sind.
4. Falls es eine englische Videoseite gibt oder geben soll, verknüpfe sie mit
   `/hilfecenter-videos`. Falls nicht, bleibt die Seite korrekt ohne hreflang.

---

## Defekt 2: `html lang` widerspricht dem hreflang

Das ist der größte der technischen Punkte, weil er die gesamte Site betrifft.

**Befund: drei verschiedene Werte im Einsatz.**

| `html lang` | Seiten |
|---|---|
| `de` | 75 |
| `de-de` | 45 |
| `en` | 60 |

45 deutsche Seiten deklarieren im HTML `lang="de-de"`, während ihr hreflang `de` sagt.
Die Seite widerspricht sich also selbst: das Dokument gibt sich als
deutschlandspezifisch aus, die Sprachauszeichnung als allgemein deutschsprachig.

**Dazu drei Seiten, deren `lang` dem eigenen URL-Baum widerspricht:**

| Seite | `html lang` | Realität |
|---|---|---|
| `/webinare` | `en` | deutsche Seite |
| `/whitepaper-blog` | `en` | deutsche Seite |
| `/en/blog` | `de-de` | englischer Baum |

Das sind wieder die Listing-Seiten. Dieselben vier Templates, denen auch der Canonical
fehlt. Der Zusammenhang ist eindeutig: die Listing-Templates sind falsch konfiguriert.

**Anweisung:**

1. Setz `lang="de"` auf allen deutschen Seiten. Da Hivebuy den DACH-Raum adressiert,
   also auch Österreich und die Schweiz, ist `de-de` zu eng. `de-de` sagt Google
   ausdrücklich Deutschland und nicht den deutschsprachigen Raum.
2. Setz `lang="en"` auf allen `/en/`-Seiten.
3. Korrigiere die drei Listing-Seiten oben zuerst, dort ist der Wert schlicht falsch,
   nicht nur zu eng.
4. Regel für künftige Seiten: `html lang` und `hreflang` müssen denselben Wert tragen.
   Wenn hreflang `de` sagt, sagt `lang` auch `de`.

In HubSpot ist das die Spracheinstellung der Seite beziehungsweise des Blogs, nicht
etwas, das man pro Seite im Editor überschreibt. Die 45 `de-de`-Seiten hängen
vermutlich an einer Domain- oder Blog-Spracheinstellung, die auf Deutsch (Deutschland)
statt Deutsch steht.

---

## Defekt 3: `x-default` fehlt vollständig

**Befund:** Keine einzige der 180 Seiten setzt `hreflang="x-default"`.

`x-default` sagt Google, welche Fassung an Nutzer ausgeliefert werden soll, deren
Sprache zu keiner der ausgezeichneten Varianten passt. Ohne den Eintrag entscheidet
Google selbst, und bei einem deutschen Unternehmen mit englischer Fassung fällt diese
Entscheidung oft auf die deutsche Seite, auch bei einem französischen oder
spanischen Nutzer.

**Anweisung:** Ergänze auf **allen 118 Seiten mit hreflang** einen dritten Eintrag, der
auf die englische Fassung zeigt. Englisch ist die richtige Wahl für `x-default`, weil
es die international zugänglichere Sprache ist.

Für jedes Paar sieht der vollständige Block danach so aus, hier am Beispiel Preise:

```html
<link rel="alternate" hreflang="de"        href="https://www.hivebuy.com/preise-hivebuy">
<link rel="alternate" hreflang="en"        href="https://www.hivebuy.com/en/pricing">
<link rel="alternate" hreflang="x-default" href="https://www.hivebuy.com/en/pricing">
```

Das ist eine Template-Änderung, keine 118 Einzeleingriffe.

---

## Defekt 4: `de-de` in zwei hreflang-Auszeichnungen

**Befund:** 116 Auszeichnungen nutzen `de`, genau zwei nutzen `de-de`. Das sind die
Blog-Listings.

**Anweisung:** Auf `de` umstellen, damit die Site einen einzigen Wert nutzt. Details
in `blog-fix-anleitung.md`, Schritt 4. Nach der Korrektur von Defekt 2 sollte das
mit erledigt sein, weil es dieselbe Spracheinstellung ist.

---

## Strukturentscheidung: die englischen Slugs

Kein Defekt im technischen Sinn, aber die größte offene Inkonsistenz.

**Befund: 41 der 59 englischen Seiten tragen den deutschen Slug**, nur 18 sind
tatsächlich übersetzt.

Übersetzt, also richtig gemacht:

```
/preise-hivebuy              -> /en/pricing
/ueber-hivebuy               -> /en/about-us
/kontakt                     -> /en/contact-us
/rechnungsmanagement         -> /en/invoice-management
/it-abteilung                -> /en/it-department
/kundenreferenzen            -> /en/references
/ressourcen                  -> /en/resources
/deine-karriere-bei-hivebuy  -> /en/career
/finanzabteilung             -> /en/finance
/produktdemo                 -> /en/product-tour
/integrationen               -> /en/integrations
/hilfecenter-videos          -> /en/helpcenter
/kundenbericht-thermondo     -> /en/customer-review-thermondo
/workflows-finanzen          -> /en/workflows-finance
/analysen-reportings         -> /en/analytics-reportings
/whitepaper_anwendungen_ki   -> /en/whitepaper_application_ki
/whitepaper_softwareimplementierung -> /en/whitepaper_implementation
/webinar-produktdemo         -> /en/webinar-productdemo
```

Nicht übersetzt, deutscher Slug im englischen Baum:

```
/en/industrien/logistik            /en/industrien/gesundheitswesen
/en/industrien/handel              /en/industrien/fertigung
/en/industrien/dienstleistungen    /en/industrien/kmu-dezentrale-organisationen
/en/ki-agenten-backoffice          /en/ki-agenten-bedarfsanforderung
/en/ki-agenten-finance             /en/ersparnisrechner_hivebuy
/en/lösungen                       /en/testzugang
/en/integration-datev              /en/integration-dvelop
/en/integration-netsuite           /en/integration-sap-ecc
/en/integration-sap-s4-hana        /en/integration-sap-business-one
/en/integration-microsoft-dynamics /en/workflows-einkauf
und weitere, darunter alle /en/case_study_* und /en/webinar-*
```

Besonders auffällig: `/en/lösungen` mit Umlaut im englischen Baum, und
`/en/analytics-reportings`, wo "reportings" kein idiomatisches Englisch ist.

**Anweisung, und hier musst du eine Richtungsentscheidung treffen:**

**Option A, konsequent übersetzen.** Die 41 gespiegelten Slugs auf englische Slugs
umziehen, alte per 301 weiterleiten, hreflang zieht automatisch nach. Sauberste
Lösung, aber 41 Redirects und ein temporärer Rankingdip auf den englischen Seiten.

**Option B, nur die schmerzhaften Fälle anfassen, empfohlen.** Die englischen Seiten
haben laut Analytics ohnehin kaum Traffic, ein Vollumzug lohnt den Aufwand nicht.
Zieh nur die vier Fälle, die aktiv schaden:

| Von | Nach | Grund |
|---|---|---|
| `/en/lösungen` | `/en/solutions` | Umlaut im englischen Baum, Canonical liefert ihn unkodiert aus |
| `/en/industrien/*` | `/en/industries/*` | sechs Seiten, "industrien" ist für englische Leser nicht erschließbar |
| `/en/analytics-reportings` | `/en/analytics-reporting` | Grammatikfehler im Slug |
| `/en/workflows-einkauf` | `/en/workflows-purchasing` | zentrale Abteilungsseite |

Die Integrationsseiten (`/en/integration-datev` und so weiter) und die Case Studies
kannst du liegen lassen. Produkt- und Firmennamen sind sprachneutral, `integration-datev`
liest sich auch auf Englisch korrekt.

Ich empfehle Option B. Der englische Baum trägt derzeit zu wenig Traffic, um 41
Redirects zu rechtfertigen, aber `/en/lösungen` und `/en/industrien/*` sind für
englischsprachige Nutzer echte Verständnishürden.

---

## Strategische Frage: Content-Abdeckung

Kein technischer Punkt, aber die eigentliche Weichenstellung.

Der englische Baum deckt **Produkt, Preise, Integrationen, Branchen und Case Studies**
ab, also die Entscheidungsphase. Er deckt **Blog, Webinare, Whitepaper und Hilfecenter**
praktisch nicht ab, also die Informationsphase und die Nachbetreuung.

Ein englischsprachiger Interessent kann sich das Produkt ansehen und Preise vergleichen,
findet aber keinen Grund, vorher auf die Seite zu kommen, und keinen Inhalt, der ihn
zum Wiederkommen bringt. Genau die Inhalte, die Nachfrage erzeugen, existieren nur
auf Deutsch.

**Drei mögliche Haltungen, bitte eine wählen:**

1. **Englisch ist Pflichtprogramm für internationale Interessenten, die schon von
   Hivebuy wissen.** Dann ist der aktuelle Zustand richtig. Dann aber bitte auch
   `hreflang="en"` vom Blog entfernen, wie in `blog-fix-anleitung.md` beschrieben,
   und keinen englischen Blog-Hub vorhalten, hinter dem nichts liegt.
2. **Englisch soll aktiv Nachfrage erzeugen.** Dann brauchst du englischen Content,
   und der sinnvolle Einstieg sind nicht 45 Blogposts, sondern die fünf bis sieben
   Artikel mit dem stärksten Suchvolumen, plus die Whitepaper, die schon übersetzt sind.
3. **Englisch wird zurückgebaut.** Legitime Option, wenn DACH das Zielsegment ist.
   Dann würde ich den englischen Baum auf Produkt, Preise, Kontakt und Case Studies
   reduzieren und die halbleeren Bereiche stilllegen, statt sie zu pflegen.

Aus den Zahlen heraus spricht viel für Variante 1 oder 3. Der deutsche Blog zieht
selbst noch keinen Traffic, und eine zweite Sprache zu bedienen, bevor die erste
funktioniert, verteilt den Aufwand auf die falsche Achse.

---

## Reihenfolge

| Schritt | Umfang | Aufwand | Priorität |
|---|---|---|---|
| Defekt 2, `html lang` vereinheitlichen | 48 Seiten, aber Spracheinstellung | 1 h | hoch |
| Defekt 1, `/en/helpcenter` neu verknüpfen | 2 Seiten | 15 min | hoch |
| Defekt 3, `x-default` ergänzen | Template, wirkt auf 118 Seiten | 1 h | mittel |
| Defekt 4, `de-de` im Blog | 2 Seiten | siehe Blog-Anleitung | mittel |
| Slug-Entscheidung, Option B | 9 Seiten plus Redirects | 3 h | mittel |
| Content-Abdeckung entscheiden | Strategie | Diskussion | vor allem anderen klären |

Die Defekte 1 bis 4 sind unstrittig und können sofort umgesetzt werden. Die
Slug-Entscheidung und die Content-Frage hängen an der strategischen Haltung zu
Englisch und sollten in dieser Reihenfolge geklärt werden.

---

## Was nicht angefasst werden darf

Die 59 Sprachpaare selbst. Selbstreferenz, Reziprozität und Zielauflösung sind zu
100 Prozent korrekt, das ist bei zweisprachigen Sites selten. Wer an der
hreflang-Logik dreht, riskiert diesen Zustand. Alle Änderungen oben sind Ergänzungen
(`x-default`), Wertkorrekturen (`lang`, `de-de`) oder eine einzelne Umverknüpfung
(Hilfecenter), keine Umbauten an der Paarungslogik.

---

## Verifikation

```bash
UA="Mozilla/5.0"

# lang und hreflang einer Seite gegenprüfen
curl -sS -A "$UA" https://www.hivebuy.com/preise-hivebuy \
  | grep -Eo '<html[^>]*lang="[^"]+"|hreflang="[^"]+"[^>]*href="[^"]+"'

# x-default site-weit zählen, erwartet nach dem Fix 118
for u in / /en/ /preise-hivebuy /en/pricing; do
  echo -n "$u "; curl -sS -A "$UA" "https://www.hivebuy.com$u" | grep -c 'x-default'
done
```
