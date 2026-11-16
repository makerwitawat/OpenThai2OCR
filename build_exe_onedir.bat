@echo off
setlocal
cd /d "%~dp0"
echo [1/3] ติดตั้ง build dependency...
python -m pip install -q -r requirements.txt -r requirements-build.txt
if errorlevel 1 (echo ติดตั้งไม่สําเร็จ & exit /b 1)
echo [2/3] build exe แบบโฟลเดอร์ (onedir)...
python -m PyInstaller OpenThai2OCR_onedir.spec --noconfirm --clean
if errorlevel 1 (echo Build ล้มเหลว & exit /b 1)
echo [3/3] ก็อปปี้ models ไปที่ dist...
if not exist "dist\OpenThai2OCR\models" mkdir "dist\OpenThai2OCR\models"
xcopy /e /i /y "models\*" "dist\OpenThai2OCR\models\" >nul
if errorlevel 1 (echo ก็อปปี้ models ล้มเหลว & exit /b 1)
echo.
echo Build สําเร็จ:  dist\OpenThai2OCR\OpenThai2OCR.exe  (ต้องแจกทั้งโฟลเดอร์)
exit /b 0