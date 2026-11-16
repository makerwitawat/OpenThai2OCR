## 🚀 v1.3.0 — OpenThai2.0 OCR

เพิ่มหน้าที่ช่วยเชื่อมต่อ/ทดสอบ API, โหมดหน้าต่างโปรแกรม (ไม่ต้องใช้เบราว์เซอร์)
และปรับขนาดตัวอักษรได้ทุกหน้า

### ✨ ฟีเจอร์ใหม่
- **หน้าต่างโปรแกรม (GUI)** — `--window` เปิด UI ในหน้าต่างจริงบนเดสก์ท็อป (WebView2)
  ไม่ต้องมีเบราว์เซอร์ · ถ้าไม่มี pywebview จะกลับไปเปิดเบราว์เซอร์ให้อัตโนมัติ
- **เลือกโหมดเมื่อเริ่มโปรแกรม** (จำค่า) — หน้าต่างโปรแกรม / เบราว์เซอร์ / ไม่เปิดอะไร (headless)
  · `--window` `--browser` `--no-browser` (CLI ชนะค่าที่จำ) · เก็บใน `settings.json` +
  `%LOCALAPPDATA%\OpenThai2OCR\settings.json`
- **หน้า `/docs` — สอนเชื่อมต่อ API** — endpoint ทั้งหมด, ตัวอย่าง curl / Python / JavaScript / PHP / C#,
  รูปแบบคำตอบ, `settings` ที่ใช้บ่อย, jobs, errors, watch folder, ปุ่มคัดลอกโค้ด (ไทย/อังกฤษ)
- **หน้า `/playground` — ทดสอบ API จริง** — อัปโหลดภาพ/PDF, เลือก `scale`/`settings`, ขอภาพผลลัพธ์,
  แสดงข้อความ + JSON + สรุปเวลา, คัดลอกคำสั่ง curl, ดาวน์โหลดผลได้
- **หน้า `/status`** — version, uptime, สถานะโมเดล, โหมด API key, โหมดเริ่มโปรแกรม, ขีดจำกัด,
  watch folder และงาน OCR ล่าสุด 20 งาน (รีเฟรชเองทุก 3 วินาที)
- **ขนาดตัวอักษร A− / A / A+** มีทุกหน้า และใช้ค่าเดียวกัน (จำค่าไว้)
- **API ใหม่** — `GET /api/status`, `GET`/`POST /api/prefs` (`start_mode`) · `/api/health` เพิ่ม `uptime_s`

### 🐞 แก้ไข
- ตั้งค่า "ไม่เปิดเบราว์เซอร์" แล้ว exe ยังเปิดเบราว์เซอร์ เพราะอ่าน `settings.json` คนละที่ →
  ตอนนี้เขียน/อ่านทั้งข้าง exe และ `%LOCALAPPDATA%\OpenThai2OCR\settings.json`

### 📥 วิธีอัปเดต / ติดตั้ง
- **Windows**: ดาวน์โหลด `OpenThai2OCR-windows-x64.exe` วางที่โฟลเดอร์ไหนก็ได้ แล้วดับเบิลคลิก
- **Linux**: ดาวน์โหลด `OpenThai2OCR-linux-x64` แล้ว `chmod +x` และรัน
- **macOS**: ดาวน์โหลด `OpenThai2OCR-macos-*` แล้วรัน (ถ้าโดนกักกัน: คลิกขวา → Open)
- อัปเดตจาก v1.2.0: ปิดโปรแกรมเดิมแล้วแทนไฟล์ด้วยไฟล์ใหม่ ไม่ต้องย้ายข้อมูลใด ๆ
- รันจากซอร์ส: `python -m pip install -r requirements.txt` แล้ว `python app.py`

### ✅ ตรวจสอบไฟล์

| ไฟล์ | SHA256 |
|---|---|
| `OpenThai2OCR-windows-x64.exe` | `aa60fd4cfb78795dd0107533125a089fba411aa24dc982e5400a845ad41c0f5d` |
| `OpenThai2OCR-linux-x64` | `df3b8747aba48c07c1ce13a6b9fa88907c7438149d92c21eefdb27a8097d6d00` |
| `OpenThai2OCR-macos-arm64` | `4fd79a5dd8843dacac1beb455efd7894f926d581a0cf548fe7981d70f217804e` |

### 🔗 ลิงก์
- คู่มือการใช้งาน: [docs/USAGE.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/USAGE.md)
- API reference (PHP/Python/JS/C#): [docs/API.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/API.md)
- ประวัติเวอร์ชัน: [CHANGELOG.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/CHANGELOG.md)
- สัญญาอนุญาต: Apache-2.0 (โมเดล © iApp Technology)

### ⚠️ หมายเหตุ
- โมเดลนี้อ่านตัวพิมพ์เป็นหลัก ลายมืออ่านได้ไม่ดี
- โหมดหน้าต่างโปรแกรมใช้ WebView2 (มีมาใน Windows 10/11) — Linux/macOS ถ้าไม่มี GTK/WebKit
  โปรแกรมจะกลับไปเปิดเบราว์เซอร์ให้
- exe ยังไม่ได้เซ็นชื่อในรุ่นนี้ (โครงพร้อม — ใส่ secret `WINDOWS_PFX_BASE64` แล้วปล่อยรุ่นถัดไป)