#!/usr/bin/env bash
# Daily customer-finding run: collect a fresh NZ segment (rotating), qualify it, then send a
# small QA-gated warm-up batch of cold emails, and process any opt-out replies. Every email
# passes the GPT pre-send QA gate (right business + right contact + flawless text) and the
# per-country legal gate. Duplicate-send guard + suppression prevent re-emailing anyone.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe"
C="auckland-local-website-pilot"

export DATABASE_URL="sqlite:///./a2_local.db"
export LIVE_API_CALLS_ENABLED=true LEAD_COLLECTION_ENABLED=true
export WEBSITE_VERIFICATION_ENABLED=true CONTACT_VERIFICATION_ENABLED=true
export URL_PROBE_ENABLED=true PHASE4_LIVE_URL_PROBE=true CONTACT_DISCOVERY_ENABLED=true
export AI_GENERATION_ENABLED=true EMAIL_DRAFTING_ENABLED=true
export EMAIL_JUDGE_ENABLED=true EMAIL_JUDGE_MODE=RULE_ONLY EMAIL_RELEVANCE_AGENT_ENABLED=true
export COUNTRY_COMPLIANCE_ENFORCED=true PRE_SEND_QA_ENABLED=true
export PIPELINE_SKIP_PROCESSED=true   # idempotent: each cycle only processes NEW leads

# Rotate the target each cycle to explore a fresh segment. NZ + Australia only (both allow
# B2B cold email with unsubscribe); the country gate blocks anything else anyway.
TARGETS=()
for CITY in Auckland Wellington Christchurch Hamilton Tauranga Dunedin Napier "Palmerston North" \
            Sydney Melbourne Brisbane Perth Adelaide Hobart Geelong Newcastle; do
  for CAT in barber beauty_salon cleaning_service; do
    TARGETS+=("$CITY|$CAT|New Zealand")
  done
done
# Australian cities use country=Australia.
i=0
for T in "${TARGETS[@]}"; do
  case "$T" in Sydney*|Melbourne*|Brisbane*|Perth*|Adelaide*|Hobart*|Geelong*|Newcastle*)
    TARGETS[$i]="${T%|*}|Australia";; esac
  i=$((i + 1))
done
CF=".acquisition_counter"
i=$(cat "$CF" 2>/dev/null || echo 0)
n=${#TARGETS[@]}; idx=$((i % n)); echo $((i + 1)) > "$CF"
SEG="${TARGETS[$idx]}"
CITY="${SEG%%|*}"; rest="${SEG#*|}"; CAT="${rest%%|*}"; COUNTRY="${rest#*|}"

echo "==== acquisition: $CAT in $CITY, $COUNTRY ===="
"$PY" -m alembic upgrade head >/dev/null 2>&1 || true
"$PY" -m app.cli.main campaign seed >/dev/null
"$PY" -m app.cli.main collect osm --campaign "$C" --city "$CITY" --country "$COUNTRY" \
  --category "$CAT" --limit 20 --commit 2>&1 | grep -E "status=" || true
"$PY" -m app.cli.main normalize run --campaign "$C" --all-raw --commit >/dev/null 2>&1
"$PY" -m app.cli.main quality candidates --campaign "$C" --commit >/dev/null 2>&1
"$PY" -m app.cli.main verify full --campaign "$C" --limit 300 --commit >/dev/null 2>&1
"$PY" -m app.cli.main score candidates --campaign "$C" --limit 300 --commit >/dev/null 2>&1
"$PY" -m app.cli.main insight generate --campaign "$C" --limit 300 --commit >/dev/null 2>&1
"$PY" -m app.cli.main email generate --campaign "$C" --limit 300 --commit >/dev/null 2>&1
"$PY" -m app.cli.main judge emails --campaign "$C" --commit >/dev/null 2>&1
"$PY" -m app.cli.main review build-queue --campaign "$C" --commit >/dev/null 2>&1

echo "==== QA-gated warm-up send ===="
"$PY" scripts/send_qa_batch.py --send

echo "==== process opt-out replies ===="
"$PY" scripts/process_optouts.py
echo "==== done ===="
