## 🚀 v1.2.0 — OpenThai2.0 OCR

ต่อยอดจาก v1.1.0: คัดลอกทีละบรรทัด, ส่งออก Word (.docx), โหมดเฝ้าโฟลเดอร์อัตโนมัติ
และโครงเซ็นชื่อ exe สำหรับ release จริง

### ✨ ฟีเจอร์ใหม่
- **คัดลอกทีละบรรทัด** — ปุ่ม "รายบรรทัด / Lines" กางทุกบรรทัดของหน้าปัจจุบันพร้อม % ความมั่นใจ
  คัดลอกทีละบรรทัด หรือ "คัดลอกทุกบรรทัด" ทั้งหน้า
- **ส่งออก Word (.docx)** — บรรทัดละย่อหน้า ฟอนต์ Leelawadee UI แก้ไขต่อได้ทันที
  ใช้ได้ทั้งปุ่มบนหน้าเว็บและ API `format=docx` (สร้าง OOXML เอง ไม่เพิ่ม dependency)
- **เฝ้าโฟลเดอร์ (watch folder)** — `--watch DIR --watch-out DIR --watch-interval SEC`
  ตรวจไฟล์ใหม่แล้วเขียน `<stem>-ocr.txt`, `.docx`, `.json` · ไฟล์ต้นฉบับไม่ถูกย้าย
  อ่านซ้ำเฉพาะเมื่อขนาด/เวลาแก้เปลี่ยน · ข้ามไฟล์ที่ยังคัดลอกไม่เสร็จ
- **เซ็นชื่อ exe (code signing)** — `tools/sign_exe.ps1` (รองรับ .pfx / thumbprint + timestamp + verify)
  และขั้นเซ็นอัตโนมัติใน workflow `release` (เปิดเมื่อมี secret `WINDOWS_PFX_BASE64`)
- `/api/health` รายงานสถานะ `watch` (dir / out / interval)

### 🐞 แก้ไข
- สลับภาษาไทย/อังกฤษแล้วสถานะและชื่อไฟล์ในช่องวางไฟล์หาย

### 📥 วิธีอัปเดต / ติดตั้ง
- **Windows**: ดาวน์โหลด `OpenThai2OCR-windows-x64.exe` วางที่โฟลเดอร์ไหนก็ได้ แล้วดับเบิลคลิก
- **Linux**: ดาวน์โหลด `OpenThai2OCR-linux-x64` แล้ว `chmod +x` และรัน
- **macOS**: ดาวน์โหลด `OpenThai2OCR-macos-*` แล้วรัน (ถ้าโดนกักกัน: คลิกขวา → Open)
- อัปเดตจาก v1.1.0: ปิดโปรแกรมเดิมแล้วแทนไฟล์ด้วยไฟล์ใหม่ ไม่ต้องย้ายข้อมูลใด ๆ
- รันจากซอร์ส: `python -m pip install -r requirements.txt` แล้ว `python app.py`

### ✅ ตรวจสอบไฟล์

| ไฟล์ | SHA256 |
|---|---|
| `OpenThai2OCR-windows-x64.exe` | `e4b6e47c7cc0d8f425d0450c13221590a220a250c72a4160362dfbf85e056228` |
| `OpenThai2OCR-linux-x64` | `0df6972f990496b6b8bb5c95d588be8befd63fc90a8fd658367510ee8fc69c5e` |
| `OpenThai2OCR-macos-arm64` | `8b66f223109cd250877f2b0d059488133bae43044f7abc4564d42788717268cf` |

### 🔗 ลิงก์
- คู่มือการใช้งาน: [docs/USAGE.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/USAGE.md)
- API reference (PHP/Python/JS/C#): [docs/API.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/API.md)
- ประวัติเวอร์ชัน: [CHANGELOG.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/CHANGELOG.md)
- สัญญาอนุญาต: Apache-2.0 (โมเดล © iApp Technology)

### ⚠️ หมายเหตุ
- โมเดลนี้อ่านตัวพิมพ์เป็นหลัก ลายมืออ่านได้ไม่ดี
- ยังไม่ได้เซ็นชื่อ exe จริงในรุ่นนี้ (โครงพร้อมแล้ว — ใส่ secret แล้วปล่อยรุ่นถัดไป)