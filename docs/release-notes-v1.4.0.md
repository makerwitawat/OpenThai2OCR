## 🚀 v1.4.0 — OpenThai2.0 OCR

แก้ข้อความแล้วส่งออกได้ · คลิกกรอบบนภาพเพื่อเลือกบรรทัด · ตรวจอัปเดตอัตโนมัติ · ไฟล์เล็กลง ~37%

### ✨ ฟีเจอร์ใหม่
- **แก้ข้อความแล้วส่งออกได้** — ปุ่ม `.docx` / `.pdf` / `.csv` / `.json` ใช้ข้อความที่แก้ในช่องผลลัพธ์
  (เดิมใช้ผลดิบจาก OCR เสมอ) · API: `POST /api/result/<id>/export` พร้อม `{"text": "..."}` (ไม่ส่ง `text` = ผลเดิม)
- **คลิกกรอบบนภาพเพื่อเลือกบรรทัด** — คลิกกรอบ → ไฮไลต์ข้อความและรายการรายบรรทัด (คลิกฝั่งข้อความ/รายการก็เลือกกรอบตาม)
  ชี้กรอบเพื่อดูค่าความมั่นใจ · API: `overlay=0` ได้ภาพเปล่า และผลลัพธ์มี `pages[].size`
- **ตรวจอัปเดตจาก GitHub Releases** — ขึ้นแถบแจ้งเมื่อมีเวอร์ชันใหม่ ปิดได้ในช่อง "ตรวจอัปเดตอัตโนมัติ"
  (ติดต่อ GitHub เท่านั้น ไม่ส่งไฟล์หรือข้อความของคุณ) · API: `GET /api/update-check`

### ⚡ ปรับปรุง
- **ไฟล์ Windows เล็กลง ~37%** (151 → 95 MB; Linux 191 → 148 MB, macOS 155 → 113 MB) — ตัดส่วนที่โปรแกรมไม่ได้ใช้ (โมเดลเลย์เอาต์ pymupdf4llm,
  ไฟล์สำหรับคอมไพล์ของ MuPDF, ตัวถอดรหัสวิดีโอของ OpenCV) ทดสอบอ่านภาพ/PDF หลายหน้า/ส่งออกครบแล้ว

### 📥 วิธีอัปเดต / ติดตั้ง
- **Windows**: ดาวน์โหลด `OpenThai2OCR-windows-x64.exe` วางที่โฟลเดอร์ไหนก็ได้ แล้วดับเบิลคลิก
- **Linux**: ดาวน์โหลด `OpenThai2OCR-linux-x64` แล้ว `chmod +x` และรัน
- **macOS**: ดาวน์โหลด `OpenThai2OCR-macos-*` แล้วรัน (ถ้าโดนกักกัน: คลิกขวา → Open หรือ `xattr -d com.apple.quarantine <ไฟล์>`)
- **ไฟล์ยังไม่ได้เซ็นดิจิทัล**: Windows อาจขึ้น "Windows protected your PC" ให้กด **More info → Run anyway** (ตรวจ SHA256 ด้านล่างได้) — รายละเอียดใน [README](https://github.com/makerwitawat/OpenThai2OCR#ถ้า-windows--macos-เตือนตอนเปิดครั้งแรก)
- อัปเดตจาก v1.3.x: ปิดโปรแกรมเดิมแล้วแทนไฟล์ด้วยไฟล์ใหม่ ไม่ต้องย้ายข้อมูลใด ๆ
- รันจากซอร์ส: `python -m pip install -r requirements.txt` แล้ว `python app.py`

### ✅ ตรวจสอบไฟล์

| ไฟล์ | SHA256 |
|---|---|
| `OpenThai2OCR-windows-x64.exe` | `860d3230873d173786339883157714524b416ae798bfbfd0fbd63527a4bf9797` |
| `OpenThai2OCR-linux-x64` | `d584dacbc967a681e30ed863515ab5b5fcf27ff995e2e398c4f543d033f591c4` |
| `OpenThai2OCR-macos-arm64` | `44326c9b700a6d61598f42586270f702a26c44b2b436e2d41c629179d3ab7fad` |

### 🔗 ลิงก์
- คู่มือการใช้งาน: [docs/USAGE.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/USAGE.md)
- API reference (PHP/Python/JS/C#): [docs/API.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/API.md)
- ประวัติเวอร์ชัน: [CHANGELOG.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/CHANGELOG.md)
- สัญญาอนุญาต: Apache-2.0 (โมเดล © iApp Technology)

### ⚠️ หมายเหตุ
- ถ้าแก้ข้อความหลายไฟล์พร้อมกัน ให้คงหัว `=== ชื่อไฟล์ ===` ไว้ เพื่อให้ตัดส่วนของแต่ละไฟล์ถูกต้อง
- ส่งออก PDF/CSV: ถ้าจำนวนบรรทัดที่แก้ไม่เท่าเดิม ตำแหน่งข้อความจะกระจายในกรอบเดิม (ข้อความยังค้นหา/คัดลอกได้)
- ในโหมดหน้าต่างโปรแกรม การดาวน์โหลดจะถามที่เก็บไฟล์ทุกครั้ง (พฤติกรรมของ WebView2)
- โมเดลนี้อ่านตัวพิมพ์เป็นหลัก ลายมืออ่านได้ไม่ดี
