@echo off
REM Continuous customer-finding engine (no schedule - runs cycles forever with pauses).
cd /d "%~dp0"
"C:\Program Files\Git\bin\bash.exe" scripts/run_forever.sh
