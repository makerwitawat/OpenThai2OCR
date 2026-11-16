# Build & Release — OpenThai2.0 OCR

**ไทย** | [English](BUILD.en.md)

## build ในเครื่อง (Windows)

```bat
build_exe.bat          :: ไฟล์เดียว  dist\OpenThai2OCR.exe  (ฝังโมเดลในตัว)
build_exe_onedir.bat   :: ทั้งโฟลเดอร์ dist\OpenThai2OCR\    (เปิดเร็วกว่า)
```

- **onefile** = แจกง่ายสุด แต่ทุกครั้งที่เปิดจะแตกไฟล์ไป temp (ช้าครั้งแรก ~2–8 วินาที)
- **onedir** = เปิดเร็ว แต่ต้องแจกทั้งโฟลเดอร์ (มี `_internal\` + `models\`)

สคริปต์ทั้งสองทำตามลำดับ (หยุดทันทีเมื่อขั้นไหนล้ม):

1. ติดตั้ง dependency (`requirements.txt` + `-dev` + `-build`)
2. `pytest -q` — ข้ามได้ด้วย `build_exe.bat --skip-tests`
3. PyInstaller (`OpenThai2OCR.spec` / `OpenThai2OCR_onedir.spec`)
4. (onedir) คัดลอก `models\` ไปไว้ข้าง exe
5. **smoke test exe ที่ build เสร็จ** — `tools\exe_smoke.py` เปิด exe ด้วย `--no-browser --port 5890`
   รอ `/api/health` → ยิง OCR 1 ครั้ง → สั่งปิด (CI รันขั้นเดียวกันนี้ใน `release.yml`)

- ใช้ `.venv\Scripts\python.exe` ก่อนถ้ามี ไม่งั้นใช้ `python` ใน PATH
- ข้อความในสคริปต์เป็นภาษาอังกฤษล้วน (ไฟล์ .bat เป็น ASCII) เพื่อไม่เพี้ยนบน Windows ที่ตั้งภาษาอื่น
- ทั้งสอง spec ตัดไฟล์ที่ไม่ใช้ออกเหมือนกัน (`_DROP`) และรวม hiddenimports ของหน้าต่างแอป (WebView2) ไว้เหมือนกัน — **แก้ spec หนึ่งต้องแก้อีกอัน**
- รันจากซอร์ส: `run_web.bat` (ส่งอาร์กิวเมนต์ต่อให้ `app.py`)

## build บน Linux / macOS

```bash
python -m pip install -r requirements.txt -r requirements-build.txt
pyinstaller OpenThai2OCR.spec --noconfirm --clean
# ผลลัพธ์: dist/OpenThai2OCR.exe  (บน Unix เป็นไบนารีธรรมดา เปลี่ยนชื่อได้)
chmod +x dist/OpenThai2OCR.exe
```

> PyInstaller ไม่ cross-compile — ต้อง build บน OS นั้น ๆ เอง (CI ใน
> `.github/workflows/release.yml` ทำให้อัตโนมัติเมื่อ push tag)

## release ทุก OS (GitHub Actions)

1. ตั้ง version ใน `CHANGELOG.md` + commit
2. push tag

```bash
git tag v1.0.0
git push origin v1.0.0
```

3. workflow `release` ทำต่อไปนี้ในแต่ละ OS: `pytest` → ตรวจโมเดล → build → **smoke test ไบนารีที่ build แล้ว**
   (`tools/exe_smoke.py`) → (Windows: เซ็นถ้ามี secret) → แนบไฟล์ลง Release
   - ถ้าขั้นไหนล้ม job หยุด และ `publish` ไม่รัน (พิสูจน์แล้วด้วย branch ทดลองที่มีเทสต์ล้ม)
   - `publish` รันเฉพาะเมื่อ push tag (`workflow_dispatch` บน branch ใช้ทดสอบ build ได้โดยไม่ออก release)

   ไฟล์ที่แนบ:

   - `OpenThai2OCR-windows-x64.exe`
   - `OpenThai2OCR-linux-x64`
   - `OpenThai2OCR-macos-arm64` (หรือ x64 ตาม runner)

ถ้าต้องการ build/release เองโดยไม่รอ CI:

```bash
gh release create v1.0.0 --notes-file notes.md dist/OpenThai2OCR.exe
python tools/release-notes-patch.py v1.0.0 notes.md --repo <owner>/<repo>
gh release upload v1.0.0 dist/OpenThai2OCR-linux-x64 --clobber
```

## เซ็นชื่อ exe (code signing)

ถ้ามีใบรับรอง code signing จะลดคำเตือน "Windows protected your PC" ได้
(ปัจจุบัน **ยังไม่ได้เซ็น** — ผู้ใช้ดูวิธีเปิดได้ใน README หัวข้อ "ถ้า Windows / macOS เตือนตอนเปิดครั้งแรก")

> ข้อควรรู้ (ตรวจเมื่อ 2026-11): CA สาธารณะออกใบรับรองใหม่โดยเก็บกุญแจในฮาร์ดแวร์ (โทเค็น/HSM) อายุสูงสุด 459 วัน
> จึงมักไม่ได้ไฟล์ .pfx ให้ใส่ GitHub secret · ทางที่เหมาะกับโปรเจกต์โอเพนซอร์สนี้คือ SignPath Foundation (ฟรี)
> ส่วน Azure Artifact Signing ยังไม่รองรับผู้พัฒนาในไทย — ถ้าจะใช้ SignPath ต้องปรับขั้นเซ็นใน `release.yml`

สคริปต์ `tools/sign_exe.ps1` หา `signtool.exe` ให้เอง (จาก PATH หรือ Windows Kits)

```powershell
# 1) ใบรับรองแบบไฟล์ .pfx
$env:SIGN_PFX = "C:\certs\codesign.pfx"; $env:SIGN_PFX_PASSWORD = "รหัส"
powershell -ExecutionPolicy Bypass -File tools\sign_exe.ps1 -Path dist\OpenThai2OCR.exe

# 2) ใบรับรองที่ติดตั้งใน Windows store (ระบุ thumbprint)
$env:SIGN_THUMBPRINT = "A1B2C3..."
powershell -ExecutionPolicy Bypass -File tools\sign_exe.ps1
```

- ต้องเซ็น **ก่อน** เปลี่ยนชื่อไฟล์/อัปโหลด (CI เซ็นให้ก่อนขั้น Rename)
- ตัวเลือกเสริม: `-TimestampUrl` (ค่าเริ่มต้น `http://timestamp.digicert.com`)
- สคริปต์จะ `signtool verify /pa` ให้ด้วย — ถ้าไม่ผ่านจะหยุดทันที

ใน CI ใส่ secret `WINDOWS_PFX_BASE64` (base64 ของ .pfx) +
`WINDOWS_PFX_PASSWORD` แล้ว workflow `release` จะเซ็น exe บน Windows ให้อัตโนมัติ
(ถ้าไม่ตั้ง secret ขั้นนี้จะถูกข้าม ไม่ทำให้ build ล้ม)

## ทดสอบก่อน build

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q          # ทดสอบ API/ส่งออก/ฯลฯ (39 เคส)
python tools/smoke_test.py   # ทดสอบอ่านภาพจริงจากซอร์ส
python tools/exe_smoke.py dist/OpenThai2OCR.exe   # ทดสอบ exe/ไบนารีที่ build แล้ว (--port, --timeout)
```

## โมเดลและ asset

ไฟล์โมเดลอยู่ใน `models/` (det.onnx, rec.onnx, rec_dict.txt, config.json)
และสเปก onefile ฝังไฟล์เหล่านี้เข้า exe อัตโนมัติ

โฟลเดอร์ `assets/` มีฟอนต์ `NotoSansThai-Regular.ttf` (OFL) สำหรับ PDF ที่ค้นหาได้
— สเปกฝังให้เช่นกัน

ดาวน์โหลด/อัปเดตโมเดลใหม่จาก Hugging Face:

```bash
python tools/download_models.py
```

## โครงสร้างไฟล์ build

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `OpenThai2OCR.spec` | onefile (ฝังโมเดล) — ใช้ใน CI |
| `OpenThai2OCR_onedir.spec` | onedir |
| `app.ico` | ไอคอน exe |
| `build_exe.bat` | build onefile บน Windows (เทสต์ → build → smoke test exe) |
| `build_exe_onedir.bat` | build onedir บน Windows (เทสต์ → build → คัดลอกโมเดล → smoke test exe) |
| `run_web.bat` | รันจากซอร์สบน Windows (ตรวจ Python/dependency ให้) |
| `tools/exe_smoke.py` | smoke test ไบนารีที่ build แล้ว (ใช้ทั้งใน `.bat` และ CI) |