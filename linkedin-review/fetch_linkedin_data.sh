#!/usr/bin/env bash
#
# fetch_linkedin_data.sh
# Fetch LinkedIn paid (Sponsored/Ads) campaign data + performance analytics.
#
# Uses the LinkedIn Marketing API (versioned REST endpoints).
# Requires an access token with the scopes: r_ads, r_ads_reporting.
#
# Output: JSON files written to ./data/ plus a printed summary.
#
# Config (env vars, all optional except the token in .env):
#   LINKEDIN_ACCESS_TOKEN   read from .env (required)
#   LINKEDIN_VERSION        API version header, default 202506 (YYYYMM)
#   LOOKBACK_DAYS           analytics window, default 730 (~2 years)
#   ACCOUNT_IDS             space-separated numeric account ids to restrict to
#                           (default: auto-discover all accessible accounts)
#
set -euo pipefail

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Create it with LINKEDIN_ACCESS_TOKEN=..." >&2
  exit 1
fi
set -a; . ./.env; set +a

: "${LINKEDIN_ACCESS_TOKEN:?LINKEDIN_ACCESS_TOKEN is not set in .env}"
LINKEDIN_VERSION="${LINKEDIN_VERSION:-202506}"
LOOKBACK_DAYS="${LOOKBACK_DAYS:-730}"

for bin in curl jq; do
  command -v "$bin" >/dev/null || { echo "ERROR: $bin is required" >&2; exit 1; }
done

BASE="https://api.linkedin.com/rest"
OUT="data"
mkdir -p "$OUT"

# ---------------------------------------------------------------------------
# HTTP helper: api_get <path-with-query> <output-file>
# Prints HTTP status; aborts on non-2xx with the error body.
# ---------------------------------------------------------------------------
api_get() {
  local url="$1" outfile="$2" code
  code=$(curl -sS -o "$outfile" -w "%{http_code}" \
    -H "Authorization: Bearer ${LINKEDIN_ACCESS_TOKEN}" \
    -H "LinkedIn-Version: ${LINKEDIN_VERSION}" \
    -H "X-Restli-Protocol-Version: 2.0.0" \
    "$url")
  if [[ "$code" != 2* ]]; then
    echo "  HTTP $code for: $url" >&2
    echo "  Response: $(cat "$outfile")" >&2
    return 1
  fi
  echo "  HTTP $code -> $outfile"
}

# URL-encode the colons in a URN so Restli parses it (urn:li:x -> urn%3Ali%3Ax)
enc_urn() { printf '%s' "$1" | sed 's/:/%3A/g'; }

# ---------------------------------------------------------------------------
# Date range for analytics (versioned Restli structured format)
# ---------------------------------------------------------------------------
END_Y=$(date -u +%Y);  END_M=$(date -u +%-m);  END_D=$(date -u +%-d)
START_EPOCH=$(( $(date -u +%s) - LOOKBACK_DAYS*86400 ))
START_Y=$(date -u -d "@$START_EPOCH" +%Y)
START_M=$(date -u -d "@$START_EPOCH" +%-m)
START_D=$(date -u -d "@$START_EPOCH" +%-d)
DATE_RANGE="(start:(year:${START_Y},month:${START_M},day:${START_D}),end:(year:${END_Y},month:${END_M},day:${END_D}))"

# Metrics we pull for performance analysis.
FIELDS="dateRange,pivotValues,impressions,clicks,costInLocalCurrency,costInUsd,externalWebsiteConversions,oneClickLeads,leadGenerationMailContactInfoShares,likes,comments,shares,follows,videoViews,videoCompletions,landingPageClicks,totalEngagements,approximateMemberReach"

echo "=== LinkedIn paid-campaign fetch ==="
echo "API version: ${LINKEDIN_VERSION} | lookback: ${LOOKBACK_DAYS}d | range: ${START_Y}-${START_M}-${START_D} .. ${END_Y}-${END_M}-${END_D}"
echo

# ---------------------------------------------------------------------------
# 1. Discover ad accounts (unless ACCOUNT_IDS provided)
# ---------------------------------------------------------------------------
echo "[1/4] Ad accounts"
if [[ -n "${ACCOUNT_IDS:-}" ]]; then
  echo "  Using provided ACCOUNT_IDS: ${ACCOUNT_IDS}"
  ids=$ACCOUNT_IDS
else
  api_get "${BASE}/adAccountUsers?q=authenticatedUser" "${OUT}/account_users.json"
  # account field looks like urn:li:sponsoredAccount:123456789
  ids=$(jq -r '.elements[]?.account | split(":") | .[-1]' "${OUT}/account_users.json" | sort -u | tr '\n' ' ')
  if [[ -z "${ids// }" ]]; then
    echo "  No ad accounts returned. Token may lack r_ads scope or has no ad accounts." >&2
    exit 1
  fi
  echo "  Discovered account ids: ${ids}"
fi

# Fetch full account details
echo '{"elements":[]}' > "${OUT}/accounts.json"
for id in $ids; do
  if api_get "${BASE}/adAccounts/${id}" "${OUT}/account_${id}.json"; then
    jq -s '{elements: (.[0].elements + [.[1]])}' \
      "${OUT}/accounts.json" "${OUT}/account_${id}.json" > "${OUT}/accounts.tmp" \
      && mv "${OUT}/accounts.tmp" "${OUT}/accounts.json"
  fi
done

# ---------------------------------------------------------------------------
# 2. Campaign groups + 3. Campaigns (per account)
# ---------------------------------------------------------------------------
echo "[2/4] Campaign groups"
echo '{"elements":[]}' > "${OUT}/campaign_groups.json"
for id in $ids; do
  if api_get "${BASE}/adAccounts/${id}/adCampaignGroups?q=search&pageSize=1000" "${OUT}/cg_${id}.json"; then
    jq -s '{elements: (.[0].elements + (.[1].elements // []))}' \
      "${OUT}/campaign_groups.json" "${OUT}/cg_${id}.json" > "${OUT}/cg.tmp" \
      && mv "${OUT}/cg.tmp" "${OUT}/campaign_groups.json"
  fi
done

echo "[3/4] Campaigns"
echo '{"elements":[]}' > "${OUT}/campaigns.json"
for id in $ids; do
  if api_get "${BASE}/adAccounts/${id}/adCampaigns?q=search&pageSize=1000" "${OUT}/camp_${id}.json"; then
    jq -s '{elements: (.[0].elements + (.[1].elements // []))}' \
      "${OUT}/campaigns.json" "${OUT}/camp_${id}.json" > "${OUT}/camp.tmp" \
      && mv "${OUT}/camp.tmp" "${OUT}/campaigns.json"
  fi
done

# ---------------------------------------------------------------------------
# 4. Analytics per account: lifetime (ALL) and monthly, pivoted by CAMPAIGN
# ---------------------------------------------------------------------------
echo "[4/4] Analytics (pivot=CAMPAIGN)"
echo '{"elements":[]}' > "${OUT}/analytics_lifetime.json"
echo '{"elements":[]}' > "${OUT}/analytics_monthly.json"
for id in $ids; do
  acct_enc=$(enc_urn "urn:li:sponsoredAccount:${id}")
  common="q=analytics&pivot=CAMPAIGN&dateRange=${DATE_RANGE}&accounts=List(${acct_enc})&fields=${FIELDS}"

  if api_get "${BASE}/adAnalytics?${common}&timeGranularity=ALL" "${OUT}/an_all_${id}.json"; then
    jq -s '{elements: (.[0].elements + (.[1].elements // []))}' \
      "${OUT}/analytics_lifetime.json" "${OUT}/an_all_${id}.json" > "${OUT}/an.tmp" \
      && mv "${OUT}/an.tmp" "${OUT}/analytics_lifetime.json"
  fi

  if api_get "${BASE}/adAnalytics?${common}&timeGranularity=MONTHLY" "${OUT}/an_month_${id}.json"; then
    jq -s '{elements: (.[0].elements + (.[1].elements // []))}' \
      "${OUT}/analytics_monthly.json" "${OUT}/an_month_${id}.json" > "${OUT}/an.tmp" \
      && mv "${OUT}/an.tmp" "${OUT}/analytics_monthly.json"
  fi
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo
echo "=== Summary ==="
printf "Ad accounts:      %s\n" "$(jq '.elements | length' "${OUT}/accounts.json")"
printf "Campaign groups:  %s\n" "$(jq '.elements | length' "${OUT}/campaign_groups.json")"
printf "Campaigns:        %s\n" "$(jq '.elements | length' "${OUT}/campaigns.json")"
printf "Analytics rows:   %s (lifetime) / %s (monthly)\n" \
  "$(jq '.elements | length' "${OUT}/analytics_lifetime.json")" \
  "$(jq '.elements | length' "${OUT}/analytics_monthly.json")"

echo
echo "Top spend (lifetime, by campaign pivot):"
jq -r '
  .elements
  | map({camp: (.pivotValues[0] // "n/a"),
         spend: (.costInLocalCurrency // "0" | tonumber),
         clicks: (.clicks // 0), impr: (.impressions // 0),
         conv: (.externalWebsiteConversions // 0)})
  | sort_by(-.spend) | .[:15][]
  | "  \(.camp)  spend=\(.spend|(.*100|round)/100)  clicks=\(.clicks)  impr=\(.impr)  conv=\(.conv)"
' "${OUT}/analytics_lifetime.json" 2>/dev/null || echo "  (no analytics rows)"

echo
echo "Done. Raw JSON in ${OUT}/"
