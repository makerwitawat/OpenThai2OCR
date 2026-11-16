# CHECKLIST.md — ตัวติดตามความคืบหน้า

> ใช้คู่กับ `docs/PLAN.md` — ขีด ✓ เมื่อทำเสร็จและ verify จริงแล้วเท่านั้น

## Phase A — v1.3.2
- [ ] A1 `_existing_instance` เทียบ `version` จาก `/api/health` · ต่างเวอร์ชัน → ข้ามไปพอร์ตถัดไป + ข้อความไทย
- [ ] A2 `tests/test_port.py` ครอบ 3 กรณี (ตรง/ต่าง/ไม่ใช่แอปเรา)
- [ ] A3 `release.yml` รัน pytest ก่อน build · พิสูจน์ว่า test ล้ม → release ล้ม
- [ ] A4 CHANGELOG + release notes v1.3.2 → tag → CI → SHA → patch script → ตรวจ `.checked`
- [ ] DoD A: เปิด exe ใหม่ขณะ 1.3.1 รัน → ได้ instance ใหม่ · pytest ผ่านบน CI · SHA ตรง `dist/OpenThai2OCR.exe`

## Phase B — v1.4.0
- [ ] B1 export ใช้ `text` ที่แก้แล้ว (PDF / DOCX / CSV / JSON) + เข้ากันได้ย้อนหลัง + อัปเดต `docs/API.md`
- [ ] B2 update-check: route + cache + UI + ปิดได้ใน prefs + ออฟไลน์ไม่ค้าง
- [ ] B3 คลิกกรอบบนภาพ ↔ ไฮไลต์บรรทัด (canvas/SVG) · `images=0` ยังใช้ได้
- [ ] B4 วัดขนาด exe ก่อน/หลัง · exclude ทีละตัว · smoke test ทุกครั้ง
- [ ] B5 test: export ด้วย text · update-check (mock) · smoke รัน exe จริงด้วย `--port`
- [ ] B6 `/docs` 5 ภาษาตรง API ใหม่ · CHANGELOG + release v1.4.0
- [ ] DoD B: ทุกข้อ B1–B5 verify แล้ว · ทดสอบบนเบราว์เซอร์/หน้าต่างแอปจริง · pytest ผ่านทั้งหมด

## Phase C — เซ็น exe (blocked: รอใบรับรอง .pfx)
- [ ] ได้ใบรับรอง
- [ ] ใส่ secrets `WINDOWS_PFX_BASE64`, `WINDOWS_PFX_PASSWORD`
- [ ] patch release ถัดไป + `Get-AuthenticodeSignature` = Valid

## ค้างจาก handoff
- [ ] เช็กด้วยมือในหน้าต่างแอป: ปุ่มดาวน์โหลดขึ้น Save dialog · ปุ่มคัดลอกใช้ได้

### คุณภาพขั้นต่ำต่อรายการ (ก่อนขีด ✓)
- [ ] โค้ดตามแผน + ไม่แตะ API เดิมแบบทำให้พัง
- [ ] มี test (unit/mock) หรือเหตุผลที่ test ไม่ได้
- [ ] ทดสอบจริง (เบราว์เซอร์/exe) ไม่ใช่แค่ pytest
- [ ] ข้อความผู้ใช้เป็นไทย · อัปเดตเอกสารที่เกี่ยวข้อง
