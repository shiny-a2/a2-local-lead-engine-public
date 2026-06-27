#!/usr/bin/env bash
# A2 Local Lead Engine - end-to-end FREE keyless pipeline runner.
#
# Data source : OpenStreetMap Overpass (no key, no signup, no credit card)
# Web verify  : direct URL probe (no Tavily key)
# Email writer: local deterministic template (no OpenAI key)
# Judge       : rule-only (no AI key)
# Sending     : DRY-RUN ONLY. Global kill switch stays ON; no real email is sent.
#
# Usage:  bash scripts/run_local_pipeline.sh [CITY] [CATEGORY] [LIMIT]
set -uo pipefail
cd "$(dirname "$0")/.."

PY=".venv/Scripts/python.exe"
CAMPAIGN="auckland-local-website-pilot"
CITY="${1:-Auckland}"
CATEGORY="${2:-barber}"
LIMIT="${3:-25}"

# --- Free keyless runtime flags (override safe code-defaults for THIS run only) ---
export DATABASE_URL="sqlite:///./a2_local.db"
export LIVE_API_CALLS_ENABLED=true        # allow the OSM HTTP call
export LEAD_COLLECTION_ENABLED=true        # allow storing collected leads
export WEBSITE_VERIFICATION_ENABLED=true   # allow Phase 4 verification commit
export CONTACT_VERIFICATION_ENABLED=true
export URL_PROBE_ENABLED=true              # keyless web probe
export PHASE4_LIVE_URL_PROBE=true          # use real probe instead of fixtures
export EMAIL_DRAFTING_ENABLED=true
# Use real GPT if a key is present either in the shell or in .env; else the free local writer.
if [ -n "${OPENAI_API_KEY:-}" ] || { [ -f .env ] && grep -qE '^OPENAI_API_KEY=.+' .env; }; then
  export AI_GENERATION_ENABLED=true            # real GPT drafting (key present)
  export OPENAI_EMAIL_MODEL="${OPENAI_EMAIL_MODEL:-gpt-4o-mini}"
  echo "(email writer: OpenAI GPT, model=$OPENAI_EMAIL_MODEL)"
else
  export EMAIL_LOCAL_WRITER_ENABLED=true        # free keyless local writer (no key)
  echo "(email writer: free local template)"
fi
export EMAIL_JUDGE_ENABLED=true            # rule-only judge
export EMAIL_JUDGE_MODE=RULE_ONLY
# Sending stays hard-blocked:
export GLOBAL_OUTREACH_KILL_SWITCH=true
export EMAIL_SENDING_ENABLED=false
export CONTROLLED_SEND_ENABLED=false
export PROVIDER_SEND_ENABLED=false

step () { echo; echo "==================== $* ===================="; }

step "0) DB migrate + seed campaign"
"$PY" -m alembic upgrade head >/dev/null 2>&1 || true
"$PY" -m app.cli.main campaign seed

step "1) Collect leads from OpenStreetMap (LIVE, free) - $CATEGORY in $CITY"
"$PY" -m app.cli.main collect osm --campaign "$CAMPAIGN" --city "$CITY" --category "$CATEGORY" --limit "$LIMIT" --commit

step "2) Normalize raw records -> candidates"
"$PY" -m app.cli.main normalize run --campaign "$CAMPAIGN" --all-raw --commit

step "3) Dedupe candidates"
"$PY" -m app.cli.main dedupe run --campaign "$CAMPAIGN" --commit

step "4) Quality gate (mark candidates ready for web verification)"
"$PY" -m app.cli.main quality candidates --campaign "$CAMPAIGN" --commit

step "5) Consolidate personalization evidence"
"$PY" -m app.cli.main evidence consolidate --campaign "$CAMPAIGN" --commit

step "6) Phase 4 - verify web presence via REAL URL probe (free, keyless)"
"$PY" -m app.cli.main verify full --campaign "$CAMPAIGN" --limit 100 --commit

step "7) Phase 5 - lead scoring"
"$PY" -m app.cli.main score candidates --campaign "$CAMPAIGN" --limit 100 --commit

step "8) Phase 6 - business insight + offer matching"
"$PY" -m app.cli.main insight generate --campaign "$CAMPAIGN" --limit 100 --commit

step "9) Phase 7 - generate email drafts (local writer, no OpenAI)"
"$PY" -m app.cli.main email generate --campaign "$CAMPAIGN" --limit 100 --commit

step "10) Phase 8 - judge drafts (rule-only)"
"$PY" -m app.cli.main judge emails --campaign "$CAMPAIGN" --commit

step "11) Phase 9 - build human review queue"
"$PY" -m app.cli.main review build-queue --campaign "$CAMPAIGN" --commit

echo
echo "==================== PIPELINE COMPLETE (through Phase 9) ===================="
echo "Sending remains DRY-RUN only. Review the human queue, then approve before any send."
