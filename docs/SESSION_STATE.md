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

## Session 4 (v1.2.0 — build exe + tag + ปล่อย release) — 2026-11-16

## Objective
ปิดงาน v1.2.0: build exe → ทดสอบ → tag `v1.2.0` → ปล่อย release → patch ตาราง SHA256

## Completed
- **build exe** `PyInstaller OpenThai2.0OCR.spec --clean` สำเร็จ (onefile, ฝังโมเดล) ~52 วิ
- **ทดสอบ exe จริง** — ปลุก `dist\OpenThai2OCR.exe --no-browser --port 5199` → `/api/health`
  (version 1.2.0, model_ready true) → อัปโหลดภาพไทย → OCR ได้ข้อความ → export
  docx/txt/json/csv ครบ (docx ขึ้นต้น `PK`) · pytest 9/9 ผ่าน
- **เจอ + แก้บั๊ก workflow** — `if: ... && secrets.WINDOWS_PFX_BASE64 != ''` ที่ระดับ step
  ทำให้ workflow parse ไม่ผ่าน (secrets ใช้ใน `if` ไม่ได้) → ย้ายไป `env` ระดับ job
  แล้วเช็ค `env.PFX_BASE64 != ''` (commit `0bc254d`)
- **tag + release** — ลบ tag เดิมที่ชี้ commit เสีย, สร้าง tag ใหม่บน `0bc254d`, push
  → CI release (win/linux/mac) + ci ผ่านทั้งหมด, GitHub Release `v1.2.0` มี 3 asset
- **release notes** — `docs/release-notes-v1.2.0.md` + เติม SHA256 จริงทั้ง 3 asset →
  `release-notes-patch.py` PATCH ผ่านภาษาไทย (ตรวจ `.checked` แล้ว)

## ข้อควรระวังที่เจอ
- `secrets.*` ใช้ใน `if` ของ step ไม่ได้ → ใช้ `env` ระดับ job แทน
- exe ที่รันค้างทำให้ตัวใหม่เจอ "already running" แล้วเปิดเบราว์เซอร์เดิมแทนที่จะฟังพอร์ตใหม่
  → ก่อนทดสอบต้อง `taskkill /T /F` ให้หมด
- ภาพทดสอบที่ตัวอักษรถูกตัดขอบ (วาดล้น canvas) จะถูกทิ้งเป็น `invalid_thai` → ข้อความว่าง
- `tools/release-notes-patch.py` เติม digest ของ `assets[0]` (บน GitHub เรียงตามชื่อ = linux)
  → เขียนตาราง SHA เองก่อน แล้วปล่อยให้สคริปต์ PATCH body (regex เติมเฉพาะบรรทัด `SHA256:`)

## Active
- ไม่มี — v1.2.0 ปล่อยแล้ว

## Blocked
- code signing ยังไม่มีใบรับรองจริง (โครงพร้อม — ใส่ secret `WINDOWS_PFX_BASE64` +
  `WINDOWS_PFX_PASSWORD` แล้วปล่อยรุ่นถัดไป)
- อ่านภาพโดยตรงไม่ได้ (ต้องตรวจผ่านโค้ด/CLI/เบราว์เซอร์)

## Next Move
- ตั้ง secret เซ็นชื่อ (ถ้ามีใบรับรอง) แล้วปล่อย v1.2.1/1.3.0 เพื่อทดสอบขั้นเซ็นจริง
- งานถัดไปที่ยังไม่มี: ทดสอบ watch folder กับไฟล์จริงในโฟลเดอร์ผู้ใช้, ปรับปรุงเอกสารตามฟีดแบ็ก

## commit ล่าสุด
- `0bc254d` (ci: fix secrets context in release signing step)
- `b9ad450` (docs: add v1.2.0 release notes)
- version: 1.2.0 — tag `v1.2.0` ปล่อยแล้ว (release id 446700332)
## Session 5 (v1.3.0 — หัวข้อ: หน้า API guide / playground / status + ไม่เปิดเบราว์เซอร์) — 2026-11-16

## Objective
เพิ่มหน้าใหม่ในเว็บ (สอนใช้ API, ทดสอบ API, สถานะ) และทำตัวเลือก "รัน UI โดยไม่เปิดเบราว์เซอร์" ให้จำค่าได้

## Completed
- **หน้า `/docs`** (`templates/docs.html`) — คู่มือเชื่อมต่อ API: endpoint ทั้งหมด, ตัวอย่าง
  curl/Python/JavaScript/PHP/C#, รูปแบบคำตอบ, `settings` ที่ใช้บ่อย, jobs, errors, watch folder,
  ปุ่มคัดลอกโค้ด, สลับไทย/อังกฤษ (data-th/data-en + localStorage `ocrLang` ร่วมกับหน้าแรก)
- **หน้า `/playground`** (`templates/playground.html`) — ยิง `/api/ocr` จริงจากเบราว์เซอร์:
  drag-drop ไฟล์, scale, settings JSON (ตรวจ JSON ก่อนส่ง), `images=0`, แสดงข้อความ/JSON/สรุป
  (HTTP, เวลา, timing, confidence), คัดลอก curl, ลิงก์ดาวน์โหลด export, กรอก API key ถ้าเปิด LAN
- **หน้า `/status`** (`templates/status.html`) — version/uptime/โมเดล/โหมด key/limits/watch folder
  + ตารางงานล่าสุด 20 งาน จาก `GET /api/status` (รีเฟรชเองทุก 3 วินาที)
- **ไม่เปิดเบราว์เซอร์อัตโนมัติ (จำค่า)** — `settings.json` ข้าง exe (fallback
  `%LOCALAPPDATA%\OpenThai2OCR\settings.json`), `--no-browser` / `--browser` (CLI ชนะค่าที่จำ),
  checkbox ในหน้าแรก → `POST /api/prefs`; `/api/prefs` + `/api/status` ใหม่, `/api/health` เพิ่ม `uptime_s`
- เมนูนำทาง 4 หน้า (OCR / สอนใช้ API / ทดสอบ API / สถานะ) + อัปเดตปุ่ม lang ให้ทั้ง 4 หน้า
- เอกสาร: README (หน้าใหม่ + --browser), USAGE/API ไทย-อังกฤษ, CHANGELOG v1.3.0
- tests เพิ่ม 3 เคส (12 ผ่านทั้งหมด) · ตรวจด้วยเบราว์เซอร์จริงทุกหน้า + playground ยิง OCR สำเร็จ
  + prefs บันทึก/อ่านข้าม restart (ไม่เปิดเบราว์เซอร์ตามค่า)

## ข้อควรระวังที่เจอ
- Flask cache template ตอนไม่ debug → แก้ template ต้องรีสตาร์ตเซิร์ฟเวอร์ก่อนทดสอบ (เจอซ้ำ)
- `.hidden` ต้องประกาศใน CSS ของแต่ละหน้า (docs.html ลืมรอบแรก → ทุกแท็บโค้ดโผล่พร้อมกัน)
- `os.access(BASE, W_OK)` ใช้ตัดสิน fallback ได้ไม่แน่เสมอ → `save_prefs` เพิ่ม try/except
  เขียน BASE ก่อน แล้ว fallback LOCALAPPDATA
- CSS `.card .v` specificity ชนะ `.ok` → ต้องเขียน `.card .v.ok` ถึงจะได้สีเขียว/แดง

## Active
- ไม่มี — โค้ด v1.3.0 พร้อม (ยังไม่ build exe/tag)

## Blocked
- เช่นเดิม: code signing ยังไม่มีใบรับรอง · อ่านภาพโดยตรงไม่ได้ (ตรวจผ่านเบราว์เซอร์เท่านั้น)

## Next Move
- build exe v1.3.0 + ทดสอบ (`--no-browser` + prefs) → tag `v1.3.0` → release notes + patch SHA
- ถ้าจะเซ็นจริง: ใส่ secret `WINDOWS_PFX_BASE64` + `WINDOWS_PFX_PASSWORD` ก่อน push tag

## commit ล่าสุด
- `a6d2696` (docs: fill v1.2.0 SHA256 table and session state)
- version: 1.3.0 (ในโค้ด) — ยังไม่ tag/release
