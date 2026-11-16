@echo off
setlocal
cd /d "%~dp0"

rem Run from source. Extra arguments are passed to app.py (e.g. run_web.bat --port 5100 --window)
set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"

"%PY%" --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found. Install Python 3.10+ and add it to PATH, or create a .venv in this folder.
  pause
  exit /b 1
)

"%PY%" -c "import flask, waitress, onnxruntime, cv2, pymupdf" >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Dependencies are missing. Run:
  echo     "%PY%" -m pip install -r requirements.txt
  pause
  exit /b 1
)

echo Starting OpenThai2.0 OCR - the browser or app window opens automatically. Press Ctrl+C to stop.
"%PY%" app.py %*
set "RC=%errorlevel%"
if not "%RC%"=="0" (
  echo.
  echo [ERROR] The program exited with code %RC%.
  pause
)
exit /b %RC%
