@echo off
REM start_tiger.bat - windows double-clickable wrapper
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_tiger.ps1" %*
