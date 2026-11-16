# OpenThai2.0 OCR — Web UI + API

**ไทย** | [English](README.en.md)

หน้าเว็บอ่านข้อความไทย/อังกฤษจาก **รูปภาพและ PDF** ทำงานบนเครื่องตัวเอง (CPU) ใช้โมเดล
[`iapp/OpenThai2.0-OCR-Text`](https://huggingface.co/iapp/OpenThai2.0-OCR-Text) (Apache-2.0)
พร้อมหน้าเว็บภาษาไทย, วางภาพจาก clipboard, API JSON สำหรับเรียกจากโปรแกรมอื่น และ build เป็น exe ไฟล์เดียว

![OpenThai2.0 OCR](docs/banner.png)

## จุดเด่น

- **วางภาพได้ทันที** — ลากไฟล์, เลือกไฟล์ หรือกด `Ctrl+V` วางภาพที่คัดลอกมา (Snipaste / Print Screen)
- **รองรับหลายไฟล์/หลายหน้า** — รูปหลายรูปหรือ PDF หลายหน้า แยกแท็บผลลัพธ์ให้
- **แสดงผลพร้อมกล่องข้อความ** — วาดกรอบแต่ละบรรทัดพร้อมค่าความมั่นใจบนภาพ
- **ปรับขนาดตัวอักษรตามจอ** — ปุ่ม `A− A A+` จำค่าไว้ในเบราว์เซอร์
- **แถบความคืบหน้า + ยกเลิก** — PDF หลายหน้ารู้ว่าอ่านถึงหน้าไหน หยุดได้กลางทาง
- **ส่งออกได้หลายแบบ** — PDF ที่ค้นหาข้อความได้, Word (.docx), CSV (เปิด Excel), JSON, TXT
- **คัดลอกทีละบรรทัด** — กางรายการทุกบรรทัดพร้อมค่าความมั่นใจ แล้วคัดลอกเฉพาะที่ต้องการ
- **เฝ้าโฟลเดอร์อัตโนมัติ** — `--watch` วางไฟล์ลงโฟลเดอร์แล้วได้ .txt/.docx/.json ทันที
- **API พร้อมใช้** — multipart / JSON base64 / งานเบื้องหลัง (jobs), เปิด CORS, ตัวอย่าง 8 ภาษา
- **ความปลอดภัยพื้นฐาน** — จำกัดขนาดไฟล์ 100 MB / 50 หน้า, มี API key สำหรับโหมด LAN, log ไฟล์
- **สลับภาษาไทย/อังกฤษในหน้าเว็บได้** — ปุ่ม EN/ไทย (จำค่าไว้) และปุ่มปิดโปรแกรมในตัว
- **ไม่ต้องใช้ GPU** — ONNX Runtime บน CPU ประมาณ 0.1–0.5 วินาทีต่อหน้า A4
- **ไฟล์เดียวจบ** — `OpenThai2OCR.exe` ฝังโมเดลไว้ในตัว แจกจ่ายได้เลย (Windows)
  หรือ build เองบน Linux/macOS

## เริ่มใช้เร็วสุด (Windows)

1. ดาวน์โหลด `OpenThai2OCR-windows-x64.exe` จากหน้า [Releases](../../releases)
2. ดับเบิลคลิก — เบราว์เซอร์จะเปิดที่ `http://127.0.0.1:5000`
3. ลากรูป/PDF มาวาง หรือกด `Ctrl+V` วางภาพหน้าจอ → ได้ข้อความทันที

> ครั้งแรกอาจใช้เวลาหลายวินาทีเพราะต้องแตกไฟล์ภายในออกมาที่ temp

## รันจากซอร์สโค้ด (ทุก OS)

```bash
python -m pip install -r requirements.txt
python app.py                # เปิด http://127.0.0.1:5000
python app.py --no-browser   # ไม่เปิดเบราว์เซอร์
python app.py --host 0.0.0.0 --port 8080   # ให้เครื่องอื่นใน LAN เรียกได้
python app.py --watch "D:\inbox"           # เฝ้าโฟลเดอร์ แล้วอ่านไฟล์ใหม่อัตโนมัติ
```

## build เป็น exe

```bat
build_exe.bat          :: Windows — ไฟล์เดียว dist\OpenThai2OCR.exe (ฝังโมเดล)
build_exe_onedir.bat   :: Windows — โฟลเดอร์ dist\OpenThai2OCR\ (โหลดเร็วกว่า)
```

Linux / macOS:

```bash
python -m pip install -r requirements.txt -r requirements-build.txt
pyinstaller OpenThai2OCR.spec --noconfirm --clean
```

## API ย่อ

```bash
curl -F "file=@page.png" "http://127.0.0.1:5000/api/ocr"
```

```php
$ch = curl_init('http://127.0.0.1:5000/api/ocr');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => ['file' => new CURLFile('page.jpg')]]);
$res = json_decode(curl_exec($ch), true);
echo $res['text'];
```

รายละเอียดทั้งหมด (JSON base64, jobs/progress, export, API key, ตัวเลือก `scale`/`settings`) → [docs/API.md](docs/API.md)

## เอกสาร

| ไฟล์ | เนื้อหา |
|---|---|
| [docs/USAGE.md](docs/USAGE.md) | คู่มือการใช้งาน + การปรับแต่งความแม่นยำ (ไทย) |
| [docs/USAGE.en.md](docs/USAGE.en.md) | User guide + accuracy tuning (English) |
| [docs/API.md](docs/API.md) | API reference + ตัวอย่าง 8 ภาษา (ไทย) |
| [docs/API.en.md](docs/API.en.md) | API reference + 8 language examples (English) |
| [docs/BUILD.md](docs/BUILD.md) | build exe / release ทุก OS (ไทย) |
| [docs/BUILD.en.md](docs/BUILD.en.md) | Build & release (English) |
| [CHANGELOG.md](CHANGELOG.md) | ประวัติเวอร์ชัน |

## ข้อจำกัด

- โมเดลนี้อ่าน **ตัวพิมพ์ (printed text)** เป็นหลัก — ลายมือและป้ายในภาพถ่ายกลางแจ้งจะอ่านได้ไม่ดี
- ภาพความละเอียดต่ำ/ตัวอักษรเล็กมากอาจอ่านผิดบางตัว — ลองตั้ง "ความละเอียดภาพ" เป็น 2×
- ตราประทับ/ลายเซ็นอาจถูกอ่านออกมาเป็นข้อความ (เพราะเป็นตัวอักษรบนกระดาษ)

## เครดิต / สัญญาอนุญาต

- โค้ดโปรเจกต์นี้: [Apache-2.0](LICENSE)
- โมเดลและ runtime: © iApp Technology — `iapp/OpenThai2.0-OCR-Text` (Apache-2.0)
- ต้นแบบ detector/recognizer: PaddlePaddle PP-OCRv6-tiny (Apache-2.0) — ดู [NOTICE](NOTICE)