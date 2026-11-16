@echo off
setlocal
cd /d "%~dp0"

rem Build the single-file exe (model embedded):  build_exe.bat [--skip-tests]
rem Steps: install deps -> pytest -> PyInstaller -> run the built exe once (tools\exe_smoke.py)
set "SKIP=0"
if /i "%~1"=="--skip-tests" set "SKIP=1"

set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"

"%PY%" --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found. Install Python 3.10+ and add it to PATH, or create a .venv in this folder.
  exit /b 1
)

echo [1/4] Installing dependencies...
"%PY%" -m pip install -q -r requirements.txt -r requirements-dev.txt -r requirements-build.txt
if errorlevel 1 (echo [ERROR] Dependency install failed. & exit /b 1)

if "%SKIP%"=="1" (
  echo [2/4] Skipping tests ^(--skip-tests^)
) else (
  echo [2/4] Running tests...
  "%PY%" -m pytest -q
  if errorlevel 1 (echo [ERROR] Tests failed - build aborted. Use --skip-tests to override. & exit /b 1)
)

echo [3/4] Building one-file exe ^(model embedded^)...
"%PY%" -m PyInstaller OpenThai2OCR.spec --noconfirm --clean
if errorlevel 1 (echo [ERROR] Build failed. & exit /b 1)

echo [4/4] Smoke test: launching the built exe...
"%PY%" tools\exe_smoke.py dist\OpenThai2OCR.exe
if errorlevel 1 (echo [ERROR] Smoke test of the built exe failed. & exit /b 1)

echo.
echo Build OK:  dist\OpenThai2OCR.exe  ^(single file, ready to distribute^)
echo Note: the exe is not code-signed, so Windows may warn on first run. See README.
exit /b 0
