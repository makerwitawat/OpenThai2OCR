# User Guide — OpenThai2.0 OCR

[ไทย](USAGE.md) | **English**

## 1. Start the app

| Mode | How |
|---|---|
| exe (Windows) | Double-click `OpenThai2OCR.exe`; the browser opens automatically |
| From source | `python app.py` (run `pip install -r requirements.txt` first) |
| Do not open a browser | add `--no-browser` |
| Change the port | `--port 8080` |
| Allow LAN access | `--host 0.0.0.0` (also allow the port in your firewall) |
| Use another model folder | `--model "D:\path\models"` |

> The single-file exe takes a few seconds on first launch because it extracts itself to a temp
> folder. This is normal.

## 2. Add an image

Four ways:

1. **Drag & drop** files onto the dashed box
2. **Click the box** and pick files (multiple selections allowed)
3. **Ctrl + V** — copy a screenshot (Snipaste / Print Screen / Snipping Tool) and paste on the page
4. **API** — send from another program (see [API.en.md](API.en.md))

Accepted: PNG, JPG/JPEG, BMP, TIF/TIFF, WEBP, PDF (every page).

### Watch folder

Instead of dropping files by hand, let the app watch a folder:

```bash
python app.py --watch "D:\inbox"                          # results -> D:\inbox\ocr-results
python app.py --watch "D:\inbox" --watch-out "D:\out"     # custom output folder
python app.py --watch "D:\inbox" --watch-interval 3       # poll every 3s (default 5)
```

- Each input yields `<stem>-ocr.txt`, `<stem>-ocr.docx`, `<stem>-ocr.json`
- Sources are **never moved or deleted**; a file is re-read only when its size/mtime changes
- Files still being copied are skipped until they stop changing

## 3. Read the result

- OCR starts automatically as soon as a file arrives
- Left = the image with line boxes and confidence scores (top-left of each box)
- Right = the text in reading order (2–3 column pages supported)
- Multiple files/pages → tabs below the image
- Buttons: **Copy** / **.txt** / **.docx** / **.pdf** / **.csv** / **.json**
  - `.pdf` = **searchable PDF** (an invisible text layer over the image)
  - `.docx` = Word document, one paragraph per line, editable
  - `.csv` = lines with confidence and box coordinates (opens in Excel)
  - `.json` = full result for downstream use
- **Lines** button — expands every line of the current page with its confidence;
  copy a single line, or **Copy all lines** for the whole page
- Multi-page PDFs: a progress bar ("Page x/y") and a **Cancel** button while reading

## 4. Accuracy tuning

### 4.1 Image scale (in the web UI)

The "Image scale" selector above the OCR button:

| Value | When to use |
|---|---|
| Auto | Normal-sized images (just leave it) |
| 1× | Already high resolution, want maximum speed |
| 1.5× | Smallish text |
| 2× | Small screenshots / tiny text — more accurate, slower |

### 4.2 Per-request settings (API `settings`)

```json
{
  "image_base64": "...",
  "settings": {
    "det": {"limit": 1600, "v_pad": 0.15, "split_gap": 1.2},
    "rec": {"drop_below": 0.8, "min_chars": 2, "color": "flatten"}
  }
}
```

| Key | Meaning | Safe range |
|---|---|---|
| `det.limit` | Longest side fed to the detector | 320–4096 (higher = more accurate, slower) |
| `det.v_pad` | Grow box height (helps Thai marks being clipped) | 0–1 |
| `det.split_gap` | Split lines merged across a gutter (fraction of line height) | 0–4 (0 = off) |
| `det.box_thresh` | Minimum box confidence | 0.1–0.99 |
| `rec.drop_below` | Drop lines below this confidence (stamps, seals) | 0–1 |
| `rec.min_chars` | Drop lines shorter than this | 0–50 |
| `rec.junk_below` / `rec.junk_invalid` | Drop low-confidence, badly-spelled lines | 0–1 |
| `rec.color` | Crop preparation: `flatten` (default), `gray`, `gray_inv`, `stretch`, `bgr` | — |

> Values are type-checked and clamped; invalid values are ignored (never crash).
> The same keys can be changed permanently in `models/config.json`.

### 4.3 Symptom → fix

| Symptom | Try |
|---|---|
| Small text misread | Scale 2× or `det.limit` 1600–2000 |
| Thai marks missing/shifted | `det.v_pad` 0.1–0.2 |
| Two columns merged into one line | `det.split_gap` 1.0–1.5 |
| Coloured text / dark background | `rec.color` = `flatten` (default) or `gray_inv` |
| Only high-confidence lines | `rec.drop_below` 0.85–0.92 |
| Too slow | Lower `det.limit` to ~960 or use 1× |

### 4.4 Limits

| Item | Default | Notes |
|---|---|---|
| Upload size | 100 MB | Larger files are rejected with a message |
| PDF pages | 50 | Split the file if you need more |
| Cached results | 5 | Used by the export buttons |
| Port | 5000-5010 | Shifts automatically when busy |
| Log file | `logs/openthai-ocr.log` | Rotating, 2 MB x 3 |

> In LAN mode (`--host 0.0.0.0`) without `--api-key`, a random key is generated and shown in a dialog.
> The web UI asks for it once, remembers it, and sends the `X-API-Key` header.

## 5. Page font size

- `A−` / `A` / `A+` at the top right — remembered for next time
- Default scale adapts to screen width automatically
- **EN / ไทย** button switches the UI language (remembered)
- **Quit** button (top right) stops the server - no Task Manager needed
- Version is shown at the top right

## 6. Using it from other programs (API)

Keep the app open, then call:

```bash
curl -F "file=@page.png" "http://127.0.0.1:5000/api/ocr"
```

See PHP / Python / JavaScript / C# / Java / Go / Ruby / PowerShell examples → [API.en.md](API.en.md)

## 7. Troubleshooting

| Problem | Cause / fix |
|---|---|
| Browser does not open | Visit `http://127.0.0.1:5000` manually; if the port is taken use `--port 8080` |
| "Windows protected your PC" | The exe is unsigned — More info → Run anyway |
| "Model files not found" | onedir builds need the `models` folder beside the exe (onefile embeds it) |
| Another machine cannot reach the API | Start with `--host 0.0.0.0` and allow the port in the firewall |
| Very slow | Lower the scale / `det.limit`; close CPU-heavy apps |
| Handwriting not recognised | This model targets printed text — use a VLM model for handwriting |
| Thai garbled in another program | Make sure your client decodes the response as UTF-8 |

## 8. Project layout

```
app.py                  Flask server + API + image handling
templates/index.html    Web UI (light theme, paste, multi-file, font scale)
models/                 ONNX models + runtime (line_engine.py, thai_norm.py)
docs/                   Guides, API, build docs (Thai + English)
tools/                  Helper scripts (model download, release notes, smoke test)
build_exe.bat           Windows one-file build
OpenThai2OCR.spec       PyInstaller onefile spec
```