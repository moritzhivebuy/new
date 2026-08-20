# HubSpot Service Key erweitern: was genau fehlt

Stand: 2026-08-20, geprüft am laufenden Token.

---

## Ausgangslage

`HUBSPOT_PRIVATE_APP_TOKEN` ist in der Umgebung gesetzt und **funktioniert**. Ein 403
statt 401 heißt: Token gültig, Berechtigung fehlt.

| Endpoint | Status | Bedeutung |
|---|---|---|
| `account-info/v3/details` | **200** | erlaubt |
| `crm/v3/objects/contacts` | **200** | erlaubt |
| `cms/v3/blogs/posts` | 403 | Scope fehlt |
| `cms/v3/pages/site-pages` | 403 | Scope fehlt |
| `cms/v3/pages/landing-pages` | 403 | Scope fehlt |
| `cms/v3/url-redirects` | 403 | Scope fehlt |
| `cms/v3/domains` | 403 | Scope fehlt |
| `marketing/v3/forms` | 403 | Scope fehlt |

Der Token hat also CRM- und Account-Rechte, aber keinen CMS-Zugriff.

---

## Was hinzugefügt werden muss

Nicht geraten. HubSpot nennt die benötigten Scopes im 403-Body selbst, im Feld
`errors[].context.requiredGranularScopes`. Ich habe jeden Endpoint einzeln abgefragt,
Lesen und Schreiben getrennt. Das Ergebnis:

| Operation | Erforderlich, ODER-verknüpft |
|---|---|
| `GET` site-pages | `content.site_pages.read` oder `content` |
| **`PATCH` site-pages** | **nur `content`** |
| `PATCH` site-page Entwurf | nur `content` |
| `POST` push-live (publizieren) | nur `content` |
| `GET` landing-pages | `content.landing_pages.read` oder `content` |
| `PATCH` landing-pages | `content.landing_pages.write` oder `content` |
| **`GET` blog posts** | **nur `content`** |
| **`PATCH` blog posts** | **nur `content`** |
| `POST` blogpost publizieren | nur `content` |
| `GET` url-redirects | nur `content` |
| `POST` url-redirect anlegen | nur `content` |
| `GET` domains | `cms.domains.read` oder `cms.domains.write` oder `content` |

### Pflicht: `content`

**Das ist der einzige Scope, den du brauchst, und er ist unvermeidbar.**

Die granularen Varianten wie `content.site_pages.read` existieren, reichen aber nicht:

- Für **Blogposts** gibt es überhaupt keine granulare Alternative, weder lesen noch
  schreiben. Nur `content`.
- Für **`PATCH` site-pages** ebenfalls nicht. Ein `content.site_pages.write` gibt es
  nicht, HubSpot verlangt dort `content`.

Da beide Aufgaben zum Umfang gehören, führt kein Weg an `content` vorbei.

### Empfohlen: `cms.domains.read`

Nur Lesen. Damit sehe ich die Domain- und Spracheinstellung, die hinter dem
`de-de`-Problem auf 45 Seiten steckt. `content` deckt es auch ab, aber wenn du den
Scope ohnehin einzeln setzen kannst, ist die Leseform sauberer.

### Optional: `business-intelligence`

Für Traffic-Daten ohne die MCP-Werkzeuge, inklusive der **Traffic-Quellen**, die im
MCP-Report fehlten. Damit ließe sich die offene Frage beantworten, ob
`/ki-beschaffungsplattform` bezahlten oder organischen Traffic hat.

Diesen Scope habe ich nicht gegengeprüft, den Namen also mit Vorbehalt.

### Nicht empfehlen: `cms.source_code.write`

Damit könnte ich theoretisch die Templates anfassen, also Canonical, H1 und `x-default`.
**Ich rate davon ab.** Zwei Gründe: der Scope erlaubt Schreibzugriff auf den gesamten
Quellcode des Themes, und er greift nur bei Templates im Entwickler-Dateisystem, nicht
bei per Design Manager gebauten Vorlagen. Template-Arbeit bleibt besser Handarbeit mit
Vorschau und Versionierung.

### Was der Token heute schon hat

26 Scopes, alle aus CRM, Automation, Files und Marketing-Campaigns, darunter
`crm.objects.contacts.read`, `files.write`, `marketing.campaigns.write`, `oauth`.
**Kein einziger CMS-Scope.** Deshalb schlagen alle acht CMS-Endpoints mit 403 fehl.

### Kein vollständiger Trockenlauf ohne `content`

Ich hatte einen Lese-zuerst-Ansatz vorgeschlagen. Das funktioniert nur teilweise: mit
`content.site_pages.read` und `content.landing_pages.read` könnte ich Seiten lesen,
**Blogposts aber nicht**, weil es dort keinen granularen Lese-Scope gibt. Ein
Trockenlauf über alle 88 Seiten ist damit nicht möglich.

Sicherheit stellen wir also anders her: du erteilst `content`, und ich zeige jede Charge
vor der Ausführung. Der erste Schreibzugriff geht auf **eine** Seite, danach prüfe ich
das Ergebnis live, bevor irgendetwas in Serie läuft.

---

## Vorgehen in HubSpot

1. Einstellungen, Integrationen, **Private Apps**
2. Die App öffnen, zu der der bestehende Token gehört. Falls unklar welche: der Token
   hat aktuell CRM-Contacts- und Account-Rechte, das grenzt es meist ein.
3. Reiter **Scopes**
4. `content` hinzufügen, dazu `cms.domains.read`, optional `business-intelligence`
5. Speichern. **Achtung:** HubSpot erzeugt bei Scope-Änderungen einen neuen Token.
6. Den neuen Token als Umgebungsvariable `HUBSPOT_PRIVATE_APP_TOKEN` in den
   Einstellungen der Claude-Code-Umgebung ersetzen, **nicht in den Chat schreiben**.
7. Neue Session starten, damit die Variable greift.

### Zur Vorsicht

Ein reiner Lese-Trockenlauf ist nicht möglich, siehe oben: Blogposts haben keinen
granularen Lese-Scope. Stattdessen: erster Schreibzugriff auf genau eine Seite, danach
Live-Kontrolle, dann Chargen mit Vorabbestätigung.

---

## Was damit möglich wird

| Aufgabe | Endpoint | Vorher | Mit `content` |
|---|---|---|---|
| 14 Blogpost-Metas | `PATCH /cms/v3/blogs/posts/{id}` | nein | **ja** |
| **72 Site-Page-Metas** | `PATCH /cms/v3/pages/site-pages/{id}` | nein | **ja** |
| Meta `/en/` | dito | nein | **ja** |
| 3 `&amp;`-Titles | dito, Feld `htmlTitle` | nein | **ja** |
| 2 Money-Page-Titles | dito | nein | **ja** |
| Meta `/ki-beschaffungsplattform` | `PATCH /cms/v3/pages/landing-pages/{id}` | nein | **ja** |
| `noindex` auf 11 Landing Pages | dito | nein | **zu prüfen**, siehe unten |
| `/en/helpcenter` umhängen | Feld `translatedFromId` | nein | **wahrscheinlich** |
| Sprache je Seite auf `de` | Feld `language` | nein | **wahrscheinlich** |

Die größte Änderung gegenüber meiner letzten Einschätzung: **die 72 Site Pages sind
machbar.** Das war der Brocken mit 3 bis 4 Stunden Handarbeit. Die MCP-Schicht meldete
`writeAccess: NOT_AVAILABLE`, die REST-API kann es aber.

### Zwei Punkte, die ich erst nach Freischaltung beantworten kann

**`noindex`:** Ich bin nicht sicher, ob die Pages-API ein eigenes Feld dafür hat. Falls
nicht, wäre der Weg ein Eintrag in `headHtml`. Das war vorher riskant, weil ich das Feld
nicht lesen konnte und vorhandene Tracking-Skripte überschrieben hätte. **Mit
Lesezugriff wird es sicher**, weil ich lesen, ergänzen und zurückschreiben kann. Ich
prüfe das an einer Seite und sage dir, welcher Weg es ist, bevor ich elf Seiten anfasse.

**Entwurf gegen Live:** Die Pages- und Blog-APIs arbeiten teils auf Entwürfen, mit
`push-live` als separatem Schritt. Ich teste an einer Seite, ob eine Änderung sofort
live geht oder publiziert werden muss, und melde das Ergebnis, bevor ich in Serie gehe.

---

## Was auch mit Service Key manuell bleibt

| Aufgabe | Warum |
|---|---|
| Canonical im Listing-Template | Template-Arbeit, siehe oben, bewusst nicht per API |
| H1 in vier Templates | dito |
| `x-default` ergänzen | dito |
| Titles der Blog-Listing-Seiten | Blog-Einstellungen, kein öffentlicher API-Endpunkt |
| Domain-Spracheinstellung | vermutlich nur Oberfläche, `cms.domains.read` zeigt nur den Ist-Zustand |
| Search Console, Index-Entfernung | anderes System, kein HubSpot |
| Interne Verlinkung im Blog-Cluster | inhaltliche Arbeit im Editor |

---

## Sicherheit, bitte einmal lesen

`content` ist ein **breiter Scope**. Er erlaubt Lesen, Ändern und Löschen aller
Website-Inhalte, Blogposts und Landing Pages im Portal. Es gibt keine Möglichkeit, ihn
auf einzelne Seiten einzugrenzen, HubSpot kennt dafür keine Feingranularität.

Konkret heißt das: mit diesem Token könnte jeder, der ihn hat, die Website löschen.
Deshalb:

1. **Eigene Private App** für diese Arbeit anlegen, keinen bestehenden Token mit
   anderen Aufgaben erweitern. Dann kannst du sie danach ersatzlos löschen.
2. **Token nicht in den Chat**, nur als Umgebungsvariable. Was im Chat steht, steht im
   Transkript.
3. **Nach Abschluss löschen oder rotieren.** Die Arbeit ist endlich, der Token muss es
   auch sein.
4. Diese Session ist flüchtig, der Token überlebt sie nicht. Für jede neue Session muss
   die Variable erneut gesetzt sein. Das ist ein Vorteil, nicht ein Nachteil.
5. Ich werde vor jeder Schreib-Serie eine Charge im Trockenlauf zeigen und auf deine
   Bestätigung warten. Bei den 72 Site Pages heißt das: erst die Liste, dann die
   Ausführung.

---

## Prüfbefehl

Nach dem Setzen des neuen Tokens, zur Kontrolle ohne den Token auszugeben:

```bash
for ep in cms/v3/blogs/posts cms/v3/pages/site-pages \
          cms/v3/pages/landing-pages cms/v3/domains; do
  printf '%-34s ' "$ep"
  curl -sS -o /dev/null -w '%{http_code}\n' \
    -H "Authorization: Bearer $HUBSPOT_PRIVATE_APP_TOKEN" \
    "https://api.hubapi.com/$ep?limit=1"
done
```

Erwartet: viermal `200`. Bei `403` fehlt noch ein Scope, bei `401` ist der Token nicht
korrekt übernommen.
