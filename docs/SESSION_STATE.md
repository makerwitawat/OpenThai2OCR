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

## Session 6 (v1.3.0 — โหมดหน้าต่างโปรแกรม + สเกลฟอนต์ทุกหน้า + แก้ทำไมยังเปิดเบราว์เซอร์) — 2026-11-16

## Objective
ตอบปัญหา "รันแล้วยังเปิดเบราว์เซอร์" และเพิ่มโหมด GUI (หน้าต่างโปรแกรม) + ปุ่ม A− A A+ ให้ครบทุกหน้า

## สาเหตุที่ยังเปิดเบราว์เซอร์ (ตอบ user)
- exe ที่ build ไว้ (v1.3.0) ยังเปิดเบราว์เซอร์เพราะ **ไม่พบ settings.json ข้าง exe**
  (`dist\settings.json`) → ใช้ค่าเริ่มต้น = เปิดเบราว์เซอร์; ค่าที่เคยตั้งอยู่ใน `settings.json`
  ของโฟลเดอร์โปรเจกต์ไม่ถูกอ่านเมื่อรัน exe (BASE = โฟลเดอร์ exe)
- แก้: `save_prefs` เขียนทั้ง `settings.json` ข้าง exe และ `%LOCALAPPDATA%\OpenThai2OCR\settings.json`
  และอ่านจากทั้งสองที่ → ตั้งครั้งเดียวใช้ได้ทุกตำแหน่งของ exe

## Completed
- **โหมด `--window` (GUI)** — pywebview + WebView2 เปิดหน้าต่างโปรแกรมจริง (ไม่ต้องมีเบราว์เซอร์)
  · เซิร์ฟเวอร์ waitress รันเป็น thread, ปิดหน้าต่างแล้วจบโปรเซส (`os._exit`)
  · ถ้ารันซ้ำตอนโปรแกรมทำงานอยู่ → เปิดหน้าต่างชี้ตัวที่รันอยู่
  · ถ้าไม่มี pywebview → fallback เปิดเบราว์เซอร์ + log
- **ตั้งค่า "เมื่อเริ่มโปรแกรม"** 3 โหมดในหน้าแรก (หน้าต่างโปรแกรม / เบราว์เซอร์ / ไม่เปิดอะไร)
  → `POST /api/prefs {"start_mode": ...}` · CLI `--window` / `--browser` / `--no-browser` ชนะค่าที่จำ
  · `/api/prefs` และ `/api/status` รายงาน `start_mode` · หน้า `/status` แสดงโหมด
- **A− / A / A+ ทุกหน้า** (docs/playground/status) — ใช้ `html{font-size: calc(var(--scale)*clamp(...))}`
  + localStorage `ocrFontScale` ค่าเดียวกับหน้าแรก
- requirements เพิ่ม `pywebview>=5.0` · spec เพิ่ม hiddenimports (webview, edgechromium, winforms, clr, clr_loader)
- tests: เพิ่มเคส start_mode (13 ผ่าน) · build exe ใหม่ทดสอบจริง:
  `--window` เปิดหน้าต่าง title "OpenThai2.0 OCR" + /api/health ตอบ · ค่าที่จำไว้ (window) เปิดหน้าต่างให้เอง
  เมื่อรันเปล่า ๆ · `--no-browser` ไม่มีหน้าต่าง (start_mode=none)

## ข้อควรระวังที่เจอ
- build เขียน `dist\OpenThai2OCR.exe` ไม่ได้ถ้า exe ตัวเก่ายังรันอยู่ (PermissionError) → build ลง
  `--distpath dist_next` แล้วค่อยสลับไฟล์หลังปิดโปรแกรม
- มี instance เก่าค้างพอร์ต 5000 ทำให้ exe ใหม่เปิดหน้าต่างไปหาตัวเก่า (API เก่า) → ตอนทดสอบใช้ `--port` แยก
- `dist_next/` เพิ่มใน .gitignore

## Active
- ไม่มี — แทน `dist\OpenThai2OCR.exe` ด้วย build ใหม่แล้ว (ปิด instance เก่า PID 7720/15892)
  · ทดสอบ exe ใน dist: version 1.3.0, `/docs` `/playground` `/status` = 200, `/api/prefs` อ่านค่าได้
  · `%LOCALAPPDATA%\OpenThai2OCR\settings.json` = `start_mode: "window"` → ดับเบิลคลิกเปิดหน้าต่างโปรแกรม

## Blocked
- code signing ยังไม่มีใบรับรอง · อ่านภาพโดยตรงไม่ได้

## Next Move
- แทนไฟล์ exe ใน dist (หลังปิดตัวเก่า) → ทดสอบซ้ำ → tag `v1.3.0` → release notes + patch SHA
- ถ้าจะเซ็นจริง: ใส่ secret `WINDOWS_PFX_BASE64` + `WINDOWS_PFX_PASSWORD`

## commit ล่าสุด
- `ee81d18` (feat(v1.3.0): API guide, playground and status pages; remembered no-browser start)
- version: 1.3.0 — ยังไม่ tag/release

## Session 7 (v1.3.0 — ปล่อย release) — 2026-11-16

## Objective
build/tag/ปล่อย v1.3.0 พร้อม release notes + SHA256 (ต่อจาก Session 6)

## Completed
- spec: ทำ hiddenimports ของ webview/clr เป็น Windows-only (`sys.platform == "win32"`)
  กัน build Linux/macOS พัง (commit `d421d1c`)
- **เจอบั๊ก CI**: `requirements.txt` ไม่มีขึ้นบรรทัดใหม่ท้ายไฟล์ → append ต่อกันเป็น
  `onnxruntime>=1.17pywebview>=5.0` → pip ของ CI พังทุก OS → แก้ + retag (commit `4aa1696`)
- ลบ tag เดิมที่ชี้ commit เสีย → tag `v1.3.0` ใหม่บน `4aa1696` → CI `release` + `ci` ผ่าน
- GitHub Release `v1.3.0` (id 446884747) มี 3 asset · PATCH notes ผ่าน `release-notes-patch.py`
  ภาษาไทยปกติ (ตรวจ `.checked`)
- ทดสอบ exe ที่ดาวน์โหลดจาก release จริง: `--window` ขึ้นหน้าต่าง "OpenThai2.0 OCR",
  `/api/health` ตอบ, ปิดผ่านปุ่มในหน้าเว็บได้ (log: shutdown requested via UI)
- เอา asset Windows จาก release มาแทน `dist\OpenThai2OCR.exe` — SHA256 ตรงกับที่ปล่อย
  (`aa60fd4c…0f5d`, 151 MB รวม WebView2/pythonnet)

## ข้อควรระวังที่เจอ
- `Add-Content` ต่อท้ายไฟล์ที่ไม่มี newline ปิดท้าย → ข้อความติดกัน (เจอใน requirements.txt)
- `gh release view --jq '...'` ใน PowerShell 5.1 มีปัญหาระบุ argument → ใช้ `--template` ไม่ได้
  ต้อง `--json ... -q` แบบไม่มี double quote ใน jq
- asset บน GitHub เรียงตามชื่อ (linux แรก) → digest ของ `assets[0]` ไม่ใช่ Windows (เขียนตารางเอง)

## Active
- ไม่มี — v1.3.0 ปล่อยแล้ว

## Blocked
- code signing ยังไม่มีใบรับรอง (โครงพร้อม) · Linux/macOS โหมดหน้าต่างต้องมี GTK/WebKit
  (ถ้าไม่มีจะ fallback เปิดเบราว์เซอร์)

## Next Move
- เก็บฟีดแบ็กจากผู้ใช้หน้า `/docs` `/playground` `/status` / โหมดหน้าต่าง
- ถ้าจะเซ็นจริง: ใส่ secret `WINDOWS_PFX_BASE64` + `WINDOWS_PFX_PASSWORD` ก่อน push tag ถัดไป

## commit ล่าสุด
- `4aa1696` (fix: newline before pywebview in requirements.txt) — tag `v1.3.0` อยู่ที่ commit นี้
- version: 1.3.0 — release แล้ว (release id 446884747)

## Session 8 (v1.3.1 — แก้ปุ่มดาวน์โหลดในโหมดหน้าต่าง + กล่องยืนยัน/toast สวย ๆ) — 2026-11-16

## Objective
แก้ "กดปุ่ม .txt/.docx/.pdf/.csv/.json แล้วไม่เห็นอะไร" และทำ alert/ยืนยันให้สวยงาม

## สาเหตุ
- pywebview/WebView2 ตั้ง `ALLOW_DOWNLOADS = False` โดยค่าเริ่มต้น → ทุกดาวน์โหลดถูก `args.Cancel = True`
  เงียบ ๆ (เบราว์เซอร์ปกติไม่เป็น) → ในโหมดหน้าต่างปุ่มส่งออกเลยเหมือนไม่ทำงาน

## Completed
- `_open_window`: เปิด `webview.settings["ALLOW_DOWNLOADS"] = True` → ดาวน์โหลดได้
  (มีหน้าต่าง Save file ของ Windows ให้เลือกที่เก็บ) · ทดสอบจริงด้วยสคริปต์ pywebview
  แทน handler ให้บันทึกอัตโนมัติ → ไฟล์ออกมาครบเนื้อหา
- **กล่องยืนยัน/กรอกข้อความแบบใหม่** แทน `window.confirm` / `window.prompt` —
  ไอคอน, หัวข้อ, ปุ่ม primary/danger, Enter/Esc, คลิกฉากหลังเพื่อปิด · ใช้กับ
  ปุ่มปิดโปรแกรม + ช่อง API key
- **toast แจ้งเตือนมุมล่างขวา** — คัดลอกแล้ว/กำลังดาวน์โหลด/ข้อผิดพลาด
- ปุ่มก่อนมีผลลัพธ์ → toast "ยังไม่มีผลลัพธ์ — อ่านไฟล์ก่อน" (เดิมเงียบ)
- เปลี่ยนข้อความ toast เป็น "ดาวน์โหลด {name}" (เพราะในโหมดหน้าต่างผู้ใช้ต้องเลือกที่เก็บเอง)
- bump version 1.3.1 · CHANGELOG + USAGE ไทย/อังกฤษ (troubleshooting) · pytest 13/13

## ข้อควรระวังที่เจอ
- pywebview: `webview.settings` เป็น ImmutableDict แต่แก้ค่า key เดิมได้ (`settings["X"] = ...`)
- monkeypatch `WinForms.SaveFileDialog` ไม่ได้ (pythonnet) → ใช้วิธีแทน
  `EdgeChrome.on_download_starting` ในสคริปต์ทดสอบ
- ปุ่มใน WebView2 ต้องโฟกัสหน้าต่างก่อน (clipboard/download dialog)

## Active
- v1.3.1 พร้อมในซอร์ส (`dist` ยังเป็น exe 1.3.0 — ต้อง build ใหม่ก่อนปล่อย)

## Blocked
- code signing ยังไม่มีใบรับรอง · อ่านภาพโดยตรงไม่ได้

## Next Move
- build exe 1.3.1 → ทดสอบในโหมดหน้าต่าง (กดดาวน์โหลด/คัดลอก) → tag `v1.3.1` → release notes + SHA

## commit ล่าสุด
- `e720dbc` (docs: fill v1.3.0 SHA256 table and session state)
- version: 1.3.1 (ในโค้ด) — ยังไม่ tag/release

## Session 9 (v1.3.1 — ปล่อย release) — 2026-11-16

## Objective
ปล่อย v1.3.1 (แก้ดาวน์โหลดในโหมดหน้าต่าง + กล่องยืนยัน/toast ใหม่) ต่อจาก Session 8

## Completed
- tag `v1.3.1` บน commit `91e3f14` → CI `release` + `ci` ผ่านทั้งหมด
  · GitHub Release `v1.3.1` (id 446981212) มี 3 asset
- เติม SHA256 จริงใน notes → `release-notes-patch.py` PATCH ผ่าน ภาษาไทยปกติ (ตรวจ `.checked`)
- ดาวน์โหลด asset Windows จาก release → ตรวจ SHA ตรง → แทน `dist\OpenThai2OCR.exe`
  (`d1bc3cd5…6070`, 151 MB) · ทดสอบเร็ว ๆ: `/api/health` = 1.3.1
- `dist` กับ release ตรงกันแล้ว (SHA เดียวกัน)

## ข้อควรระวัง
- build ในเครื่องได้ exe ~123 MB แต่ CI ได้ ~151 MB (ชุด DLL ของ pythonnet/WebView2 ต่างกัน)
  → ใช้ asset จาก release เป็นตัวแทน dist เพื่อให้ SHA ตรงกับที่ผู้ใช้ดาวน์โหลด

## Active
- ไม่มี — v1.3.1 ปล่อยแล้ว

## Blocked
- code signing ยังไม่มีใบรับรอง (โครงพร้อม)
- Linux/macOS โหมดหน้าต่างต้องมี GTK/WebKit — ถ้าไม่มีจะ fallback เปิดเบราว์เซอร์

## Next Move
- รอฟีดแบ็กหน้า `/docs` `/playground` `/status` และโหมดหน้าต่าง
- ถ้าจะเซ็นจริง: ใส่ secret `WINDOWS_PFX_BASE64` + `WINDOWS_PFX_PASSWORD` ก่อน push tag ถัดไป

## commit ล่าสุด
- `91e3f14` (docs: add v1.3.1 release notes) — tag `v1.3.1`
- version: 1.3.1 — release แล้ว (release id 446981212)

## Session 10 (แผนปรับปรุง v1.3.2 → v1.4.0) — 2026-11-16

## Objective
ทำตาม `docs/PLAN.md` ทั้งหมด: แพตช์ v1.3.2 แล้วฟีเจอร์ v1.4.0 (ตัวติดตาม: `docs/CHECKLIST.md`)

## ข้อสำคัญ
- OCR หลายไฟล์/PDF หลายหน้า/progress **มีอยู่แล้ว** (ตัดออกจากแผน)
- ผู้ใช้เลือก: ยังไม่มีใบรับรอง (Phase C blocked) · แยก 2 release · export ใช้ข้อความที่แก้
- ผลตกลง: instance ต่างเวอร์ชัน = ไม่ผูกต่อ (ข้ามไปพอร์ตถัดไป)

## Completed
- **v1.3.2** (tag `v1.3.2`, commit `51fd6fd`): `_existing_instance` เทียบเวอร์ชัน (+ e2e จริง 5700→5701) ·
  `release.yml` รัน pytest · `tests/test_port.py` · แก้ `assert` เยื้องผิดใน `test_watch_folder` (`3e43923`)
- **v1.4.0** (tag `v1.4.0`, commit `0ace78d`):
  - export POST `{"text"}` (`_apply_edit`, `_edited_lines`) → PDF/CSV/DOCX/JSON/TXT ใช้ข้อความที่แก้
  - `/api/update-check` + แถบแจ้ง + prefs `update_check` (ทดสอบกับ GitHub จริง)
  - กรอบ SVG คลิกได้ (`overlay=0`, `pages[].size`) ภาพ ↔ ข้อความ ↔ รายบรรทัด
  - `OpenThai2OCR.spec` ตัด pymupdf layout onnx / mupdf-devel / opencv ffmpeg → Windows 151→95 MB, Linux 191→148, macOS 155→113
  - tests 39 ตัว · docs API/USAGE/`/docs` อัปเดต
- Release ทั้งสองมี SHA ใน notes + ตรวจ `.checked` แล้ว · `dist/OpenThai2OCR.exe` = asset v1.4.0 (`860d3230…9797`, 95 MB)

## Active
- ไม่มี

## Blocked
- Phase C: เซ็น exe — รอใบรับรอง .pfx (ใส่ secrets `WINDOWS_PFX_BASE64` / `WINDOWS_PFX_PASSWORD` แล้วออก patch release)

## Next Move
- เช็กด้วยมือในหน้าต่างแอป (WebView2): ปุ่มดาวน์โหลดขึ้น Save dialog, คัดลอก, คลิกกรอบบนภาพ
- ข้อเสนอเล็ก: lightbox แสดงกรอบ · smoke test รัน exe จริงใน CI · พิสูจน์ว่า pytest ล้ม → release ล้ม

## คำสั่งยืนยัน
- `python -m pytest -q` (39 ผ่าน) · `python tools/smoke_test.py`
- build ทดลอง: `python -m PyInstaller OpenThai2OCR.spec --noconfirm --clean --distpath dist_next --workpath .tmp\build`

## commit ล่าสุด
- `0ace78d` (feat(v1.4.0)) — tag `v1.4.0` · version: 1.4.0 — release แล้ว (release id RE_kwDOVv4pB84apOin)


---

## Session 11 (ต่อยอดหลัง v1.4.0 11 — lightbox แสดงกรอบ) — 2026-11-16

## Completed
- lightbox (ภาพเต็มจอ) มีกรอบ SVG คลิกเลือกบรรทัดได้ · ไฮไลต์ซิงก์ภาพหลัก/ช่องข้อความ · คลิกที่ว่างปิด (แก้ 	emplates/index.html เท่านั้น)
- ทดสอบจริงด้วย Playwright (banner.png 3 บรรทัด) + pytest 39 ผ่าน · CHANGELOG (หัว "ยังไม่ปล่อย") + CHECKLIST อัปเดต

- commit `ad56812` (lightbox) + `9663a75` (CI smoke test exe: `tools/exe_smoke.py` ในขั้น release.yml · publish รันเฉพาะ tag)
- ยืนยันบน CI: release (workflow_dispatch, run 43869907951) ผ่านทั้ง 3 OS รวมขั้น smoke exe · publish ข้าม
- พิสูจน์แล้ว: branch ทดลองที่ test ล้ม → API tests ล้ม, build/publish ไม่รัน (run 43870963213) · ลบ branch แล้ว

## Active
- ไม่มี (CHANGELOG/CHECKLIST/SESSION_STATE อัปเดตแล้ว รอ commit docs)

## Next Move
- รวมไปกับ release ถัดไป (v1.4.1 หรือพร้อมงานอื่น)
- ยังค้าง: เช็กมือในหน้าต่างแอป (WebView2 — ต้องคนกด) · Phase C เซ็น exe (รอ .pfx)

## commit ล่าสุด
- 9663a75 · version: 1.4.0 (โค้ดยังไม่บัมพ์)
