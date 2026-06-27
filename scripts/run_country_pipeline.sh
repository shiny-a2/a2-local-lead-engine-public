#!/usr/bin/env bash
# Collect leads across all cities of a country (from app/config/geography.yaml),
# then run the whole FREE keyless pipeline through Phase 9. Sending stays dry-run.
#
# Usage: bash scripts/run_country_pipeline.sh "<Country>" [big|small|all] [category] [limit]
#   e.g. bash scripts/run_country_pipeline.sh "Australia" big beauty_salon 25
set -uo pipefail
cd "$(dirname "$0")/.."

PY=".venv/Scripts/python.exe"
CAMPAIGN="auckland-local-website-pilot"
COUNTRY="${1:-New Zealand}"
SIZE="${2:-big}"
CATEGORY="${3:-beauty_salon}"
LIMIT="${4:-25}"

export DATABASE_URL="sqlite:///./a2_local.db"
export LIVE_API_CALLS_ENABLED=true LEAD_COLLECTION_ENABLED=true
export WEBSITE_VERIFICATION_ENABLED=true CONTACT_VERIFICATION_ENABLED=true
export URL_PROBE_ENABLED=true PHASE4_LIVE_URL_PROBE=true
export EMAIL_DRAFTING_ENABLED=true
if [ -n "${OPENAI_API_KEY:-}" ] || { [ -f .env ] && grep -qE '^OPENAI_API_KEY=.+' .env; }; then
  export AI_GENERATION_ENABLED=true
  export OPENAI_EMAIL_MODEL="${OPENAI_EMAIL_MODEL:-gpt-4o-mini}"
else
  export EMAIL_LOCAL_WRITER_ENABLED=true
fi
export EMAIL_JUDGE_ENABLED=true EMAIL_JUDGE_MODE=RULE_ONLY
export GLOBAL_OUTREACH_KILL_SWITCH=true EMAIL_SENDING_ENABLED=false

"$PY" -m alembic upgrade head >/dev/null 2>&1 || true
"$PY" -m app.cli.main campaign seed >/dev/null

echo "==== Collecting $CATEGORY across $COUNTRY ($SIZE cities) ===="
"$PY" -m app.cli.main geo cities --country "$COUNTRY" --size "$SIZE" 2>/dev/null \
  | grep -v '^count=' | while IFS= read -r CITY; do
    [ -z "$CITY" ] && continue
    echo "-- $CITY --"
    "$PY" -m app.cli.main collect osm --campaign "$CAMPAIGN" --city "$CITY" \
      --country "$COUNTRY" --category "$CATEGORY" --limit "$LIMIT" --commit 2>&1 \
      | grep -E "status=|stored=" || true
    sleep 6   # be polite to the free Overpass endpoint
done

echo "==== Processing pipeline (normalize -> Phase 9) ===="
"$PY" -m app.cli.main normalize run --campaign "$CAMPAIGN" --all-raw --commit 2>&1 | grep -E "verdict"
"$PY" -m app.cli.main quality candidates --campaign "$CAMPAIGN" --commit
"$PY" -m app.cli.main evidence consolidate --campaign "$CAMPAIGN" --commit >/dev/null
"$PY" -m app.cli.main verify full --campaign "$CAMPAIGN" --limit 1000 --commit 2>&1 | grep -E "verdict"
"$PY" -m app.cli.main score candidates --campaign "$CAMPAIGN" --limit 1000 --commit 2>&1 | grep -E "verdict"
"$PY" -m app.cli.main insight generate --campaign "$CAMPAIGN" --limit 1000 --commit 2>&1 | grep -E "verdict"
"$PY" -m app.cli.main email generate --campaign "$CAMPAIGN" --limit 1000 --commit 2>&1 | grep -E "verdict"
"$PY" -m app.cli.main judge emails --campaign "$CAMPAIGN" --commit 2>&1 | grep -E "verdict"
"$PY" -m app.cli.main review build-queue --campaign "$CAMPAIGN" --commit 2>&1 | grep -E "human_review_run"
echo "==== Done. Sending stays dry-run/blocked. ===="
