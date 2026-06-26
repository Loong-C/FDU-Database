@echo off
setlocal

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

cd /d "%ROOT%\frontend" || exit /b 1

if not exist "node_modules" (
  echo Installing frontend dependencies...
  call npm.cmd ci --cache ".npm-cache"
  if errorlevel 1 (
    echo.
    echo npm install failed.
    pause
    exit /b 1
  )
)

echo Frontend: http://127.0.0.1:5173
echo Press Ctrl+C to stop.
echo.

call npm.cmd run dev -- --host 127.0.0.1 --port 5173

echo.
echo Frontend stopped or failed to start.
pause
