@echo off
setlocal

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

cd /d "%ROOT%" || exit /b 1

if not exist ".venv\Scripts\python.exe" (
  echo [error] Missing .venv\Scripts\python.exe
  echo Create the virtual environment, then run:
  echo   .venv\Scripts\python.exe -m pip install -r backend\requirements.txt
  exit /b 1
)

if not exist "backend\.env" (
  echo [warn] Missing backend\.env
  echo Copy backend\.env.example to backend\.env and check the DB settings.
)

if /i "%~1"=="--check" (
  if not exist "frontend\node_modules" (
    echo [warn] frontend\node_modules is missing. The first normal run will install it.
  )
  echo [ok] Startup prerequisites checked.
  exit /b 0
)

if not exist "frontend\node_modules" (
  echo [setup] Installing frontend dependencies...
  pushd "frontend" || exit /b 1
  call npm.cmd ci --cache ".npm-cache"
  if errorlevel 1 (
    popd
    echo [error] npm dependency installation failed.
    exit /b 1
  )
  popd
)

echo [start] Backend:  http://127.0.0.1:8000
start "Bookstore Backend" "%ROOT%\start-backend.cmd"

echo [start] Frontend: http://127.0.0.1:5173
start "Bookstore Frontend" "%ROOT%\start-frontend.cmd"

echo.
echo Open http://127.0.0.1:5173 after both windows finish starting.
