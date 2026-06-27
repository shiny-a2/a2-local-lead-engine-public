#!/usr/bin/env bash
# Continuous customer-finding engine. Runs acquisition cycles back-to-back forever (no fixed
# schedule), pausing between cycles to respect the free API limits. Opt-out processing happens
# inside each cycle. A single-instance lock prevents duplicate engines on re-logon.
cd "$(dirname "$0")/.."
SLEEP="${1:-2400}"          # seconds between cycles (default 40 min)
STALE=$((SLEEP + 1800))     # lock considered stale after sleep + 30 min
LOCK=".engine.lock"

now() { date +%s 2>/dev/null || echo 0; }

if [ -f "$LOCK" ]; then
  last=$(cat "$LOCK" 2>/dev/null || echo 0)
  if [ $(( $(now) - last )) -lt "$STALE" ]; then
    echo "A2 engine already running (lock fresh); exiting this instance."
    exit 0
  fi
fi

echo "A2 continuous engine started (cycle pause ${SLEEP}s)."
while true; do
  now > "$LOCK"
  bash scripts/run_acquisition.sh 2>&1 | tail -8
  now > "$LOCK"
  echo "---- cycle done; pausing ${SLEEP}s ----"
  sleep "$SLEEP"
done
