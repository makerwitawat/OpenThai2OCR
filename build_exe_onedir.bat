@echo off
setlocal
cd /d "%~dp0"

rem Build the folder (onedir) version:  build_exe_onedir.bat [--skip-tests]
rem Steps: install deps -> pytest -> PyInstaller -> copy models -> run the built exe once (tools\exe_smoke.py)
set "SKIP=0"
if /i "%~1"=="--skip-tests" set "SKIP=1"

set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"

"%PY%" --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found. Install Python 3.10+ and add it to PATH, or create a .venv in this folder.
  exit /b 1
)

echo [1/5] Installing dependencies...
"%PY%" -m pip install -q -r requirements.txt -r requirements-dev.txt -r requirements-build.txt
if errorlevel 1 (echo [ERROR] Dependency install failed. & exit /b 1)

if "%SKIP%"=="1" (
  echo [2/5] Skipping tests ^(--skip-tests^)
) else (
  echo [2/5] Running tests...
  "%PY%" -m pytest -q
  if errorlevel 1 (echo [ERROR] Tests failed - build aborted. Use --skip-tests to override. & exit /b 1)
)

echo [3/5] Building onedir ^(folder^)...
"%PY%" -m PyInstaller OpenThai2OCR_onedir.spec --noconfirm --clean
if errorlevel 1 (echo [ERROR] Build failed. & exit /b 1)

echo [4/5] Copying models to dist...
if not exist "dist\OpenThai2OCR\models" mkdir "dist\OpenThai2OCR\models"
xcopy /e /i /y "models\*" "dist\OpenThai2OCR\models\" >nul
if errorlevel 1 (echo [ERROR] Copying models failed. & exit /b 1)

echo [5/5] Smoke test: launching the built exe...
"%PY%" tools\exe_smoke.py dist\OpenThai2OCR\OpenThai2OCR.exe
if errorlevel 1 (echo [ERROR] Smoke test of the built exe failed. & exit /b 1)

echo.
echo Build OK:  dist\OpenThai2OCR\OpenThai2OCR.exe  ^(distribute the whole folder^)
echo Note: the exe is not code-signed, so Windows may warn on first run. See README.
exit /b 0
