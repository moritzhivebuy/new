# Standing Prompt: Wettbewerbs-Monitoring

Dieser Text ist der Prompt, der bei jedem geplanten Lauf (Routine / Cron) in einer
frischen Session ausgeführt wird. Er ist absichtlich vollständig und
voraussetzungsfrei formuliert, da die Session keinen Vorkontext hat.

---

Du führst den regelmäßigen Wettbewerbs-Scan für Hivebuy durch. Arbeite im Repo
`moritzhivebuy/new` auf dem Branch `claude/competitor-monitoring-hivebuy-h78tmv`.

**Ablauf:**

1. `competitor-monitoring/competitors.json` lesen. Für jede Site mit
   `"role": "competitor"` sowie für `hivebuy` selbst:
   `node competitor-monitoring/scripts/crawl.mjs --site <id> --max-pages 150`
   Das schreibt `competitor-monitoring/snapshots/<id>/<YYYY-MM-DD>.json`.
2. Falls für eine Site bereits ein älterer Snapshot existiert:
   `node competitor-monitoring/scripts/diff.mjs --site <id>`
   Der Änderungsbericht ist die faktische Grundlage, nicht deine Erinnerung.
3. Ergänzend Websuche nutzen für Signale, die nicht auf der Website stehen:
   Pressemeldungen, Finanzierungsrunden, Personalwechsel, neue Reviews auf
   OMR / Capterra / trusted.de / G2, Vergleichsartikel, in denen Hivebuy oder ein
   Wettbewerber auftaucht.
4. Bericht schreiben nach
   `competitor-monitoring/reports/<YYYY-MM-DD>-monitoring.md` nach der Struktur in
   `competitor-monitoring/REPORT_TEMPLATE.md`.
5. Committen und pushen (`git push -u origin claude/competitor-monitoring-hivebuy-h78tmv`).
6. Nur wenn es echte Veränderungen gibt: kurze Zusammenfassung (max. 10 Zeilen)
   als Notion-Seite anlegen bzw. in Slack posten, je nach konfiguriertem Kanal.
   Ohne Veränderungen: nur committen, keine Benachrichtigung.

**Qualitätsregeln:**

- Jede Aussage über einen Wettbewerber braucht eine Quelle: Snapshot-Feld
  (`snapshots/<id>/<date>.json`), Diff-Zeile oder URL. Keine Behauptungen aus
  dem Gedächtnis, keine geschätzten Zahlen ohne Kennzeichnung.
- Blockierte oder fehlgeschlagene Abrufe explizit als Lücke ausweisen
  (`errors` im Snapshot), nicht stillschweigend weglassen.
- Pflicht ist die Bewertung, nicht die Aufzählung: Was bedeutet die Änderung für
  Hivebuys Positionierung, Preis-Story, Content-Lücken? Maximal fünf
  Handlungsempfehlungen, priorisiert.
- Widersprüchliche Zahlen (z. B. Lieferantenzahl in Marketing vs. Presse) als
  Widerspruch benennen, nicht auflösen durch Auswahl.
- Rechtliches: nur öffentlich zugängliche Seiten abrufen, keine Logins, keine
  Umgehung von Zugangsbeschränkungen, moderate Crawl-Rate (Default 700 ms Pause).
