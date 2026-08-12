# Bereinigungs-Engine für HubSpot-Kontaktdaten

Umsetzung von Variante b aus [`../../hubspot-kontaktdaten-audit.md`](../../hubspot-kontaktdaten-audit.md):
ein externes Skript gegen die HubSpot-CRM-API. Nur Standardbibliothek, Python 3.11+.

In Claude Code wird die Engine über `/hubspot-dq` gefahren
(siehe [`../../.claude/commands/hubspot-dq.md`](../../.claude/commands/hubspot-dq.md)).

## Grundprinzip

**Dry-Run ist der Default und lässt sich nicht umgehen.** Ein Lauf liest, wendet die
Regeln an und schreibt einen CSV-Diff. Geschrieben wird erst, wenn diese CSV mit
`--apply` zurückgegeben wird — und dann nur die Zeilen mit `freigabe=ja`.

Technisch abgesichert: `HubSpotClient` wird ohne `allow_write=True` erzeugt und
blockiert jeden nicht-lesenden Aufruf mit `WriteBlocked`, bevor er das Netz erreicht.

Nur Änderungen mit Konfidenz `high` bekommen `freigabe=ja` vorbelegt. `medium` und
`low` landen mit `freigabe=nein` in derselben Datei und setzen `dq_status=pruefen`.

## Einrichtung

```bash
export HUBSPOT_PRIVATE_APP_TOKEN=pat-eu1-…
python3 -m scripts.dq.run --check-scopes
```

Benötigte Scopes im Private App:

| Scope | wofür |
|---|---|
| `crm.objects.contacts.read` | alle Analysephasen |
| `crm.schemas.contacts.read` | Property-Erkennung |
| `crm.objects.contacts.write` | `--apply` |
| `crm.schemas.contacts.write` | `--create-properties` |

## Bedienung

```bash
# Regeltests (kein Netzwerk)
python3 -m scripts.dq.test_rules

# Vollständiger Dry-Run, schreibt nichts
python3 -m scripts.dq.run --out befund --portal 145132698

# Einzelne Phasen
python3 -m scripts.dq.run --phases 2,3,4 --out befund

# Phase 04 auf die Import-Kohorte begrenzen
python3 -m scripts.dq.run --phases 4 --source IMPORT --out befund

# Nachvollziehbarkeits-Properties anlegen (einmalig)
python3 -m scripts.dq.run --create-properties

# Freigegebene Zeilen schreiben
python3 -m scripts.dq.run --apply befund/aenderungen.csv
```

`--dry-run` zusätzlich zu `--apply` oder `--create-properties` zeigt, was passieren
würde, ohne es zu tun.

## Phasen

Die Reihenfolge ist nicht beliebig. Phase 02 muss vor Phase 03 laufen, sonst entstehen
Kontakte namens „Bestellung Reichelt".

| Phase | Inhalt |
|---|---|
| `0` | Meldet, welche der fünf `dq_`-Properties fehlen. Ändert nichts. |
| `1` | Leere Geisterdatensätze finden → eigene CSV, `freigabe` steht auf `nein`. |
| `2` | Funktionspostfächer erkennen und `kontakt_typ` setzen. **Vor Phase 3.** |
| `3` | Vor-/Nachname aus der E-Mail ableiten, nur bei leerem Vornamen. |
| `4` | Vertauschte Vor-/Nachnamen erkennen und drehen. |
| `5` | Namen, Anrede und Telefon (E.164) normalisieren. |
| `6` | `country`, `hs_language`, `contact_typ__channel_` aus Quelle und TLD ableiten. |

## Dateien

| Datei | Inhalt |
|---|---|
| `lexicon.py` | Nachschlagelisten: ~1.500 Vornamen, Rollen-Token, Partikel, Titel, Freemail, TLD→Land. Reine Daten. |
| `rules.py` | Entscheidungslogik als reine Funktionen. Kein Netzwerk, keine Seiteneffekte. |
| `client.py` | HubSpot-API: Suche mit Paginierung, Batch-Update, Batch-Archive, Retry mit Backoff. |
| `pipeline.py` | Die Phasen. Erzeugen `Change`-Objekte, schreiben nichts. |
| `run.py` | CLI, CSV-Ausgabe, `--apply`. |
| `test_rules.py` | 151 Prüfungen gegen echte Fälle aus dem Portal. |

## Die zentralen Leitplanken im Code

Jede steht dort, weil sie in einem Live-Dry-Run konkret aufgeschlagen ist.

**Ein Swap braucht ein Signal außerhalb des Lexikons.** `rules.detect_swap` wertet drei
unabhängige Signale aus (Vornamen-Lexikon, Reihenfolge im Local Part, Anrede). Das
Lexikon allein reicht nie für `high`, weil Namen wie `Wolf`, `Günther`, `Martin` oder
`Peter` Vor- *und* Nachname sein können. Ohne Bestätigung durch E-Mail oder Anrede →
`medium` → Prüfliste.

**Zusammengesetzte Namen brauchen alle Teile im Lexikon.** `Straib-Lorenz` enthält
`Lorenz`, ist aber ein Nachname. Würde `is_given` einen Teiltreffer genügen lassen,
tauschte die Routine `Julianna Straib-Lorenz` fälschlich um.

**Die Position des Initials entscheidet, nichts anderes.** `b.weigler@` bedeutet
„Vorname beginnt mit b". Das umgekehrte Muster `full.initial` ist ambig — `alexander.p`
ist `vorname.nachnameinitial`, `gajic.r` ist `nachname.vornameinitial` — und wird
bewusst ignoriert. Bei Freemail-Domains greift das Initial-Signal gar nicht.

**Trümmerfelder werden nicht getauscht.** Enthält ein Namensfeld ein Leerzeichen, eine
Ziffer oder endet auf `-`, wird es zur Reparatur gemeldet statt gedreht. Sonst wird aus
`Lena-` / `Kristin Deisler` etwas noch Falscheres.

**Mindestens drei Buchstaben je Namensteil.** Ohne diese Prüfung entsteht aus
`el-jazouli.s@` der Name „El S" und aus `m.priller-passreiter@` „M Passreiter".

**Funktionspostfächer bekommen nie einen Personennamen.** Phase 03 prüft das selbst
noch einmal, unabhängig davon, ob Phase 02 schon gelaufen ist.

**`name_quelle = manuell` wird nie überschrieben.** Handpflege schlägt Automatik.

**Alte Werte landen in `dq_befund`.** Jeder Schreibvorgang ist damit umkehrbar.

**Nie stillschweigend abschneiden.** Die Search-API blättert nicht über 10.000 Treffer.
`client.search` warnt sichtbar, wenn das Fenster erschöpft ist; die Phasen mit
Vollabdeckung nutzen `search_all_by_id`, das per `hs_object_id` weiterläuft.

## Grenzen

- **Reihenfolge ohne Lexikontreffer und ohne Domain-Konvention ist nicht entscheidbar.**
  Diese Fälle gehen auf `pruefen`. Das ist gewollt: falsch-negativ kostet Prüfzeit,
  falsch-positiv beschädigt Daten.
- **`GIVEN` in `lexicon.py` ist der wichtigste Stellhebel.** Jeder ergänzte Vorname
  verschiebt Fälle von „prüfen" nach „automatisch". Erweitern, dann `test_rules.py`
  fahren, dann einen Dry-Run vergleichen.
- **Die Geschlechtsheuristik für den Anrede-Abgleich ist listenbasiert** und bei
  international besetzten Vornamen unscharf. Widersprüche sind Prüfhinweise, keine Urteile.
- **Phase 05 und 06 scannen alle Kontakte** und brauchen mehrere Minuten. Im Hintergrund
  starten.
- Ein Kontakt kann in mehreren Phasen auftauchen. `--apply` gruppiert die Änderungen
  pro Kontakt zu einem Update; bei widersprüchlichen Zeilen zum selben Feld gewinnt
  die letzte in der CSV.
