@echo off
REM Daily customer-finding: collect a fresh NZ segment, qualify, send a QA-gated warm-up batch,
REM and process opt-out replies. Every email passes the GPT no-blunder QA gate. Throttled.
cd /d "%~dp0"
"C:\Program Files\Git\bin\bash.exe" scripts/run_acquisition.sh
