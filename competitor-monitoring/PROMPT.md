# Standing Prompt: Wettbewerbs-Monitoring

Dieser Text ist der Prompt, der bei jedem geplanten Lauf in einer frischen Session
ausgeführt wird. Er ist absichtlich vollständig und voraussetzungsfrei formuliert,
weil die Session keinen Vorkontext hat.

**Zeitplan:** Der Trigger feuert wöchentlich montags früh, der Lauf selbst hält
über die 10-Tage-Sperre unten einen 14-tägigen Rhythmus ein.

---

Du führst den regelmäßigen Wettbewerbs-Scan für Hivebuy durch. Repo
`moritzhivebuy/new`, Branch `claude/competitor-monitoring-hivebuy-h78tmv`.

**Schritt 0, Sperre:** Die Sperre gilt nur für automatische Läufe. Prüfe zuerst,
wie dieser Lauf gestartet wurde:

- **Manuell gestartet** (ein Mensch hat den Lauf in dieser Sitzung angefordert,
  "run now" gedrückt oder den Skill `competitor-scan` aufgerufen): Sperre
  überspringen, sofort mit dem Ablauf weitermachen. Ein Mensch, der den Lauf
  auslöst, will Ergebnisse, nicht den Hinweis auf die Sperre. Trägt der Bericht
  von heute schon einen Dateinamen, hänge `-2`, `-3` usw. an
  (`<YYYY-MM-DD>-monitoring-2.md`), statt den bestehenden zu überschreiben.
- **Automatisch gestartet** (Scheduler/Cron-Trigger, kein Mensch in der
  Sitzung): Prüfe `competitor-monitoring/reports/`. Ist der neueste Bericht
  weniger als 10 Tage alt, brich sofort ab, ohne Commit, ohne Notion, ohne
  Slack. Der Scan läuft 14-tägig, der Trigger wöchentlich.

Im Zweifel, wenn die Startart nicht eindeutig ist: als automatisch behandeln und
die Sperre anwenden.

**Ablauf:**

1. `competitor-monitoring/competitors.json` lesen. Für jede Site darin
   (alle Wettbewerber plus `hivebuy` selbst):
   `node competitor-monitoring/scripts/crawl.mjs --site <id> --max-pages 150`
   Das schreibt `competitor-monitoring/snapshots/<id>/<YYYY-MM-DD>.json` und die
   Screenshots nach `snapshots/<id>/screenshots/<YYYY-MM-DD>/`. Fehlt `playwright`,
   vorher `npm install --no-fund --no-audit` ausführen, sonst gibt es keine
   Screenshots.
   Scheitern alle Abrufe mit `EGRESS_BLOCKED` oder `403` vom Proxy, dann ist die
   Netzwerk-Policy der Umgebung zu restriktiv: notiere das im Bericht als
   Datenlücke, arbeite für diesen Lauf nur mit Websuche weiter und weise in der
   Slack-Nachricht ausdrücklich die gesperrten Hosts aus.
   Scheitert dagegen nur der Browser (`net::ERR_CONNECTION_RESET` auf allen
   Hosts, während `curl` dieselben Hosts mit 200 erreicht), ist das **kein**
   Policy-Problem, sondern der TLS-1.3-Handshake von Chromium am MITM-Proxy.
   `crawl.mjs` deckelt deshalb TLS auf 1.2 (`--ssl-version-max=tls1.2`), siehe
   README, Abschnitt "Chromium und der Egress-Proxy". Nicht erneut als
   Netzwerksperre diagnostizieren und nicht auf `--no-browser` ausweichen, ohne
   die TLS-Deckelung geprüft zu haben, sonst fehlen wieder alle Screenshots.
2. Für jede Site mit älterem Snapshot:
   `node competitor-monitoring/scripts/diff.mjs --site <id>`
   Der Änderungsbericht ist die faktische Grundlage, nicht deine Erinnerung.
3. Ergänzend Websuche für Signale, die nicht auf der Website stehen:
   Pressemeldungen, Finanzierungsrunden, Personalwechsel, neue Reviews auf
   OMR / Capterra / trusted.de / G2 / Gartner Peer Insights, Vergleichsartikel,
   in denen Hivebuy oder ein Wettbewerber vorkommt.
4. Bericht schreiben nach
   `competitor-monitoring/reports/<YYYY-MM-DD>-monitoring.md`, Struktur aus
   `competitor-monitoring/REPORT_TEMPLATE.md`.
5. Snapshots und Bericht committen und pushen
   (`git push -u origin claude/competitor-monitoring-hivebuy-h78tmv`).
6. Ausgabe, nur wenn es echte Veränderungen gibt:
   - **Notion:** Unterseite unter der Sammelseite "Wettbewerbs-Monitoring"
     (`page_id` 3c06f8c1-d67e-810c-a8ed-d264c4139505), Titel
     "Wettbewerbs-Monitoring <YYYY-MM-DD>". Inhalt: Kurzfassung, Tabelle der
     Signale, Handlungsempfehlungen, Link auf den Bericht im Repo.
   - **Screenshots in Notion:** Für jeden Screenshot, der eine Änderung zeigt
     (geänderte Preisseite, neues Hero, neue Landingpage): `create-file-upload`
     mit dem Dateinamen aufrufen, die PNG per `multipart/form-data` an die
     zurückgegebene `upload_url` posten (Feldname `file`, alle `upload_headers`
     mitsenden), dann `create-attachment` mit `source_file_id` und das
     `markdown_source` in die Notion-Seite einbauen. Ein bis zwei Bilder pro
     Wettbewerber, nicht alles hochladen.
     Fällt der Upload aus, weil `api.notion.com` nicht erreichbar ist: Screenshots
     sind ohnehin im Repo committet, dann in der Notion-Seite auf die Dateipfade
     im Branch verlinken und den fehlgeschlagenen Upload dort vermerken.
   - **Slack:** DM an Moritz Lienert (`U071B33N4LQ`), maximal 10 Zeilen: pro
     Wettbewerber die relevanteste Änderung, dann der Notion-Link.
   Ohne relevante Veränderungen: nur committen, keine Nachricht, keine Notion-Seite.

**Qualitätsregeln:**

- Jede Aussage über einen Wettbewerber braucht eine Quelle: Snapshot-Feld
  (`snapshots/<id>/<date>.json`), Diff-Zeile oder URL. Keine Behauptungen aus
  dem Gedächtnis, keine geschätzten Zahlen ohne Kennzeichnung.
- Blockierte oder fehlgeschlagene Abrufe explizit als Lücke ausweisen
  (`errors` im Snapshot), nicht stillschweigend weglassen.
- Pflicht ist die Bewertung, nicht die Aufzählung: Was bedeutet die Änderung für
  Hivebuys Positionierung, Preis-Story, Content-Lücken? Maximal fünf
  Handlungsempfehlungen, priorisiert.
- "Keine Änderungen" ist ein gültiges Ergebnis. Nichts erfinden, um den Bericht
  zu füllen.
- Widersprüchliche Zahlen (z. B. Lieferantenzahl in Marketing vs. Presse) als
  Widerspruch benennen, nicht durch Auswahl auflösen.
- Rechtliches: nur öffentlich zugängliche Seiten abrufen, keine Logins, keine
  Umgehung von Zugangsbeschränkungen, moderate Crawl-Rate (Default 700 ms Pause).
  Der Crawler wertet robots.txt aus und überspringt gesperrte Pfade, das Feld
  `robotsSkipped` im Snapshot zeigt, was ausgelassen wurde. Diese Prüfung nicht
  deaktivieren.
- Screenshots sind Belege, keine Deko: nur aufnehmen und in Notion legen, wo sie
  eine Aussage im Bericht stützen.
