---
description: HubSpot Kontaktdaten prüfen (Dry-Run) und Befund berichten
allowed-tools: Bash(python3 -m scripts.dq.run:*), Bash(python3 -m scripts.dq.test_rules), Read, Grep
argument-hint: "[--phases 2,3,4] [--source IMPORT] | apply <csv> | scopes"
---

# HubSpot Datenqualitäts-Routine

Argumente des Aufrufs: `$ARGUMENTS`

Du fährst die Bereinigungsroutine für das HubSpot-Kontaktobjekt. Die Engine liegt
unter `scripts/dq/`, der zugehörige Befundbericht unter
`hubspot-kontaktdaten-audit.md`.

## Grundregel

**Diese Routine schreibt niemals unaufgefordert nach HubSpot.** Der Standardlauf
ist ein Dry-Run, der nur liest und einen CSV-Diff erzeugt. Geschrieben wird
ausschließlich, wenn der Nutzer eine geprüfte CSV ausdrücklich freigibt.

## Ablauf

### Fall A: kein Argument, oder Argumente beginnen mit `--`

Das ist der Regelfall — ein Dry-Run.

1. Regeltests fahren: `python3 -m scripts.dq.test_rules`
   Schlagen sie fehl, **hier abbrechen** und die Fehler berichten. Ein Lauf mit
   defekten Regeln ist wertlos.
2. Dry-Run starten. Ohne weitere Angabe alle Phasen:
   ```
   python3 -m scripts.dq.run --out befund --portal 145132698 $ARGUMENTS
   ```
   Der volle Lauf dauert mehrere Minuten (Phase 5 und 6 scannen alle Kontakte).
   Starte ihn deshalb im Hintergrund und warte auf die Benachrichtigung, statt
   zu pollen.
3. Aus `befund/aenderungen.csv` einen Befund berichten, der folgendes enthält:
   - je Phase: geprüft / automatisch / zur Prüfung
   - **eine Stichprobe von 15–25 automatischen Änderungen im Klartext**, Format
     `alt -> neu   e-mail` — der Nutzer muss sehen, was passieren würde
   - die Risikoprüfung aus Schritt 4
   - Veränderungen gegenüber dem letzten Lauf, falls ein früherer Befund vorliegt
4. **Risikoprüfung, immer ausführen.** Zähle in den freigegebenen Zeilen
   (`freigabe=ja`):
   - Swaps, die einen bekannten Vornamen ins Nachnamensfeld verschieben → muss 0 sein
   - getauschte Felder, die ein Leerzeichen, eine Ziffer oder `@ | / \` enthalten → muss 0 sein
   - abgeleitete Namen mit ein oder zwei Zeichen → muss 0 sein
   - Rollenpostfächer, die trotzdem einen Personennamen bekommen → muss 0 sein
   Ist eine Zahl größer als 0, **melde das als Blocker** und empfehle keine
   Freigabe. Es ist dann ein Regelfehler, kein Datenfehler.
5. Zum Schluss den nächsten Schritt nennen: CSV prüfen, `freigabe`-Spalte
   anpassen, dann `/hubspot-dq apply befund/aenderungen.csv`.

### Fall B: Argumente beginnen mit `apply`

Der Nutzer gibt eine geprüfte CSV frei.

1. Prüfen, ob die Datei existiert. Zählen, wie viele Zeilen `freigabe=ja` tragen
   und wie viele Kontakte betroffen sind.
2. **Diese Zahlen nennen und die Bestätigung des Nutzers abwarten**, bevor
   geschrieben wird — außer der Nutzer hat im selben Satz schon zugestimmt.
3. Schreiben: `python3 -m scripts.dq.run --apply <pfad>`
4. Bei HTTP 403 ist der Scope `crm.objects.contacts.write` nicht gesetzt. Dann
   nicht herumprobieren, sondern den Nutzer auf
   Settings → Integrations → Private Apps → Scopes verweisen.
5. Ergebnis berichten: geschriebene Kontakte, und dass die alten Werte in
   `dq_befund` stehen und der Vorgang damit umkehrbar ist.

### Fall C: Argumente beginnen mit `scopes`

`python3 -m scripts.dq.run --check-scopes` ausführen und das Ergebnis berichten.

## Wöchentlicher Automatiklauf

Der wiederkehrende Lauf ist als **Routine/Trigger im Claude-Konto** einzurichten, nicht
über `CronCreate` — das ist session-lokal und läuft nach sieben Tagen aus.

Einzurichten unter *Automations / Routinen* mit Zeitplan **montags 07:03 Uhr** und
diesem Prompt:

> Fahre die HubSpot-Datenqualitätsroutine als Dry-Run: `/hubspot-dq`.
> Berichte den Befund inklusive Stichprobe und Risikoprüfung. Schreibe nichts nach
> HubSpot und lösche nichts. Wenn sich gegenüber der Vorwoche nichts Wesentliches
> geändert hat, halte den Bericht kurz.

Läuft der Trigger in einer frischen Session, muss `HUBSPOT_PRIVATE_APP_TOKEN` in der
Umgebung gesetzt sein.

## Wichtig

- **Löschungen niemals automatisch.** `befund/loeschkandidaten.csv` enthält die
  leeren Geisterdatensätze. Deren Löschung ist irreversibel und läuft nur nach
  ausdrücklicher Aufforderung des Nutzers, in einem eigenen Schritt.
- **Zahlen nicht schönen.** Wenn ein Lauf abbricht oder eine Phase weniger
  Kontakte gesehen hat als erwartet, sag das. Eine Warnung über ein erschöpftes
  Suchfenster ist ein Befund, keine Randnotiz.
- **Keine Zahlen erfinden.** Alles, was du berichtest, kommt aus der CSV oder aus
  der Konsolenausgabe des Laufs.
- Antworte auf Deutsch.
