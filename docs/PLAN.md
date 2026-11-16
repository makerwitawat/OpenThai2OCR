# PLAN.md — แผนปรับปรุง OpenThai2.0 OCR (v1.3.2 → v1.4.0)

> ฐาน: v1.3.1 (commit 61a6d45) · สำรวจสถานะเมื่อ 2026-11-16 · ติดตามงานที่ `docs/CHECKLIST.md`
> ข้อมูล file:line ได้จากการสำรวจ — ต้องเปิดไฟล์ยืนยันอีกครั้งก่อนแก้

## 1. ขอบเขต

| # | กลุ่ม | รายการ | ทำเฟสไหน | หมายเหตุ |
|---|---|---|---|---|
| 1 | ความถูกต้อง | เทียบเวอร์ชัน instance เก่าที่พอร์ต 5000 | A (v1.3.2) | `_existing_instance` เช็กแค่ชื่อแอป (`app.py:970-979`) |
| 2 | คุณภาพ | release.yml รัน pytest ก่อน build | A | ตอนนี้รันแค่ smoke test (`release.yml:28-31`) |
| 3 | คุณภาพ | เพิ่ม test: พอร์ต/เวอร์ชัน/ส่งออก/หน้าเว็บ | A + B | ตอนนี้มี 13 test ใน `tests/test_api.py` |
| 4 | ความถูกต้อง | ส่งออก PDF/DOCX/CSV/JSON ใช้ข้อความที่ผู้ใช้แก้ | B (v1.4.0) | ตอนนี้ `/api/result/<id>/export` ใช้ผลเดิม (`app.py:922`) |
| 5 | ฟีเจอร์ | ตรวจอัปเดตจาก GitHub Releases | B | ยังไม่มี |
| 6 | ฟีเจอร์ | คลิกกรอบบนภาพเพื่อเลือก/ไฮไลต์บรรทัด | B | ตอนนี้เป็นภาพ PNG ฝังกรอบจากเซิร์ฟเวอร์ (`annotate_image` `app.py:198`) |
| 7 | ขนาด | วัดและลดขนาด exe (151 MB) | B | ประเมินเท่านั้น ต้องวัดจริงก่อน |
| 8 | ความปลอดภัย | เซ็น exe | C | **blocked** รอใบรับรอง (.pfx) |
| — | ตัดออก | OCR หลายไฟล์/PDF หลายหน้า/แถบความคืบหน้า | — | มีอยู่แล้ว (`index.html:665`, `app.py:164`, `app.py:718-751`) |

หลักการ: แก้ของที่ผิด/เสี่ยงก่อน (A) แล้วค่อยเพิ่มฟีเจอร์ (B) · ไม่แตะงานที่มีอยู่แล้ว

## 2. เฟส + DoD

### Phase A — v1.3.2 (แพตช์)
| งาน | ไฟล์ | วิธีทำ |
|---|---|---|
| A1 เทียบเวอร์ชัน | `app.py` | `_existing_instance` อ่าน `version` จาก `/api/health` (`app.py:628`) · เวอร์ชันต่างกัน → ไม่ผูกต่อ ข้ามไปพอร์ตถัดไป (สแกน N..N+10 เดิม) พร้อมข้อความไทยบอกผู้ใช้ |
| A2 test พอร์ต | `tests/test_port.py` | mock `/api/health` 3 กรณี: เวอร์ชันตรง · ต่าง · ไม่ใช่แอปเรา ; ห้ามพึ่งพอร์ต 5000 จริง ใช้ `--port` |
| A3 CI release | `.github/workflows/release.yml` | เพิ่มขั้น `python -m pytest -q` ก่อน smoke test+build (ใช้รูปแบบเดียวกับ `ci.yml`) |
| A4 ปล่อย | `CHANGELOG.md`, `docs/release-notes-v1.3.2.md` | ตาม release flow ใน handoff |

**DoD A:** exe 1.3.2 เปิดขณะ 1.3.1 รันอยู่ → ได้ instance ใหม่ (ไม่ผูกต่อตัวเก่า) · pytest ผ่านทั้งหมดบน CI · release job ล้มถ้า pytest ล้ม (พิสูจน์ด้วย test ที่จงใจ fail บน branch ชั่วคราว) · SHA ใน release ตรง `dist/OpenThai2OCR.exe`

### Phase B — v1.4.0 (ฟีเจอร์)
| งาน | ไฟล์ | วิธีทำ |
|---|---|---|
| B1 ส่งออกข้อความที่แก้ | `app.py`, `templates/index.html` | รับ `text` (optional) ใน body ของ `/api/result/<id>/export` · ถ้ามี ใช้แทนผลเดิม · UI ส่ง `out.value` · เก็บ API เดิมเข้ากันได้ (ไม่ส่ง `text` = ผลเดิม) · อัปเดต `docs/API.md` |
| B2 ตรวจอัปเดต | `app.py` (route `/api/update-check`), `index.html` | ฝั่งเซิร์ฟเวอร์เรียก GitHub Releases API (timeout 5 วิ, cache 6 ชม.) · เทียบเวอร์ชัน · UI แสดงแบนเนอร์/toast พร้อมลิงก์ · ปิดได้ใน prefs · ออฟไลน์/ล้มเหลว = เงียบ ไม่ขัดการใช้งาน |
| B3 คลิกกรอบ | `app.py`, `index.html` | ให้ API คืนพิกัดกรอบต่อบรรทัด (ถ้ายังไม่คืน) · UI วาดกรอบด้วย canvas/SVG ทับภาพ ไม่ฝังใน PNG · คลิกกรอบ → ไฮไลต์บรรทัดใน textarea และกลับกัน · `images=0` ยังใช้ได้ |
| B4 วัดขนาด exe | `OpenThai2OCR.spec` | วัดหาตัวกินพื้นที่ด้วยการดูใน onedir/`pyi-archive_viewer` ก่อนแก้ · exclude `pymupdf_layout`/`pymupdf4llm`/`shapely` เท่าที่ไม่ได้ใช้ (ตรวจ import ก่อน) · ทำทีละตัวแล้ว build + smoke test ทุกครั้ง |
| B5 test | `tests/` | test export ด้วย `text` · test update-check (mock HTTP) · smoke test รัน exe จริงด้วย `--port` |
| B6 ปล่อย | เหมือน A4 | v1.4.0 + อัปเดต `/docs` 5 ภาษาให้ตรง API ใหม่ |

**DoD B:** แก้ข้อความแล้วส่งออก PDF/DOCX/CSV/JSON ได้ข้อความที่แก้ (ทดสอบทั้ง 4 รูปแบบ) · update-check ทำงานเมื่อมี release ใหม่กว่า และไม่ค้างเมื่อออฟไลน์ · คลิกกรอบแล้วไฮไลต์ตรงบรรทัด (ทดสอบบนเบราว์เซอร์จริง) · exe เล็กลงโดยไม่ทำให้ฟังก์ชันหาย (เทียบก่อน/หลัง + smoke test ผ่าน) · pytest ผ่านทั้งหมด

### Phase C — เซ็น exe (blocked)
- รอใบรับรอง .pfx → ใส่ secrets `WINDOWS_PFX_BASE64`, `WINDOWS_PFX_PASSWORD` → ออก patch release ถัดไป (ใช้ `tools/sign_exe.ps1` + workflow ที่มี `env` ระดับ job)
- **DoD C:** `Get-AuthenticodeSignature` ของ exe ที่ release ได้สถานะ Valid

## 3. Gotchas (จาก handoff — ห้ามพลาดซ้ำ)
| กับดัก | วิธีรับมือ |
|---|---|
| `secrets.*` ใน `if` ของ step ทำให้ workflow parse ล้ม | ใช้ `env` ระดับ job แล้วทดสอบ `env.X` |
| ต่อท้าย requirements.txt ไม่มี newline | ตรวจขึ้นบรรทัดใหม่ท้ายไฟล์ ก่อน tag |
| build ขณะ exe รัน → PermissionError | build ไป `--distpath dist_next` แล้วค่อย copy |
| instance เก่าที่พอร์ต 5000 | ทดสอบทุกครั้งด้วย `--port` (A1 แก้ที่ต้นเหตุ) |
| Flask cache template เมื่อไม่ debug | restart server หลังแก้ template |
| `release-notes-patch.py` เติม `assets[0]` (linux) | กรอกตาราง SHA เอง แล้วค่อยรันสคริปต์ |
| pywebview ดาวน์โหลดถูกยกเลิกเงียบ | `ALLOW_DOWNLOADS` เปิดไว้แล้ว — ห้ามถอด |
| grep ผ่าน PowerShell เห็นไทยเป็น `?` | ตรวจไทยด้วย Read tool เท่านั้น ห้าม Set-Content แก้ไฟล์ไทย |

## 4. คำสั่งยืนยัน
| งาน | คำสั่ง |
|---|---|
| test | `.venv\Scripts\python.exe -m pytest -q` |
| smoke | `.venv\Scripts\python.exe tools\smoke_test.py` |
| build | ดู `docs/BUILD.md` (ใช้ `--distpath dist_next`) |
| release | notes → tag/push → รอ CI → กรอก SHA → `tools\release-notes-patch.py` → ตรวจ `.checked` ด้วย Read |

## 5. กติกา
- ตอบ/เอกสารเป็นไทย · stage เฉพาะไฟล์ตัวเอง ห้าม `git add -A` · ไฟล์ชั่วคราวใน `.tmp/`
- ปิดแต่ละเฟส: อัปเดต `docs/SESSION_STATE.md` + `CHANGELOG.md` → commit → push
