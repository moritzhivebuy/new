# Datenmodell HubSpot (Abschnitt 0)

Stand der Verifikation: 12.08.2026, gegen den Live-Account geprüft.

> Ergänzen: Abschnitt 0 des ursprünglichen CS-Routinen-Dokuments gehört hier
> hinein. Alles unten Stehende ist am Live-Account nachgeprüft und weicht
> möglicherweise von einer älteren Fassung ab.

## Basisdefinition "aktiver Kunde"

```
lifecyclestage = 'customer' AND churn_date IS NULL
```

* **74 Unternehmen** laut CRM, **108.199,73 EUR** Summe `company_mrr`
  (12.08.2026). Nach Abzug der Ausschlussliste (siehe unten) rechnen die
  Routinen mit **73 Kunden**; die MRR-Basis bleibt gleich, weil der
  ausgeschlossene Datensatz keinen MRR-Wert hat.
* `churn_date` ist laut Property-Beschreibung *"Last day of the contract not
  date of the termination letter"*, also das Vertragsende gekündigter Kunden,
  nicht das Datum des Kündigungsschreibens.
* Es gibt weitere Companies mit `lifecyclestage = 'customer'` **und** gesetztem
  `churn_date`. Die sind gechurnt, hängen aber am Kunden-Lifecycle. Deshalb ist
  der `churn_date IS NULL`-Filter zwingend und darf nicht wegfallen, solange es
  keinen eigenen Lifecycle-Wert gibt (siehe Voraussetzung 3 in `SKILL.md`).

Diese Definition steckt in genau einer Funktion: `hubspot.active_customers()`.
Keine Routine formuliert sie erneut.

## Relevante COMPANY-Properties

| Property | Typ | Anmerkung |
|---|---|---|
| `hs_object_id` | String | Record-ID. Nie `id` verwenden. |
| `name` | String | **HTML-escaped** ausgeliefert (`Lanes &amp; Planes`). Vor jeder Ausgabe und jedem Join durch `norm_name()`. |
| `domain` | String | Teils mit Protokoll (`https://vda-mannheim.de/`), teils ohne, teils `www.`. Als Join-Schlüssel unbrauchbar ohne Normalisierung. |
| `lifecyclestage` | Enum | Basisfilter. |
| `churn_date` | Datum (ms) | Basisfilter. |
| `contract_start_date` | Datum (ms) | Vertragsbeginn. |
| `contract_end_date` | Datum (ms) | **Vertragsende, nicht Kündigungsstichtag.** |
| `contract_duration_months_` | Zahl | Laufzeit in Monaten. Trailing Underscore ist Teil des Namens. |
| `company_mrr` | Zahl | Kann **leerer String** sein, nicht nur `NULL`. |
| `contracted_users` | Zahl | Bei den aktuell fälligen Verträgen durchgängig leer. |
| `hubspot_owner_id` | String | Bei einigen aktiven Kunden leer. |
| `hs_last_sales_activity_timestamp` | Datum (ms) | Letzte Sales-Aktivität. Fehlt bei einigen Kunden ganz. |

Nicht vorhanden, obwohl naheliegend: **kein Feld für die Kündigungsfrist.**
Verwandt existieren nur `sonderkundigungsrecht` und `hs_next_renewal_date`
(letzteres aus dem HubSpot-Contracts-Objekt abgeleitet, im Account nicht
gepflegt). Die Frist ist deshalb eine Konstante im Code:
`hubspot.NOTICE_PERIOD_MONTHS`.

Weitere MRR-artige Properties existieren (`mrr`, `monthly_recurring_revenue`,
`forecasted_mrr`, `upsell_mrr__company_`, `test` mit Label "Sales MRR"). Die
Routinen verwenden ausschließlich `company_mrr`. Wenn das falsch ist, an einer
Stelle in `hubspot.py` ändern, nicht in den Routinen.

## Fallen beim Auslesen

1. **Datumsfelder sind Millisekunden-Timestamps als String.** Die MCP liefert
   zusätzlich ein `*_iso`-Feld, die REST-API nicht. `to_ms()` versteht beide.
2. **Zahlen sind Strings, leere Werte sind `''`.** `float('')` wirft. Immer
   `to_float()`, das `None` zurückgibt.
3. **Leere Properties fehlen in der Antwort komplett.** Ein nicht vorhandener
   Key bedeutet "leer", nicht "Fehler".
4. **Namen sind HTML-escaped.** Betrifft jeden Kunden mit `&` im Namen.
5. **Aggregate der MCP kommen als TSV-Text**, nicht als Datensatzliste. Für die
   Routinen deshalb immer Detailzeilen abfragen und in Python aggregieren.
6. **`IS NULL` vs. leerer String.** In der MCP-SQL funktioniert
   `churn_date IS NULL`; in der REST-Search-API entspricht das
   `NOT_HAS_PROPERTY`.

## Bekannte Datenlücken (Stand 12.08.2026)

* **13 aktive Kunden** mit `contract_end_date` in der Vergangenheit.
* **11 aktive Kunden** ohne `contract_end_date` (12 im CRM, minus d.velop).
* Zusammen **24 von 73 Kunden (32,9 %)** und **17.310,00 EUR MRR (16,0 %)** ohne
  belastbares Vertragsende.
* **4 aktive Kunden** ohne `company_mrr`, **8** ohne `hubspot_owner_id`.
* **d.velop** (401316842690) steht auf `lifecyclestage = 'customer'`, ist aber
  kein Kunde (Angabe Moritz, 12.08.2026). Der Datensatz hat weder MRR noch Owner
  noch Vertragsdaten. Bis das Feld im CRM korrigiert ist, greift
  `hubspot.NON_CUSTOMERS`.
* Dublettenverdacht: `JMarquardt Audiovisual` (17554843636 / 49463093489),
  `igus` (188745085157 / 401851610339 / 401764367589),
  `rebuy` / `reBuy reCommerce Services` (401457651913 / 18622719466).

Diese Zahlen sind kein Fixpunkt, sondern der Ausgangsstand. Die Routine
berechnet sie bei jedem Lauf neu und weist sie im Block *Datenqualität* aus.

## Owner

* Seit dem 12.08.2026 liegt die Zuordnung bei **Bettina Fischer** (109171979,
  aktiv) mit 61 aktiven Kunden. Vorher lief fast alles auf **Jan Vollers**
  (33319925), inaktiv. Weitere Owner in der Basis: Robert Eickmeyer
  (255483530), Dennis Hartmann (77804274), 8 Kunden ohne Zuordnung.
* `mcp__HubSpot__search_owners` bzw. `GET /crm/v3/owners` liefert
  standardmäßig nur aktive Owner. Ausgeschiedene Kollegen stehen unter
  `?archived=true`. Genau die brauchen wir, um verwaiste Zuordnungen zu sehen.
* `hubspot.owner_info()` lädt beide Seiten und markiert inaktive Owner.

## Tickets (Vorgriff Routine 2)

`SUPPORT_PIPELINE = '0'` ist als harte Konstante in `hubspot.py` gesetzt. Nicht
zur Laufzeit ableiten.
