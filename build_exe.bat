@echo off
setlocal
cd /d "%~dp0"
echo [1/2] ติดตั้ง build dependency...
python -m pip install -q -r requirements.txt -r requirements-build.txt
if errorlevel 1 (echo ติดตั้งไม่สําเร็จ & exit /b 1)
echo [2/2] build exe ไฟล์เดียว (ฝังโมเดลไว้ในตัว)...
python -m PyInstaller OpenThai2OCR.spec --noconfirm --clean
if errorlevel 1 (echo Build ล้มเหลว & exit /b 1)
echo.
echo Build สําเร็จ:  dist\OpenThai2OCR.exe  (ไฟล์เดียว แจกจ่ายได้เลย)
exit /b 0