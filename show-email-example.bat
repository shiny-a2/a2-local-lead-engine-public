@echo off
REM Double-click to see ONE real outreach email written by GPT (from your OpenAI key),
REM checked by the rule judge and placed in the review queue. Nothing is sent.
cd /d "%~dp0"
".venv\Scripts\python.exe" scripts\demo_gpt_draft.py
echo.
pause
