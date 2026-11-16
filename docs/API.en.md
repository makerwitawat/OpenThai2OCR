# API — OpenThai2.0 OCR

[ไทย](API.md) | **English**

Call it from any language over HTTP JSON (PHP, Python, Node.js, C#, Java, Go, Ruby, PowerShell …).
CORS is open for every origin.

## Start the server

| Mode | Command |
|---|---|
| exe | double-click `OpenThai2OCR.exe` (or `OpenThai2OCR.exe --port 5000`) |
| python | `python app.py` |
| LAN access | add `--host 0.0.0.0`, e.g. `python app.py --host 0.0.0.0 --port 5000` |
| Watch a folder | `python app.py --watch "D:\inbox"` (see the watch folder section below) |

It listens on `127.0.0.1:5000` by default (this machine only).

## Endpoints

> The app ships with a guide and a live tester: `http://127.0.0.1:5000/docs` (API guide) and
> `http://127.0.0.1:5000/playground` (send real requests, inspect JSON/timing).

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

Full status for `/status`: adds `results_cached` and `jobs` (last 20)

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

Read/save app preferences (stored in `settings.json` next to the exe)

```bash
curl -X POST http://127.0.0.1:5000/api/prefs \
  -H "Content-Type: application/json" -d '{"open_browser": false}'
```

| Field | Type | Description |
|---|---|---|
| `start_mode` | string | `window` (app window) · `browser` · `none` — applies on the next start |
| `open_browser` | bool | Legacy: `true` = `browser`, `false` = `none` |
| `update_check` | bool | Turn the GitHub new-version check on/off (default `true`) — can be sent without `start_mode` |

### `POST /api/ocr` — file upload (multipart, field name `file`)

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

| Field | Type | Description |
|---|---|---|
| `image_base64` | string | data URL or bare base64 (`file_base64` also accepted) |
| `filename` | string | used to infer the extension when no data URL |
| `images` | bool | `false` = omit annotated images (smaller response), default `true` |
| `overlay` | bool | `false` = return a plain image without baked-in boxes/confidence (draw your own from `lines[].box` + `size`), default `true` |
| `scale` | number \| `"auto"` | upscale before OCR: `auto` (default), `1`, `1.5`, `2` … max 4 |
| `settings` | object | engine overrides, see the table below |

For multipart, send `images=0`, `scale=2`, `settings={"rec":{...}}` as form fields instead.

### Response

```json
{
  "ok": true,
  "text": "--- page 1 ---\nthe whole page text...",
  "pages": [
    {
      "page": 1,
      "text": "the whole page text...",
      "n_lines": 12,
      "scale": 1.0,
      "rotation": 0,
      "text_angle": 0.0,
      "timing": {"det_ms": 76.2, "rec_ms": 15.4, "n_lines": 12},
      "lines": [
        {"text": "line one", "confidence": 0.986, "row": 0,
         "box": [[10.0, 20.0], [300.0, 20.0], [300.0, 60.0], [10.0, 60.0]],
         "words": [{"text": "line", "confidence": 0.99, "box": [[0,0],[0,0],[0,0],[0,0]]}]}
      ],
      "image": "<base64 PNG with boxes drawn>"
    }
  ]
}
```

- `lines[].box` coordinates are in the processed image (after `scale`)
- `size` = `[width, height]` of the processed image (use it as the viewBox when drawing boxes over the image)
- `rotation` = 0/90/180/270 (auto page rotation)
- `timing.det_ms` / `rec_ms` = detection / recognition milliseconds

### `settings` keys

| Key | Meaning | Range |
|---|---|---|
| `det.limit` | longest side fed to the detector | 320–4096 |
| `det.v_pad` | grow box height (Thai marks) | 0–1 |
| `det.split_gap` | split lines merged across a gutter | 0–4 |
| `det.box_thresh` | minimum box confidence | 0.1–0.99 |
| `rec.drop_below` | drop lines under this confidence | 0–1 |
| `rec.min_chars` | drop too-short lines | 0–50 |
| `rec.junk_below`, `rec.junk_invalid` | drop junk / badly spelled lines | 0–1 |
| `rec.batch` | lines per forward pass | 1–64 |
| `rec.color` | `flatten` (default), `gray`, `gray_inv`, `stretch`, `bgr` | — |

### `POST /api/jobs` — background job (progress + cancel)

Use this for multi-page PDFs or when you want progress reporting.
It accepts the same payloads as `/api/ocr` (multipart or JSON base64).

```json
{"ok": true, "job_id": "06ee616b67186519", "total": 3}
```

### `GET /api/jobs/<job_id>`

```json
{"ok": true, "job_id": "...", "status": "running",
 "progress": {"done": 1, "total": 3}, "error": ""}
```

`status`: `queued` -> `running` -> `done` | `error` | `cancelled`
When `done`, the response includes `pages`, `text`, and `result_id`.

### `POST /api/jobs/<job_id>/cancel`

```json
{"ok": true}
```

Stops between pages.

### `GET /api/result/<result_id>/export?format=pdf|csv|json|txt|docx`

Downloads the result (the last 5 results are kept).

- `pdf` = searchable PDF (invisible text layer over the image)
- `csv` = lines + confidence + box coordinates (UTF-8 BOM, opens in Excel)
- `json` = full result (no images)
- `txt` = plain text
- `docx` = Word document, one paragraph per line, Leelawadee UI font (editable)

```bash
curl -o result.pdf "http://127.0.0.1:5000/api/result/<id>/export?format=pdf"
```

#### Export with edited text — `POST /api/result/<result_id>/export?format=...`

Send JSON `{"text": "..."}` so the exported file uses your corrected text instead of the raw OCR output
(no `text`, or `GET` = the original result · the result stored on the server is never modified)

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": "corrected line\nanother line"}' \
  -o fixed.pdf "http://127.0.0.1:5000/api/result/<id>/export?format=pdf"
```

- `=== file name ===` and `--- Page N ---` header lines are stripped automatically; use `--- Page N ---` to separate pages of a multi-page PDF
- `txt`/`json` use the text as sent · `docx` gets one paragraph per line
- `pdf`/`csv`: if the line count equals the original row count, each line is placed on its row's box; otherwise lines are spread vertically inside the original text area
- `text` is limited to 2,000,000 characters (more = `413`) · a non-string value = `400`

### `GET /api/update-check`

Asks the server to look up the latest version on GitHub Releases (cached 6 h, 5 s timeout, offline = no error).
Add `?force=1` to bypass the cache.

```json
{"ok": true, "enabled": true, "current": "1.4.0", "latest": "1.4.0",
 "update_available": false, "url": "https://github.com/makerwitawat/OpenThai2OCR/releases/tag/v1.4.0",
 "error": null}
```

Turn it off with `POST /api/prefs {"update_check": false}` — the check only talks to GitHub; none of your files or text are sent.

### `POST /api/shutdown`

Stops the app, localhost only (used by the web UI "Quit" button).

### Watch folder

Start with `--watch <dir>` — new or changed files are OCR'd every
`--watch-interval` seconds (default 5).

| Flag | Default | Meaning |
|---|---|---|
| `--watch DIR` | (off) | folder to watch |
| `--watch-out DIR` | `<DIR>/ocr-results` | where results are written |
| `--watch-interval SEC` | `5` | poll interval (minimum 1) |

Each input produces `<stem>-ocr.txt`, `<stem>-ocr.docx`, `<stem>-ocr.json`.
Sources are never moved or deleted, and a file is re-read only when its size or
mtime changes. Watch status is exposed by `/api/health` (`watch`).

```bash
python app.py --watch "D:\inbox" --watch-out "D:\out" --watch-interval 3 --no-browser
```

### Authentication (when `--api-key` is set)

Send `X-API-Key: <key>` (or `?key=<key>`) on every `/api/*` call,
except `/api/health`, `/`, and `/favicon.ico`.

```bash
curl -H "X-API-Key: secret123" -F "file=@page.png" http://127.0.0.1:5000/api/ocr
```

### Limits

| Item | Value |
|---|---|
| Upload size | 100 MB (`413`) |
| PDF pages | 50 (`400`) |
| Cached results | 5 (re-run when exceeded) |
| Processing | one request at a time (others queue) |

## PHP

```php
<?php
// 1) multipart upload
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
    echo 'error: ' . ($res['error'] ?? 'unknown');
}

// 2) base64 JSON (from an upload or a canvas)
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

## Python

```python
import base64, json, urllib.request

data = base64.b64encode(open("page.png", "rb").read()).decode()
body = json.dumps({"image_base64": data, "images": False, "scale": 2}).encode()
req = urllib.request.Request("http://127.0.0.1:5000/api/ocr", data=body,
                             headers={"Content-Type": "application/json"})
out = json.loads(urllib.request.urlopen(req).read())
print(out["text"])

# or with requests:
# r = requests.post("http://127.0.0.1:5000/api/ocr", files={"file": open("page.png", "rb")},
#                   data={"scale": "2", "images": "0"})
# print(r.json()["text"])
```

## Node.js (18+)

```js
import { readFile } from "node:fs/promises";

const form = new FormData();
form.append("file", new Blob([await readFile("page.png")]), "page.png");
form.append("scale", "2");
form.append("images", "0");

const r = await fetch("http://127.0.0.1:5000/api/ocr", { method: "POST", body: form });
const j = await r.json();
console.log(j.ok ? j.text : j.error);
```

## C# (.NET)

```csharp
using var http = new HttpClient { Timeout = TimeSpan.FromMinutes(2) };
using var form = new MultipartFormDataContent();
form.Add(new ByteArrayContent(await File.ReadAllBytesAsync("page.png")), "file", "page.png");
form.Add(new StringContent("2"), "scale");
form.Add(new StringContent("0"), "images");
var res = await http.PostAsync("http://127.0.0.1:5000/api/ocr", form);
var json = JsonDocument.Parse(await res.Content.ReadAsStringAsync());
Console.WriteLine(json.RootElement.GetProperty("text").GetString());
```

## Java 11+

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

## Go

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

## Ruby

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

## PowerShell

```powershell
# PowerShell 7+
$j = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/ocr" -Method Post -Form @{
    file   = Get-Item "page.png"
    scale  = "2"
    images = "0"
}
$j.text
```

> PowerShell 5.1 has no `-Form`; use `curl.exe -F "file=@page.png" ...` instead.

## Notes

- A PDF is rendered page by page; results are split by `pages[].page`
- Accepted extensions: png, jpg/jpeg, bmp, tif/tiff, webp, pdf
- With `--host 0.0.0.0` other machines can use `http://<this-machine-ip>:5000` — never expose it to
  the internet without authentication and a firewall
- Requests are processed one at a time (internal lock); concurrent calls queue automatically