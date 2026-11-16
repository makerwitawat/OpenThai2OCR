# CHECKLIST.md — ตัวติดตามความคืบหน้า

> ใช้คู่กับ `docs/PLAN.md` — ขีด ✓ เมื่อทำเสร็จและ verify จริงแล้วเท่านั้น

## Phase A — v1.3.2 ✅ ปล่อยแล้ว (tag `v1.3.2`)
- [x] A1 `_existing_instance` เทียบ `version` จาก `/api/health` · ต่างเวอร์ชัน → ข้ามไปพอร์ตถัดไป + log เตือน
- [x] A2 `tests/test_port.py` ครอบ 4 กรณี (ตรง/ต่าง/ต่างแล้วตามด้วยตรง/ไม่ใช่แอปเรา+error)
- [x] A3 `release.yml` รัน pytest ก่อน build (ติดตั้ง requirements-dev ด้วย)
  - พิสูจน์แล้ว (2026-11-16): branch ทดลองที่มี test ล้ม → ขั้น API tests ล้ม · build/publish ไม่รัน (run 43870963213) · ลบ branch แล้ว
- [x] A4 CHANGELOG + release notes v1.3.2 → tag → CI → SHA → patch script → ตรวจ `.checked` ด้วย Read
- [x] DoD A: ทดสอบ e2e — เปิด instance เวอร์ชัน 1.3.1 ที่ 5700 แล้วรันตัวใหม่ `--port 5700` → ได้ 5701 (1.3.2) · pytest ผ่านบน CI · SHA ตรง `dist/OpenThai2OCR.exe`

## Phase B — v1.4.0 ✅ ปล่อยแล้ว (tag `v1.4.0`)
- [x] B1 export ใช้ `text` ที่แก้แล้ว (PDF / DOCX / CSV / JSON / TXT) + เข้ากันได้ย้อนหลัง + อัปเดต `docs/API.md` / `API.en.md` / `docs.html`
  - ทดสอบเบราว์เซอร์จริง: แก้ข้อความ → ดาวน์โหลด .csv/.pdf ได้ข้อความที่แก้ · ทดสอบ PDF 2 หน้าด้วย `--- หน้า N ---`
- [x] B2 update-check: route + cache 6 ชม. + negative cache 10 นาที + แบนเนอร์ + สวิตช์ใน prefs + ออฟไลน์เงียบ (ทดสอบกับ GitHub จริง)
- [x] B3 คลิกกรอบบนภาพ ↔ ไฮไลต์บรรทัด (SVG) · `images=0` ใช้ได้ · API ใหม่ `overlay=0` + `pages[].size`
  - ข้อจำกัด: lightbox (คลิกภาพเต็มจอ) แสดงภาพเปล่าไม่มีกรอบ · ไฮไลต์ในช่องข้อความหาจากข้อความตามลำดับ (หลังผู้ใช้แก้ข้อความอาจหาไม่เจอ = ไม่ไฮไลต์)
- [x] B4 วัดขนาด exe: ตัวกินพื้นที่คือ `pymupdf/layout/resources/onnx` (~38 MB), `opencv_videoio_ffmpeg` (13 MB), `mupdf-devel` → ตัดใน spec · Windows CI 151 → 95 MB, Linux 191 → 148, macOS 155 → 113
- [x] B5 test: 39 ตัว (export แก้ข้อความ, update-check mock, overlay/size, PDF 2 หน้า) · รัน exe จริงด้วย `--port`: อ่านภาพ + PDF 2 หน้า + export 5 รูปแบบ + export แก้ข้อความ + update-check + โหมด `--window` เปิดได้
  - เพิ่ม smoke test รัน exe จริงใน release.yml แล้ว (`tools/exe_smoke.py`) · ผ่านทั้ง 3 OS (run 43869907951)
- [x] B6 `docs/API*.md`, `USAGE*.md`, `/docs` อัปเดต · CHANGELOG + release v1.4.0 (SHA กรอกแล้ว, `.checked` ตรวจแล้ว)
- [x] DoD B: ทดสอบบนเบราว์เซอร์จริง + exe ที่ปล่อย (`dist/OpenThai2OCR.exe` = asset SHA `860d3230…9797`, 95 MB)

## Phase D — v1.5.0 ✅ (ตั้งค่า + build เล็กลง + เปิดเร็ว)
- [x] D1 `settings.json` ครบทุกค่า + หน้า `/settings` + `GET/POST /api/config` (local-only, ตรวจ Origin)
- [x] D2 exe เล็กลง 105 → 87 MB (build ใน `.venv` สะอาด + ตัดแพ็กเกจที่ไม่ใช้)
- [x] D3 แก้บั๊ก prefs เขียนทับกัน (`start_mode` หาย) · lightbox แสดงกรอบ · สคริปต์ .bat/CI smoke test
- [x] D4 แก้เปิดช้า: `_existing_instance` ไล่ 11 พอร์ตรอ timeout (~8 วิ) → เช็ก bind ก่อน · โหมดหน้าต่างเปลี่ยน `sleep 0.8` เป็น `_wait_port`
  - วัดจาก exe จริง: เซิร์ฟเวอร์พร้อม 9.7 → ~2 วิ (onefile) / 8.5 → ~0.6 วิ (onedir) · หน้าต่างขึ้น onefile 2.3–3.2 วิ
- [x] D5 pytest 73 ตัวผ่าน · build onefile + onedir + smoke test ผ่าน · เอกสาร (CHANGELOG/BUILD/USAGE/API) อัปเดต

## Phase C — เซ็น exe (blocked: รอใบรับรอง .pfx)
- [ ] ได้ใบรับรอง
- [ ] ใส่ secrets `WINDOWS_PFX_BASE64`, `WINDOWS_PFX_PASSWORD`
- [ ] patch release ถัดไป + `Get-AuthenticodeSignature` = Valid

## ค้าง / ข้อเสนอต่อ
- [ ] เช็กด้วยมือในหน้าต่างแอป: ปุ่มดาวน์โหลดขึ้น Save dialog · ปุ่มคัดลอกใช้ได้ · คลิกกรอบบนภาพ (WebView2 จริง ผมทดสอบได้แค่ว่าหน้าต่างเปิด)
- [x] smoke test รัน exe จริง (`--port`) ใน CI
- [x] lightbox แสดงกรอบ + คลิกเลือกบรรทัดได้ (ทำแล้วใน `templates/index.html` ยังไม่ commit/ปล่อย · ทดสอบเบราว์เซอร์จริงด้วย Playwright)

### คุณภาพขั้นต่ำต่อรายการ (ก่อนขีด ✓)
- [x] โค้ดตามแผน + ไม่แตะ API เดิมแบบทำให้พัง
- [x] มี test (unit/mock) หรือเหตุผลที่ test ไม่ได้
- [x] ทดสอบจริง (เบราว์เซอร์/exe) ไม่ใช่แค่ pytest
- [x] ข้อความผู้ใช้เป็นไทย · อัปเดตเอกสารที่เกี่ยวข้อง
