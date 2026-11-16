# Build & Release — OpenThai2.0 OCR

**ไทย** | [English](BUILD.en.md)

## build ในเครื่อง (Windows)

```bat
build_exe.bat          :: ไฟล์เดียว  dist\OpenThai2OCR.exe  (ฝังโมเดลในตัว)
build_exe_onedir.bat   :: ทั้งโฟลเดอร์ dist\OpenThai2OCR\    (เปิดเร็วกว่า)
```

- **onefile** = แจกง่ายสุด แต่ทุกครั้งที่เปิดจะแตกไฟล์ไป temp (ช้าครั้งแรก ~2–8 วินาที)
- **onedir** = เปิดเร็ว แต่ต้องแจกทั้งโฟลเดอร์ (มี `_internal\` + `models\`)

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

3. workflow `release` จะ build 3 ระบบและแนบไฟล์ลง Release:
   - `OpenThai2OCR-windows-x64.exe`
   - `OpenThai2OCR-linux-x64`
   - `OpenThai2OCR-macos-arm64` (หรือ x64 ตาม runner)

ถ้าต้องการ build/release เองโดยไม่รอ CI:

```bash
gh release create v1.0.0 --notes-file notes.md dist/OpenThai2OCR.exe
python tools/release-notes-patch.py v1.0.0 notes.md --repo <owner>/<repo>
gh release upload v1.0.0 dist/OpenThai2OCR-linux-x64 --clobber
```

## ทดสอบก่อน build

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q          # ทดสอบ API 7 เคส
python tools/smoke_test.py   # ทดสอบอ่านภาพจริง
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
| `build_exe.bat` | build onefile บน Windows |
| `build_exe_onedir.bat` | build onedir บน Windows |