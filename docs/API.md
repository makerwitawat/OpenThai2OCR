# API — OpenThai2.0 OCR

**ไทย** | [English](API.en.md)

เรียกใช้จากโปรแกรมอื่นได้ผ่าน HTTP JSON ทุกภาษา (PHP, Python, Node.js, C#, Java, Go, Ruby, PowerShell ฯลฯ)
เปิด CORS ให้ทุก origin แล้ว

## เปิดเซิร์ฟเวอร์

| วิธี | คำสั่ง |
|---|---|
| exe | ดับเบิลคลิก `OpenThai2OCR.exe` (หรือ `OpenThai2OCR.exe --port 5000`) |
| python | `python app.py` |
| ให้เครื่องอื่นใน LAN เรียกได้ | ตั้ง `--host 0.0.0.0` เช่น `python app.py --host 0.0.0.0 --port 5000` |
| เฝ้าโฟลเดอร์ (watch) | `python app.py --watch "D:\inbox"` (ดูหัวข้อ watch folder ด้านล่าง) |

ค่าเริ่มต้นฟังที่ `127.0.0.1:5000` (เครื่องตัวเองเท่านั้น)

## Endpoints

> หน้าเว็บในตัวมีคู่มือและตัวทดสอบ: `http://127.0.0.1:5000/docs` (สอนใช้งาน API) และ
> `http://127.0.0.1:5000/playground` (ยิงคำขอจริง ดู JSON/เวลา)

### `GET /api/health`

```json
{
  "ok": true,
  "app": "openthai2ocr",
  "version": "1.3.0",
  "uptime_s": 128.4,
  "model_dir": "D:\\...\\models",
  "model_ready": true,
  "auth_required": false,
  "watch": {"dir": null, "out": null, "interval": null},
  "limits": {"max_upload_mb": 100, "max_pages": 50}
}
```

### `GET /api/status`

สถานะละเอียดสำหรับหน้า `/status`: เพิ่ม `results_cached` และ `jobs` (20 งานล่าสุด)

```json
{
  "ok": true,
  "version": "1.3.0",
  "uptime_s": 128.4,
  "open_browser": true,
  "results_cached": 2,
  "jobs": [{"id": "ab12cd34", "name": "book.pdf", "status": "running",
            "progress": {"done": 5, "total": 12}, "error": "", "created": 1760000000.0}]
}
```

### `GET` / `POST /api/prefs`

อ่าน/บันทึกค่าตั้งของโปรแกรม (เก็บใน `settings.json` ข้าง exe)

```bash
curl -X POST http://127.0.0.1:5000/api/prefs \
  -H "Content-Type: application/json" -d '{"open_browser": false}'
```

| ฟิลด์ | ชนิด | คำอธิบาย |
|---|---|---|
| `open_browser` | bool | เปิดเบราว์เซอร์อัตโนมัติเมื่อเริ่มโปรแกรมครั้งถัดไป |

### `POST /api/ocr` — แนบไฟล์ (multipart, ชื่อ field = `file`)

```bash
curl -F "file=@page.png" "http://127.0.0.1:5000/api/ocr"
curl -F "file=@page.png" -F "scale=2" "http://127.0.0.1:5000/api/ocr?images=0"
```

### `POST /api/ocr` — JSON base64

```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgo...",
  "filename": "page.png",
  "images": false,
  "scale": "auto",
  "settings": {"rec": {"drop_below": 0.85}, "det": {"limit": 1600}}
}
```

| ฟิลด์ | ชนิด | คำอธิบาย |
|---|---|---|
| `image_base64` | string | รับทั้ง data URL และ base64 ล้วน (หรือใช้ `file_base64` ก็ได้) |
| `filename` | string | ใช้เดานามสกุลเมื่อไม่ได้ส่ง data URL |
| `images` | bool | `false` = ไม่คืนภาพผลลัพธ์ (เบากว่า) ค่าเริ่มต้น `true` |
| `scale` | number \| `"auto"` | ขยายภาพก่อนอ่าน: `auto` (ค่าเริ่มต้น), `1`, `1.5`, `2`… สูงสุด 4 |
| `settings` | object | ค่าปรับ engine ดูตารางด้านล่าง |

multipart ใส่ `images=0`, `scale=2`, `settings={"rec":{...}}` เป็นฟอร์มฟิลด์แทนได้

### รูปแบบผลลัพธ์

```json
{
  "ok": true,
  "text": "--- หน้า 1 ---\nข้อความทั้งหน้า...",
  "pages": [
    {
      "page": 1,
      "text": "ข้อความทั้งหน้า...",
      "n_lines": 12,
      "scale": 1.0,
      "rotation": 0,
      "text_angle": 0.0,
      "timing": {"det_ms": 76.2, "rec_ms": 15.4, "n_lines": 12},
      "lines": [
        {"text": "บรรทัดที่ 1", "confidence": 0.986, "row": 0,
         "box": [[10.0, 20.0], [300.0, 20.0], [300.0, 60.0], [10.0, 60.0]],
         "words": [{"text": "บรรทัดที่", "confidence": 0.99, "box": [[0,0],[0,0],[0,0],[0,0]]}]}
      ],
      "image": "<base64 PNG ที่วาดกล่องข้อความ>"
    }
  ]
}
```

- `lines[].box` เป็นพิกัดในภาพที่ประมวลผล (หลังขยายตาม `scale` แล้ว)
- `rotation` = 0/90/180/270 (องศาที่ระบบหมุนหน้าอัตโนมัติ)
- `timing.det_ms` / `rec_ms` = เวลาตรวจจับ/อ่าน (มิลลิวินาที)

### ค่าปรับใน `settings`

| คีย์ | ความหมาย | ช่วง |
|---|---|---|
| `det.limit` | ขนาดยาวสุดที่ detector ย่อไปประมวลผล | 320–4096 |
| `det.v_pad` | ขยายความสูงกรอบ (ช่วยวรรณยุกต์ไทย) | 0–1 |
| `det.split_gap` | ตัดบรรทัดที่ merge ข้ามคอลัมน์ | 0–4 |
| `det.box_thresh` | ความมั่นใจขั้นต่ำของกรอบ | 0.1–0.99 |
| `rec.drop_below` | ตัดบรรทัดความมั่นใจต่ำ | 0–1 |
| `rec.min_chars` | ตัดบรรทัดสั้นเกิน | 0–50 |
| `rec.junk_below`, `rec.junk_invalid` | ตัดข้อความขยะ/สะกดเพี้ยน | 0–1 |
| `rec.batch` | จำนวนบรรทัดต่อรอบ | 1–64 |
| `rec.color` | `flatten` (ค่าเริ่มต้น), `gray`, `gray_inv`, `stretch`, `bgr` | — |

### `POST /api/jobs` — งานเบื้องหลัง (มี progress + ยกเลิก)

ใช้เมื่อไฟล์เป็น PDF หลายหน้า หรืออยากให้หน้าเว็บแสดงความคืบหน้า
รับ payload เหมือน `/api/ocr` ทุกอย่าง (multipart หรือ JSON base64)

```json
{"ok": true, "job_id": "06ee616b67186519", "total": 3}
```

### `GET /api/jobs/<job_id>`

```json
{"ok": true, "job_id": "...", "status": "running",
 "progress": {"done": 1, "total": 3}, "error": ""}
```

`status`: `queued` → `running` → `done` | `error` | `cancelled`
เมื่อ `done` จะมี `pages`, `text`, `result_id` ให้ใช้ต่อได้

### `POST /api/jobs/<job_id>/cancel`

```json
{"ok": true}
```

ยกเลิกระหว่างอ่านได้ (หยุดที่ขอบเขตหน้าถัดไป)

### `GET /api/result/<result_id>/export?format=pdf|csv|json|txt|docx`

ดาวน์โหลดผลลัพธ์ (เก็บผลล่าสุด 5 รายการ)

- `pdf` = PDF ที่ค้นหาข้อความได้ (text layer ซ่อนเหนือภาพ)
- `csv` = บรรทัด + confidence + พิกัดกรอบ (UTF-8 BOM เปิด Excel ได้)
- `json` = ผลเต็ม (ไม่มีภาพประกอบ)
- `txt` = ข้อความล้วน
- `docx` = Word — บรรทัดละย่อหน้า ฟอนต์ Leelawadee UI (แก้ไขต่อได้ทันที)

```bash
curl -o result.pdf "http://127.0.0.1:5000/api/result/<id>/export?format=pdf"
```

### `POST /api/shutdown`

ปิดโปรแกรมจากเครื่องตัวเองเท่านั้น (ใช้โดยปุ่ม "ปิดโปรแกรม" ในหน้าเว็บ)

### watch folder (เฝ้าโฟลเดอร์)

เปิดด้วย `--watch <โฟลเดอร์>` — โปรแกรมจะตรวจไฟล์ใหม่ (หรือไฟล์ที่ถูกแก้) ทุก ๆ
`--watch-interval` วินาที (ค่าเริ่มต้น 5) แล้วอ่านให้อัตโนมัติ

| ธง | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `--watch DIR` | (ปิด) | โฟลเดอร์ที่เฝ้า |
| `--watch-out DIR` | `<DIR>/ocr-results` | โฟลเดอร์เก็บผลลัพธ์ |
| `--watch-interval SEC` | `5` | ตรวจทุกกี่วินาที (ต่ำสุด 1) |

ผลที่ได้ต่อไฟล์: `<ชื่อไฟล์>-ocr.txt`, `<ชื่อไฟล์>-ocr.docx`, `<ชื่อไฟล์>-ocr.json`
ไฟล์ต้นฉบับไม่ถูกย้าย/ลบ และไฟล์เดิมจะถูกอ่านซ้ำก็ต่อเมื่อขนาด/เวลาแก้เปลี่ยน
สถานะ watch ดูได้จาก `/api/health` (`watch`)

```bash
python app.py --watch "D:\inbox" --watch-out "D:\out" --watch-interval 3 --no-browser
```

### Authentication (เมื่อเปิด `--api-key`)

ส่ง header `X-API-Key: <key>` (หรือ `?key=<key>`) กับทุก `/api/*`
ยกเว้น `/api/health`, `/`, `/favicon.ico`

```bash
curl -H "X-API-Key: secret123" -F "file=@page.png" http://127.0.0.1:5000/api/ocr
```

### ขีดจำกัด

| รายการ | ค่า |
|---|---|
| ขนาดอัปโหลด | 100 MB (`413`) |
| จำนวนหน้า PDF | 50 (`400`) |
| ผลลัพธ์ที่เก็บ | 5 รายการ (เกินแล้วให้ประมวลผลใหม่) |
| การประมวลผล | ทีละคำขอ (คำขออื่นเข้าคิว) |

## ตัวอย่าง PHP

```php
<?php
// ---- วิธีที่ 1: แนบไฟล์ (multipart) ----
$ch = curl_init('http://127.0.0.1:5000/api/ocr');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => ['file' => new CURLFile('C:/scan/page.jpg')],
    CURLOPT_TIMEOUT        => 120,
]);
$res = json_decode(curl_exec($ch), true);
if (!empty($res['ok'])) {
    echo $res['text'];
} else {
    http_response_code(500);
    echo 'ผิดพลาด: ' . ($res['error'] ?? 'ไม่ทราบสาเหตุ');
}

// ---- วิธีที่ 2: ส่ง base64 (เช่นได้มาจาก upload หรือ canvas) ----
$b64 = base64_encode(file_get_contents('C:/scan/page.jpg'));
$payload = json_encode(['image_base64' => $b64, 'filename' => 'page.jpg', 'images' => false]);
$ch = curl_init('http://127.0.0.1:5000/api/ocr');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $payload,
    CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
    CURLOPT_TIMEOUT        => 120,
]);
$res = json_decode(curl_exec($ch), true);
echo $res['text'] ?? $res['error'];
```

## ตัวอย่าง Python

```python
import base64, json, urllib.request

data = base64.b64encode(open("page.png", "rb").read()).decode()
body = json.dumps({"image_base64": data, "images": False, "scale": 2}).encode()
req = urllib.request.Request("http://127.0.0.1:5000/api/ocr", data=body,
                             headers={"Content-Type": "application/json"})
out = json.loads(urllib.request.urlopen(req).read())
print(out["text"])
```

## ตัวอย่าง JavaScript (เบราว์เซอร์ / Node 18+)

```js
const r = await fetch("http://127.0.0.1:5000/api/ocr", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ image_base64: dataUrl, images: false, scale: 2 }),
});
const j = await r.json();
console.log(j.ok ? j.text : j.error);
```

## ตัวอย่าง C# (.NET)

```csharp
using var http = new HttpClient { Timeout = TimeSpan.FromMinutes(2) };
using var form = new MultipartFormDataContent();
form.Add(new ByteArrayContent(File.ReadAllBytes("page.png")), "file", "page.png");
form.Add(new StringContent("2"), "scale");
form.Add(new StringContent("0"), "images");
var msg = await http.PostAsync("http://127.0.0.1:5000/api/ocr", form);
var json = await msg.Content.ReadAsStringAsync();
```

## ตัวอย่าง Java 11+

```java
import java.net.URI;
import java.net.http.*;
import java.nio.file.*;
import java.util.Base64;

String b64 = Base64.getEncoder().encodeToString(Files.readAllBytes(Path.of("page.png")));
String body = "{\"image_base64\":\"" + b64 + "\",\"filename\":\"page.png\",\"images\":false}";
HttpRequest req = HttpRequest.newBuilder(URI.create("http://127.0.0.1:5000/api/ocr"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(body))
    .timeout(java.time.Duration.ofMinutes(2))
    .build();
HttpResponse<String> res = HttpClient.newHttpClient().send(req, HttpResponse.BodyHandlers.ofString());
System.out.println(res.body());
```

## ตัวอย่าง Go

```go
package main

import (
    "bytes"
    "fmt"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

func main() {
    var buf bytes.Buffer
    w := multipart.NewWriter(&buf)
    f, _ := os.Open("page.png")
    defer f.Close()
    part, _ := w.CreateFormFile("file", "page.png")
    io.Copy(part, f)
    w.WriteField("images", "0")
    w.WriteField("scale", "2")
    w.Close()

    req, _ := http.NewRequest("POST", "http://127.0.0.1:5000/api/ocr", &buf)
    req.Header.Set("Content-Type", w.FormDataContentType())
    res, err := http.DefaultClient.Do(req)
    if err != nil {
        panic(err)
    }
    defer res.Body.Close()
    out, _ := io.ReadAll(res.Body)
    fmt.Println(string(out))
}
```

## ตัวอย่าง Ruby

```ruby
require "net/http"
require "json"
require "base64"

b64 = Base64.strict_encode64(File.binread("page.png"))
uri = URI("http://127.0.0.1:5000/api/ocr")
req = Net::HTTP::Post.new(uri, "Content-Type" => "application/json")
req.body = { image_base64: b64, filename: "page.png", images: false }.to_json
res = Net::HTTP.start(uri.hostname, uri.port, read_timeout: 120) { |h| h.request(req) }
puts JSON.parse(res.body)["text"]
```

## ตัวอย่าง PowerShell

```powershell
# PowerShell 7+
$j = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/ocr" -Method Post -Form @{
    file   = Get-Item "page.png"
    scale  = "2"
    images = "0"
}
$j.text
```

> PowerShell 5.1 ไม่มี `-Form` — ใช้ `curl.exe -F "file=@page.png" ...` แทน

## ข้อควรรู้

- PDF ถูกแปลงทุกหน้าและอ่านทีละหน้า (ผลแยกตาม `pages[].page`)
- นามสกุลที่รับ: png, jpg/jpeg, bmp, tif/tiff, webp, pdf
- เปิด `--host 0.0.0.0` แล้วเครื่องใน LAN ใช้ `http://<IP-ของเครื่องนี้>:5000` ได้ — อย่าเปิดสู่อินเทอร์เน็ตโดยไม่มี auth/ไฟร์วอลล์
- โปรแกรมประมวลผลทีละคำขอ (มี lock ภายใน) — ส่งพร้อมกันหลายคำขอจะเข้าคิวอัตโนมัติ