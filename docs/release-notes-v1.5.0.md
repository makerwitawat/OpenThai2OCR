## 🚀 v1.5.0 — OpenThai2.0 OCR

เปิดโปรแกรมเร็วขึ้นมาก · หน้าตั้งค่า (`/settings`) + `settings.json` · ไฟล์ Windows เล็กลงเหลือ ~87 MB

### ✨ ฟีเจอร์ใหม่
- **หน้าเว็บ "ตั้งค่า" (`/settings`)** — แก้ค่าทั้งหมดในหน้าเดียว ตรวจค่าให้ มีปุ่มกลับค่าเริ่มต้น และบอกว่าต้องรีสตาร์ต
  (เปิดได้เฉพาะจากเครื่องที่รันโปรแกรม) · API: `GET/POST /api/config`
- **ตั้งค่าผ่าน `settings.json`** — host, port, path (โมเดล/log/watch), ขีดจำกัดอัปโหลด/หน้า PDF, thread, API key ฯลฯ
  ลำดับความสำคัญ: flag CLI > `settings.json` > ค่าเริ่มต้น · เพิ่ม flag `--port-tries --log-dir --max-upload-mb --max-pages --threads --engine-threads`
- **ภาพเต็มจอ (lightbox) แสดงกรอบ** — คลิกกรอบเพื่อเลือกบรรทัดได้ เหมือนภาพหลัก

### 🔧 แก้บั๊ก
- **เปิดโปรแกรมช้า (~10 วินาทีกว่า GUI จะขึ้น)** — เดิมเช็ก instance ที่รันอยู่ด้วยการไล่ยิงทุกพอร์ต 5000–5010 รอ timeout ทีละพอร์ต
  ตอนนี้เช็กเฉพาะพอร์ตที่มีโปรแกรมจับอยู่จริง · โหมดหน้าต่างเอาการหน่วง 0.8 วินาทีตายตัวออก
- **ค่า "เมื่อเริ่มโปรแกรม" (เช่น เปิดเป็นหน้าต่าง) หายหลังบันทึกค่าอื่น** — ไฟล์ตั้งค่า 2 ที่เขียนทับกัน แก้แล้ว
- `--port` ที่ไม่ใช่ตัวเลขไม่ทำให้โปรแกรมล้มแล้ว · ไล่พอร์ตสำรอง 5000–5010 ได้จริง (เดิมลองแค่ 5000)

### ⚡ ปรับปรุง
- **เวลาเปิดโปรแกรม (วัดจากไฟล์จริงบน Windows)**: เซิร์ฟเวอร์พร้อม ~10 → ~2 วินาที (ไฟล์เดียว) · หน้าต่างโปรแกรมขึ้นใน ~2–3 วินาที
- **ไฟล์ Windows เล็กลง 105 → ~87 MB** — ตัดแพ็กเกจที่โปรแกรมไม่ได้ใช้ (cryptography, Pillow ฯลฯ)

### 📥 วิธีอัปเดต / ติดตั้ง
- **Windows**: ดาวน์โหลด `OpenThai2OCR-windows-x64.exe` วางที่โฟลเดอร์ไหนก็ได้ แล้วดับเบิลคลิก
- **Linux**: ดาวน์โหลด `OpenThai2OCR-linux-x64` แล้ว `chmod +x` และรัน
- **macOS**: ดาวน์โหลด `OpenThai2OCR-macos-*` แล้วรัน (ถ้าโดนกักกัน: คลิกขวา → Open หรือ `xattr -d com.apple.quarantine <ไฟล์>`)
- **ไฟล์ยังไม่ได้เซ็นดิจิทัล**: Windows อาจขึ้น "Windows protected your PC" ให้กด **More info → Run anyway** (ตรวจ SHA256 ด้านล่างได้) — รายละเอียดใน [README](https://github.com/makerwitawat/OpenThai2OCR#ถ้า-windows--macos-เตือนตอนเปิดครั้งแรก)
- อัปเดตจาก v1.4.x: ปิดโปรแกรมเดิมแล้วแทนไฟล์ด้วยไฟล์ใหม่ ไม่ต้องย้ายข้อมูลใด ๆ (ค่าที่เคยตั้งใน `settings.json` ใช้ต่อได้)
- รันจากซอร์ส: `python -m pip install -r requirements.txt` แล้ว `python app.py`
- อยากให้เปิดเร็วขึ้นอีก (~1 วินาที): build แบบโฟลเดอร์ด้วย `build_exe_onedir.bat` (แจกทั้งโฟลเดอร์)

### ✅ ตรวจสอบไฟล์

| ไฟล์ | SHA256 |
|---|---|
| `OpenThai2OCR-windows-x64.exe` | `e6629f02a085ede41f533a17c19b3093a6815921a6542cd29bf1072f17dac657` |
| `OpenThai2OCR-linux-x64` | `0b112aaa1ac9fb01f9e9f21015cc2759360d21a2abc6631f366e41a87f4eecad` |
| `OpenThai2OCR-macos-arm64` | `40c0320995ed29423fc364bbd89a2747415b76cfdd596d403d2c2a387625f2b7` |

### 🔗 ลิงก์
- คู่มือการใช้งาน: [docs/USAGE.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/USAGE.md)
- API reference (PHP/Python/JS/C#): [docs/API.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/docs/API.md)
- ประวัติเวอร์ชัน: [CHANGELOG.md](https://github.com/makerwitawat/OpenThai2OCR/blob/master/CHANGELOG.md)
- สัญญาอนุญาต: Apache-2.0 (โมเดล © iApp Technology)

### ⚠️ หมายเหตุ
- ไฟล์ onefile ต้องแตกไฟล์ลง temp ทุกครั้งที่เปิด จึงเปิดช้ากว่าแบบโฟลเดอร์เล็กน้อย (~2–3 วินาที)
- ในโหมดหน้าต่างโปรแกรม การดาวน์โหลดจะถามที่เก็บไฟล์ทุกครั้ง (พฤติกรรมของ WebView2)
- โมเดลนี้อ่านตัวพิมพ์เป็นหลัก ลายมืออ่านได้ไม่ดี
