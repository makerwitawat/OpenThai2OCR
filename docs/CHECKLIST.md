# CHECKLIST.md — ตัวติดตามความคืบหน้า

> ใช้คู่กับ `docs/PLAN.md` — ขีด ✓ เมื่อทำเสร็จและ verify จริงแล้วเท่านั้น

## Phase A — v1.3.2 ✅ ปล่อยแล้ว (tag `v1.3.2`)
- [x] A1 `_existing_instance` เทียบ `version` จาก `/api/health` · ต่างเวอร์ชัน → ข้ามไปพอร์ตถัดไป + log เตือน
- [x] A2 `tests/test_port.py` ครอบ 4 กรณี (ตรง/ต่าง/ต่างแล้วตามด้วยตรง/ไม่ใช่แอปเรา+error)
- [x] A3 `release.yml` รัน pytest ก่อน build (ติดตั้ง requirements-dev ด้วย)
  - ยังไม่ได้พิสูจน์ว่า test ล้ม → release ล้มจริงด้วย branch ทดลอง (เชื่อตามพฤติกรรม GitHub Actions: step ล้ม = job ล้ม = `publish` ไม่รัน)
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
  - ยังไม่ได้เพิ่ม smoke test รัน exe จริงเข้า CI (ทดสอบด้วยมือผ่านสคริปต์ชั่วคราวเท่านั้น)
- [x] B6 `docs/API*.md`, `USAGE*.md`, `/docs` อัปเดต · CHANGELOG + release v1.4.0 (SHA กรอกแล้ว, `.checked` ตรวจแล้ว)
- [x] DoD B: ทดสอบบนเบราว์เซอร์จริง + exe ที่ปล่อย (`dist/OpenThai2OCR.exe` = asset SHA `860d3230…9797`, 95 MB)

## Phase C — เซ็น exe (blocked: รอใบรับรอง .pfx)
- [ ] ได้ใบรับรอง
- [ ] ใส่ secrets `WINDOWS_PFX_BASE64`, `WINDOWS_PFX_PASSWORD`
- [ ] patch release ถัดไป + `Get-AuthenticodeSignature` = Valid

## ค้าง / ข้อเสนอต่อ
- [ ] เช็กด้วยมือในหน้าต่างแอป: ปุ่มดาวน์โหลดขึ้น Save dialog · ปุ่มคัดลอกใช้ได้ · คลิกกรอบบนภาพ (WebView2 จริง ผมทดสอบได้แค่ว่าหน้าต่างเปิด)
- [ ] smoke test รัน exe จริง (`--port`) ใน CI
- [x] lightbox แสดงกรอบ + คลิกเลือกบรรทัดได้ (ทำแล้วใน `templates/index.html` ยังไม่ commit/ปล่อย · ทดสอบเบราว์เซอร์จริงด้วย Playwright)

### คุณภาพขั้นต่ำต่อรายการ (ก่อนขีด ✓)
- [x] โค้ดตามแผน + ไม่แตะ API เดิมแบบทำให้พัง
- [x] มี test (unit/mock) หรือเหตุผลที่ test ไม่ได้
- [x] ทดสอบจริง (เบราว์เซอร์/exe) ไม่ใช่แค่ pytest
- [x] ข้อความผู้ใช้เป็นไทย · อัปเดตเอกสารที่เกี่ยวข้อง
