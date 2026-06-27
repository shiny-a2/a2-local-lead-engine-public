@echo off
REM Double-click to run the whole FREE lead pipeline (collect -> ... -> human review queue).
REM Nothing is sent. Edit the city/category/limit on the line below if you want.
cd /d "%~dp0"
"C:\Program Files\Git\bin\bash.exe" scripts/run_local_pipeline.sh Auckland beauty_salon 60
echo.
echo ============================================================
echo Done. Reports are in the "reports" folder.
echo ============================================================
pause
