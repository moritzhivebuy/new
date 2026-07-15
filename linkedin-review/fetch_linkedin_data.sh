#!/usr/bin/env bash
#
# fetch_linkedin_data.sh
# Ruft die Kampagnen eines LinkedIn Ad Accounts über die Marketing REST API ab
# und listet sie mit Name und Status auf.
#
# Voraussetzung: eine .env-Datei im selben Verzeichnis mit:
#   LINKEDIN_ACCESS_TOKEN=<token>
#
# Nutzung:
#   ./fetch_linkedin_data.sh [AD_ACCOUNT_ID]
# Standard-Account: 509511309

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AD_ACCOUNT_ID="${1:-509511309}"
LINKEDIN_VERSION="202606"

# --- Token aus .env laden ---
if [[ ! -f "${SCRIPT_DIR}/.env" ]]; then
  echo "Fehler: ${SCRIPT_DIR}/.env nicht gefunden." >&2
  exit 1
fi
set -a
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/.env"
set +a

if [[ -z "${LINKEDIN_ACCESS_TOKEN:-}" ]]; then
  echo "Fehler: LINKEDIN_ACCESS_TOKEN ist in .env nicht gesetzt." >&2
  exit 1
fi

# --- API-Aufruf ---
RESPONSE_FILE="${SCRIPT_DIR}/data/campaigns_${AD_ACCOUNT_ID}.json"
mkdir -p "${SCRIPT_DIR}/data"

HTTP_STATUS=$(curl -sS -o "${RESPONSE_FILE}" -w "%{http_code}" \
  -H "Authorization: Bearer ${LINKEDIN_ACCESS_TOKEN}" \
  -H "LinkedIn-Version: ${LINKEDIN_VERSION}" \
  -H "X-Restli-Protocol-Version: 2.0.0" \
  "https://api.linkedin.com/rest/adAccounts/${AD_ACCOUNT_ID}/adCampaigns?q=search")

if [[ "${HTTP_STATUS}" != "200" ]]; then
  echo "API-Aufruf fehlgeschlagen (HTTP ${HTTP_STATUS}). Antwort:" >&2
  cat "${RESPONSE_FILE}" >&2
  exit 1
fi

# --- Kampagnen mit Name und Status auflisten ---
echo "Kampagnen fuer Ad Account ${AD_ACCOUNT_ID}:"
echo "-------------------------------------------"
if command -v jq >/dev/null 2>&1; then
  jq -r '.elements[] | "\(.id)\t\(.name // "(ohne Namen)")\t\(.status)"' "${RESPONSE_FILE}" \
    | column -t -s $'\t'
else
  echo "(jq nicht installiert - Rohantwort in ${RESPONSE_FILE})"
  cat "${RESPONSE_FILE}"
fi

echo
echo "Vollstaendige Antwort gespeichert unter: ${RESPONSE_FILE}"
