@echo off
set "appDir=%~dp0"
powershell -ExecutionPolicy Bypass -File "%appDir%\ps_scripts\main.ps1"
pause
