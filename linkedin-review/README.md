# LinkedIn Review

Tooling zum Abruf von LinkedIn Marketing API Daten (Kampagnen etc.).

## Setup

1. `.env` im Ordner `linkedin-review/` anlegen (wird NICHT committet):

   ```
   LINKEDIN_ACCESS_TOKEN=<dein-token>
   ```

2. Umgebung braucht ausgehenden Zugriff auf `api.linkedin.com`
   (Netzwerkzugriff "Voll" oder Custom-Allowlist mit `api.linkedin.com`).

## Nutzung

```bash
./fetch_linkedin_data.sh [AD_ACCOUNT_ID]
```

Standard-Account: `509511309`. Ruft die Kampagnen über die REST API ab
(Header `LinkedIn-Version: 202606`, `X-Restli-Protocol-Version: 2.0.0`),
listet sie mit Name und Status auf und speichert die Rohantwort unter
`data/campaigns_<ID>.json`.
