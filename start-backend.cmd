@echo off
setlocal

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

cd /d "%ROOT%" || exit /b 1

echo Backend: http://127.0.0.1:8000
echo Press Ctrl+C to stop.
echo.

".venv\Scripts\python.exe" backend\manage.py runserver 127.0.0.1:8000

echo.
echo Backend stopped or failed to start.
pause
