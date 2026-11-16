## 🚀 v1.3.2 — OpenThai2.0 OCR

แพตช์แก้การเปิดโปรแกรมใหม่ขณะที่เวอร์ชันเก่ายังค้างอยู่

### 🐞 แก้ไข
- **เปิดโปรแกรมใหม่แล้วได้ตัวเก่า** — ถ้ามีเวอร์ชันเก่ารันค้างที่พอร์ต 5000 โปรแกรมใหม่เคยผูกต่อไปที่ตัวเก่า
  (หน้าเว็บและ API เป็นเวอร์ชันเก่า) → ตอนนี้เทียบเวอร์ชันก่อน ถ้าไม่ตรงจะเปิด instance ใหม่ที่พอร์ตว่างถัดไป
  (เช่น 5001) ส่วนเวอร์ชันเดียวกันยังผูกต่อได้เหมือนเดิม

### 🔧 ภายใน
- workflow `release` รัน `pytest` ก่อน build — test ล้มจะไม่ปล่อย release
- เพิ่ม test สำหรับการเลือกพอร์ต/เทียบเวอร์ชัน (รวม 17 test)

### 📥 วิธีอัปเดต / ติดตั้ง
- **Windows**: ดาวน์โหลด `OpenThai2OCR-windows-x64.exe` วางที่โฟลเดอร์ไหนก็ได้ แล้วดับเบิลคลิก
- **Linux**: ดาวน์โหลด `OpenThai2OCR-linux-x64` แล้ว `chmod +x` และรัน
- **macOS**: ดาวน์โหลด `OpenThai2OCR-macos-*` แล้วรัน (ถ้าโดนกักกัน: คลิกขวา → Open)
- อัปเดตจาก v1.3.1: ปิดโปรแกรมเดิมแล้วแทนไฟล์ด้วยไฟล์ใหม่ ไม่ต้องย้ายข้อมูลใด ๆ
- รันจากซอร์ส: `python -m pip install -r requirements.txt` แล้ว `python app.py`

### ✅ ตรวจสอบไฟล์

| ไฟล์ | SHA256 |
|---|---|
| `OpenThai2OCR-windows-x64.exe` | `3024ad401ae8acc5d0d0767b6aa7d3b8ea6d35b92dde15ddf85358d1a40f7ef5` |
| `OpenThai2OCR-linux-x64` | `d288d734c5282880066d4939a50360ae5b1794d75af188436f04f600c186abd4` |
| `OpenThai2OCR-macos-arm64` | `5021495d09ffe60e8335b26d28f332220fb46745bc3698774cbf0658d00c6d4b` |

### 🔗 ลิงก์
- คู่มือการใช้งาน: [docs/USAGE.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/USAGE.md)
- API reference (PHP/Python/JS/C#): [docs/API.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/API.md)
- ประวัติเวอร์ชัน: [CHANGELOG.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/CHANGELOG.md)
- สัญญาอนุญาต: Apache-2.0 (โมเดล © iApp Technology)

### ⚠️ หมายเหตุ
- ในโหมดหน้าต่างโปรแกรม การดาวน์โหลดจะถามที่เก็บไฟล์ทุกครั้ง (พฤติกรรมของ WebView2)
- โมเดลนี้อ่านตัวพิมพ์เป็นหลัก ลายมืออ่านได้ไม่ดี
