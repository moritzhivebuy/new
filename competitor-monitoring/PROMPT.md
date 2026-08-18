# Standing Prompt: Wettbewerbs-Monitoring

Dieser Text ist der Prompt, der bei jedem geplanten Lauf in einer frischen Session
ausgeführt wird. Er ist absichtlich vollständig und voraussetzungsfrei formuliert,
weil die Session keinen Vorkontext hat.

**Zeitplan:** Der Trigger feuert wöchentlich montags früh, der Lauf selbst hält
über die 10-Tage-Sperre unten einen 14-tägigen Rhythmus ein.

---

Du führst den regelmäßigen Wettbewerbs-Scan für Hivebuy durch. Repo
`moritzhivebuy/new`, Branch `claude/competitor-monitoring-hivebuy-h78tmv`.

**Schritt 0, Sperre:** Prüfe `competitor-monitoring/reports/`. Wenn der neueste
Bericht weniger als 10 Tage alt ist, brich sofort ab, ohne Commit, ohne Notion,
ohne Slack. Der Scan läuft 14-tägig, der Trigger wöchentlich.

**Ablauf:**

1. `competitor-monitoring/competitors.json` lesen. Für jede Site darin
   (alle Wettbewerber plus `hivebuy` selbst):
   `node competitor-monitoring/scripts/crawl.mjs --site <id> --max-pages 150`
   Das schreibt `competitor-monitoring/snapshots/<id>/<YYYY-MM-DD>.json`.
   Scheitern alle Abrufe mit `EGRESS_BLOCKED`, dann ist die Netzwerk-Policy der
   Umgebung zu restriktiv: notiere das im Bericht als Datenlücke, arbeite für
   diesen Lauf nur mit Websuche weiter und weise in der Slack-Nachricht darauf hin.
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
