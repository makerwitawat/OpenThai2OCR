## 🚀 v1.3.1 — OpenThai2.0 OCR

แก้บั๊กปุ่มดาวน์โหลดในโหมดหน้าต่างโปรแกรม และปรับหน้าตากล่องยืนยัน/แจ้งเตือนใหม่

### 🐞 แก้ไข
- **ปุ่ม `.txt` / `.docx` / `.pdf` / `.csv` / `.json` กดแล้วเงียบในโหมดหน้าต่างโปรแกรม** —
  WebView2 ปิดการดาวน์โหลดไว้โดยค่าเริ่มต้น → เปิด `ALLOW_DOWNLOADS`
  (กดแล้วจะมีหน้าต่าง **บันทึกไฟล์** ของ Windows ให้เลือกที่เก็บ)
- **คัดลอกข้อความ** — เพิ่มวิธีสำรอง (`execCommand`) และแจ้งเตือนเมื่อคัดลอกไม่ได้
- กดปุ่มก่อนมีผลลัพธ์ (รายบรรทัด / ส่งออก) มีข้อความแจ้งชัดเจนแทนที่จะเงียบ

### ✨ ปรับปรุงหน้าตา
- **กล่องยืนยัน / กรอกข้อความแบบใหม่** แทน `confirm` / `prompt` ของเบราว์เซอร์ —
  ไอคอน, หัวข้อ, ปุ่มหลัก/ปุ่มอันตราย, กด Enter/Esc ได้, คลิกฉากหลังเพื่อปิด
  (ใช้กับปุ่มปิดโปรแกรมและช่อง API key)
- **แจ้งเตือนมุมล่างขวา (toast)** — คัดลอกแล้ว / กำลังดาวน์โหลด / ข้อผิดพลาด

### 📥 วิธีอัปเดต / ติดตั้ง
- **Windows**: ดาวน์โหลด `OpenThai2OCR-windows-x64.exe` วางที่โฟลเดอร์ไหนก็ได้ แล้วดับเบิลคลิก
- **Linux**: ดาวน์โหลด `OpenThai2OCR-linux-x64` แล้ว `chmod +x` และรัน
- **macOS**: ดาวน์โหลด `OpenThai2OCR-macos-*` แล้วรัน (ถ้าโดนกักกัน: คลิกขวา → Open)
- อัปเดตจาก v1.3.0: ปิดโปรแกรมเดิมแล้วแทนไฟล์ด้วยไฟล์ใหม่ ไม่ต้องย้ายข้อมูลใด ๆ
- รันจากซอร์ส: `python -m pip install -r requirements.txt` แล้ว `python app.py`

### ✅ ตรวจสอบไฟล์

| ไฟล์ | SHA256 |
|---|---|
| `OpenThai2OCR-windows-x64.exe` | `d1bc3cd55ff1c8e0007796c91b2a864603877c273acfa84483f2b7dfbf056070` |
| `OpenThai2OCR-linux-x64` | `eef85e32cdf4e821bc05fe04781d0e61f6deba39ad672d932ce7a54354fdb4f2` |
| `OpenThai2OCR-macos-arm64` | `86a508b6e06d59030db667b57c7c49cfe6e3d65a06484aba8856af2c44824799` |

### 🔗 ลิงก์
- คู่มือการใช้งาน: [docs/USAGE.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/USAGE.md)
- API reference (PHP/Python/JS/C#): [docs/API.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/API.md)
- ประวัติเวอร์ชัน: [CHANGELOG.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/CHANGELOG.md)
- สัญญาอนุญาต: Apache-2.0 (โมเดล © iApp Technology)

### ⚠️ หมายเหตุ
- ในโหมดหน้าต่างโปรแกรม การดาวน์โหลดจะถามที่เก็บไฟล์ทุกครั้ง (พฤติกรรมของ WebView2)
- โมเดลนี้อ่านตัวพิมพ์เป็นหลัก ลายมืออ่านได้ไม่ดี