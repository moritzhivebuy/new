# Queries

Alle SQL-Statements der CS-Routinen, benannt. Der Name ist gleichzeitig der
Cache-Schlüssel: die MCP-Antwort zu `active_customers` gehört nach
`data/active_customers.json`.

Ausgeführt werden sie über `mcp__HubSpot__query_crm_data`. Einschränkungen der
HubSpot-SQL, die hier relevant sind: keine Aliase, kein `CASE WHEN`, keine
Subqueries, kein `JOIN`, kein `HAVING`, kein `COALESCE`, ein Objekttyp pro
Query. Datumsvergleiche gehen über `BETWEEN` mit Datumsstrings.

---

## `active_customers` — die Basisabfrage

Die einzige Abfrage, die Routine 3 tatsächlich braucht. **Bewusst ohne
Zeitfenster:** Fenster, abgelaufene und fehlende Vertragsdaten werden in Python
gebildet. Filtert man das Fenster in SQL, verschwinden genau die 25 Kunden, um
die es eigentlich geht.

```sql
SELECT hs_object_id, name, domain, contract_start_date, contract_end_date,
       contract_duration_months_, company_mrr, contracted_users,
       hubspot_owner_id, hs_last_sales_activity_timestamp
FROM COMPANY
WHERE lifecyclestage = 'customer'
  AND churn_date IS NULL
```

REST-Äquivalent (API-Modus, `hubspot.SEARCH_TRANSLATIONS`):
`POST /crm/v3/objects/companies/search` mit
`lifecyclestage EQ customer` + `churn_date NOT_HAS_PROPERTY`.

---

## Ad-hoc-Varianten

Nicht von den Skripten verwendet — nützlich, um einen Block direkt in der
Session gegenzuprüfen. `{today}` / `{today_plus_90}` als `YYYY-MM-DD` einsetzen.

### `renewals_window` — Vertragsende im Fenster

```sql
SELECT hs_object_id, name, domain, contract_start_date, contract_end_date,
       contract_duration_months_, company_mrr, contracted_users,
       hubspot_owner_id, hs_last_sales_activity_timestamp
FROM COMPANY
WHERE lifecyclestage = 'customer'
  AND churn_date IS NULL
  AND contract_end_date BETWEEN '{today}' AND '{today_plus_90}'
ORDER BY contract_end_date ASC
```

### `renewals_expired` — abgelaufene Vertragsdaten

`<` funktioniert (am 12.08.2026 geprüft, identisches Ergebnis wie die
`BETWEEN`-Variante mit weit zurückliegender Untergrenze).

```sql
SELECT hs_object_id, name, contract_end_date, company_mrr, hubspot_owner_id,
       hs_last_sales_activity_timestamp
FROM COMPANY
WHERE lifecyclestage = 'customer'
  AND churn_date IS NULL
  AND contract_end_date < '{today}'
ORDER BY contract_end_date ASC
```

### `renewals_missing` — ohne Vertragsdatum

```sql
SELECT hs_object_id, name, contract_start_date, contract_duration_months_,
       company_mrr, hubspot_owner_id, hs_last_sales_activity_timestamp
FROM COMPANY
WHERE lifecyclestage = 'customer'
  AND churn_date IS NULL
  AND contract_end_date IS NULL
ORDER BY company_mrr DESC
```

### `mrr_base` — Gesamtbasis zur Kontrolle

Liefert TSV, keine Datensätze. Nur zur Gegenprüfung der Prozentwerte, nicht
cachebar.

```sql
SELECT SUM(company_mrr), COUNT(*)
FROM COMPANY
WHERE lifecyclestage = 'customer'
  AND churn_date IS NULL
```

### `churned_but_customer` — Voraussetzung 3 messen

```sql
SELECT hs_object_id, name, churn_date, company_mrr
FROM COMPANY
WHERE lifecyclestage = 'customer'
  AND churn_date BETWEEN '2000-01-01' AND '{today}'
ORDER BY churn_date DESC
```

---

## `deals` — Deals inkl. Company-Verknüpfung

**Nicht über SQL.** Die Verknüpfung kommt aus der Associations-API; die MCP-SQL
kann nur `COMPANY.name` als Cross-Object-Spalte ausgeben, und ein Join über
Firmennamen ist bei den vorhandenen Dubletten unzuverlässig. `hubspot.deals()`
verwendet deshalb:

```
GET /crm/v3/objects/deals
    ?limit=100
    &properties=dealname,dealstage,pipeline,amount,closedate,createdate,
                hs_is_closed,hs_is_closed_won,hubspot_owner_id,hs_lastmodifieddate
    &associations=companies
```

Achtung: die Antwort enthält **jede Company doppelt**, einmal als
`deal_to_company` und einmal als `deal_to_company_unlabeled`. Immer über
`hubspot.association_company_ids()` deduplizieren.

Stage-Labels über `GET /crm/v3/pipelines/deals`.

Zur reinen Sichtprüfung in der Session geht auch:

```sql
SELECT hs_object_id, dealname, dealstage, pipeline, amount, closedate,
       hs_is_closed, COMPANY.name
FROM DEAL
WHERE hs_is_closed = 'false'
```

## Routine 1 und 2

Noch nicht definiert. Die vier Engagement-Quellen (Routine 1) und die
Ticket-Aggregation über `SUPPORT_PIPELINE = '0'` (Routine 2) kommen hier dazu,
sobald die Routinen gebaut werden — mit demselben Namensschema, damit der
Cache-Modus ohne Sonderfälle funktioniert.
