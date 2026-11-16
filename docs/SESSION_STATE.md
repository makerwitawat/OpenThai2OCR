# SESSION_STATE — OpenThai2.0 OCR Web UI

## Session 1 (งานหลัก: Web UI + API + exe + Release) — 2026-11-16

## Objective
ทำหน้าเว็บ UI สำหรับใช้ OCR (OpenThai2.0-OCR-Text บน CPU) → build exe → ใส่ icon →
API รองรับเครื่องอื่น (PHP ฯลฯ) → ธีมขาว/paste/ฟอนต์ตามจอ → คู่มือ → GitHub public + release ทุก OS

## ข้อสำคัญ
- โมเดล: `iapp/OpenThai2.0-OCR-Text` (CPU เท่านั้น) — อยู่ใน `models/`, ฝังเข้า onefile exe
- Runtime: `LineOCR` (models/runtime/line_engine.py) — import เป็น package `models.runtime`
- Backend OCR ใช้ ONNX Runtime (backend ใน config เป็น openvino → fallback เป็น onnxruntime อัตโนมัติ ถ้าไม่มี openvino)
- ตัวอ่านภาพไม่ได้ → ตรวจผ่านโค้ด/CLI เท่านั้น (โมเดล AI นี้ไม่รองรับ image input)
- exe 2.5GB ตอนแรก = PyInstaller ดึง torch/CUDA ตามไม่เจอ → ใส่ excludes แล้ว เหลือ 115.9MB
- เครื่องนี้: Python 3.12, CPU i9-14900HX, GPU RTX5060 (โมเดลใช้ CPU ไม่ได้ใช้ GPU)

## Completed (+commit)
- Flask app + UI ไทย (paste, หลายไฟล์, tabs, คัดลอก/ดาวน์โหลด) — commit `b9a0437`
- API: multipart + JSON base64 + `scale`/`settings` + CORS + health — `b9a0437`, `94990d9`
- ธีมขาว + ฟอนต์ A−/A/A+ (localStorage) + ความละเอียด auto/1×/1.5×/2×
- icon `app.ico` ฝังใน exe (ยืนยันแล้ว ExtractAssociatedIcon=True)
- build: `build_exe.bat` (onefile) + `build_exe_onedir.bat` + 2 spec — ทดสอบผ่าน (GET 200, OCR ok, scale=2)
- เอกสาร: README / docs/USAGE / docs/API / docs/BUILD / CHANGELOG / LICENSE / NOTICE
- CI: `.github/workflows/ci.yml` (smoke test 3 OS) + `release.yml` (build 3 OS → attach release)
  - CI ผ่านทั้งหมด (Windows/Linux/macOS) ทั้ง 2 รอบ
- GitHub public `makerwitawat/OpenThai2OCR` (master) — push 2 commits
- Release `v1.0.0` ครบ 3 ไฟล์ + release notes ไทย + ตาราง SHA256
  - windows-x64.exe `9b96917d…a2ad9`
  - linux-x64 `80ff2972…4ebbc`
  - macos-arm64 `3b11b1a4…684e7e`
- tools/release-notes-patch.py (DEFAULT_REPO=makerwitawat/OpenThai2OCR) + download_models.py + smoke_test.py
- เอกสาร 2 ภาษา: README/README.en, docs/USAGE(.en), docs/API(.en), docs/BUILD(.en)
  + API ตัวอย่าง 8 ภาษา (PHP, Python, Node.js, C#, Java, Go, Ruby, PowerShell) ทั้งไทย/อังกฤษ

## Active
- ไม่มี (งานรอบนี้จบเรียบร้อย) — exe ล่าสุด `dist/OpenThai2OCR.exe` 115.9MB พร้อมใช้

## Blocked
- ผมอ่านภาพโดยตรงไม่ได้ ต้องใช้คน/เครื่องมืออื่นถ้าต้อง "ดูภาพ"

## Next Move (ถ้ามีรอบต่อไป)
- ถ้าผู้ใช้ส่งภาพตัวอย่างที่อ่านผิด → ปรับ config (det.limit 1600+, det.v_pad 0.1-0.2) แล้วเทียบผล
- เพิ่ม line-level copy / export PDF ที่ค้นหาได้ / watch folder / API key+TLS ถ้าจะเปิดนอก LAN
- release ครั้งถัดไป: แก้ CHANGELOG → commit → `git tag v«x» && git push origin v«x»` → รอ CI → patch SHA ตาม file จริง

## คำสั่งยืนยัน
- เริ่มรีลีสใหม่: `gh release create v0.0.x --title "..." --notes "Release ..." dist/OpenThai2OCR.exe` แล้ว `python tools/release-notes-patch.py v0.0.x .tmp/release-notes.md` (ภาษาไทยผ่าน API PATCH ตรง)
- รัน dev: `python app.py` (หรือ `run_web.bat`) · build exe: `build_exe.bat`
- ทดสอบ: `python tools/smoke_test.py`

## Session 2 (v1.1.0 — ปิดช่องโหว่ + UI 2 ภาษา) — 2026-11-16

## Objective
ปิดช่องโหว่ที่ขาด (limits/log/instance/quit/auth/progress) + export (PDF ค้นหาได้/CSV/JSON) + UI 2 ภาษา

## Completed (+commit)
- logging หมุนเวียน `logs/openthai-ocr.log` + แสดง path/version ใน health
- จำกัด 100 MB และ PDF 50 หน้า + error 413/400 ชัดเจน
- single-instance (เปิดซ้ำ → เปิดเบราว์เซอร์เดิม) + เลื่อนพอร์ต 5000–5010
- ปุ่มปิดโปรแกรม + `POST /api/shutdown` (เฉพาะเครื่องตัวเอง)
- API key (`--api-key` / สุ่มอัตโนมัติในโหมด LAN) + UI ถาม key ครั้งแรก
- `POST /api/jobs`, `GET /api/jobs/<id>`, cancel → progress bar + ยกเลิกใน UI
- export: PDF ค้นหาได้ (TextWriter + Noto Sans Thai OFL), CSV (UTF-8 BOM), JSON, TXT
- UI: สลับ ไทย/EN (localStorage), lightbox, rerun อัตโนมัติเมื่อเปลี่ยน scale, favicon, version, ปุ่ม export
- tests: `tests/test_api.py` 7 เคส (ผ่าน) + CI รัน pytest ทุก OS
- เอกสาร 2 ภาษา + CHANGELOG v1.1.0 อัปเดตครบ

## ข้อควรระวังที่เจอ
- PDF text layer: ต้องใช้ `pymupdf.TextWriter` (insert_text + fontfile ให้ข้อความสกัดได้เป็น \x00)
- PyInstaller onefile: ต้อง exclude torch/CUDA (ถ้าไม่ exclude exe ใหญ่ 2.5GB)
- อย่าลืม `taskkill /IM OpenThai2OCR.exe /F` ก่อน build (ไฟล์ exe ถูกล็อก)

## Active
- ไม่มี — exe v1.1.0 `dist/OpenThai2OCR.exe` (116.3 MB) ทดสอบแล้วครบ (jobs/export/shutdown)

## Blocked
- อ่านภาพโดยตรงไม่ได้ (ต้องตรวจผ่านโค้ด/CLI)

## Next Move
- release v1.1.0 (tag) → รอ CI → patch SHA table
- ถ้าต้องการต่อ: line-level copy, watch folder, DOCX export, code signing

## commit ล่าสุด
- `f023ea4` (feat(v1.1.0): limits, logging, single-instance, API key, jobs/progress, exports, bilingual UI)
- version: v1.1.0 — release ครบ 3 OS (windows/linux/macos) + SHA ใน notes แล้ว

## Session 3 (v1.2.0 — คัดลอกบรรทัด + DOCX + watch folder + code signing) — 2026-11-16

## Objective
ทำครบ 4 ข้อที่ค้างจาก Next Move ของ Session 2 (line-level copy, watch folder, DOCX export, code signing)

## Completed (+commit `3ad9b00`)
- **คัดลอกทีละบรรทัด** — ปุ่ม "รายบรรทัด" (Lines) กางทุกบรรทัดของหน้าปัจจุบัน + %ความมั่นใจ,
  คัดลอกทีละบรรทัด หรือ "คัดลอกทุกบรรทัด" · ใช้ `pages[i].lines` ที่มีอยู่ (หน้าบ้านล้วน)
- **DOCX export** — `_export_docx` สร้าง OOXML เอง (zip + document/styles/[Content_Types]) ไม่เพิ่ม dependency,
  บรรทัดละย่อหน้า, ฟอนต์ Leelawadee UI, รองรับหลายหน้า (หัวข้อ "หน้า N") + `format=docx` + ปุ่ม `.docx`
- **watch folder** — `--watch DIR` / `--watch-out DIR` / `--watch-interval SEC`,
  thread เฝ้าโฟลเดอร์ เขียน `<stem>-ocr.txt/.docx/.json`, ต้นฉบับไม่ถูกย้าย,
  อ่านซ้ำเฉพาะเมื่อ size/mtime เปลี่ยน, ข้ามไฟล์ที่ยังเขียนไม่เสร็จ (อายุ < interval/2),
  ล้าง state ไฟล์ที่ถูกลบ, error ไม่วน retry; `/api/health` มี `watch`
- **code signing** — `tools/sign_exe.ps1` (หา signtool จาก PATH/Windows Kits, รองรับ
  .pfx หรือ thumbprint, timestamp + verify /pa) + step ใน `release.yml` เปิดเมื่อมี
  secret `WINDOWS_PFX_BASE64` (+`WINDOWS_PFX_PASSWORD`) — ไม่ตั้งก็ข้าม ไม่ทำให้ build ล้ม
- **แก้บั๊กเดิม** — สลับภาษาแล้วสถานะ/ชื่อไฟล์ใน placeholder หาย (applyLang เขียนทับ textContent)
- tests 9 เคสผ่าน (`test_docx_export`, `test_watch_folder`) · ตรวจ UI จริงด้วยเบราว์เซอร์ (อัปโหลด →
  รายบรรทัด → คัดลอก → สลับภาษา → docx 200/PK) · ทดสอบ watch จริงบนพอร์ต 5100

## ข้อควรระวังที่เจอ
- Flask cache template ตอนรันแบบไม่ debug → แก้ `templates/index.html` ต้องรีสตาร์ตเซิร์ฟเวอร์ก่อนทดสอบ
- ไฟล์ที่ watch ต้อง "นิ่ง" ก่อน (mtime เก่ากว่า interval/2) ไม่งั้นถูกข้ามในรอบแรก
- DOCX ต้อง escape XML (&, <, >, ") ไม่งั้นไฟล์เสีย

## Active
- ไม่มี — โค้ด v1.2.0 พร้อม release แต่ยังไม่ build exe/tag

## Blocked
- code signing ยังไม่มีใบรับรองจริง → ทดสอบได้แค่ตัวสคริปต์/ขั้น CI (ยังไม่เซ็นจริง)
- อ่านภาพโดยตรงไม่ได้ (ต้องตรวจผ่านโค้ด/CLI/เบราว์เซอร์)

## Next Move
- build exe v1.2.0 (`build_exe.bat`) → ทดสอบ → tag `v1.2.0` → รอ CI → patch SHA table
- ถ้าจะเซ็นจริง: ใส่ secret `WINDOWS_PFX_BASE64` + `WINDOWS_PFX_PASSWORD` ก่อน push tag

## commit ล่าสุด
- `3ad9b00` (feat(v1.2.0): line-level copy, DOCX export, watch folder, code signing)
- version: 1.2.0 (ในโค้ด) — ยังไม่ tag/release