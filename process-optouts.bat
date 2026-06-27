@echo off
REM Fetch info@ mailbox and suppress anyone who replied "unsubscribe". Sends nothing.
cd /d "%~dp0"
".venv\Scripts\python.exe" scripts\process_optouts.py
