# -*- coding: utf-8 -*-
"""OpenThai2.0-OCR-Text: web UI (Flask) + OCR engine, buildable with PyInstaller."""
import base64
import csv
import io
import json
import logging
import os
import queue
import secrets
import socket
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
import webbrowser
from collections import OrderedDict
from logging.handlers import RotatingFileHandler
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request, send_file

APP_NAME = "openthai2ocr"
APP_VERSION = "1.1.0"

BASE = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
BUNDLE = Path(getattr(sys, "_MEIPASS", BASE)) if getattr(sys, "frozen", False) else BASE


def _resolve_model_dir() -> Path:
    embedded = BUNDLE / "models"
    if (embedded / "det.onnx").exists():
        return embedded
    return BASE / "models"


def asset_path(name: str) -> Path:
    for candidate in (BUNDLE / "assets" / name, BASE / "assets" / name, BUNDLE / name, BASE / name):
        if candidate.exists():
            return candidate
    return BUNDLE / "assets" / name


MODEL_DIR = _resolve_model_dir()
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".pdf"}
MAX_CONTENT_MB = 100
MAX_PAGES = 50
RESULT_KEEP = 5
LOG_DIR = BASE / "logs"
PORT = 5000
API_KEY = ""
log = logging.getLogger(APP_NAME)


def setup_logging(level: str = "INFO") -> Path | None:
    log.setLevel(getattr(logging, level.upper(), logging.INFO))
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    target = LOG_DIR
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError:
        target = Path(os.environ.get("TEMP", ".")) / "openthai-ocr-logs"
        target.mkdir(parents=True, exist_ok=True)
    path = target / "openthai-ocr.log"
    handler = RotatingFileHandler(path, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
    handler.setFormatter(fmt)
    log.addHandler(handler)
    stream = logging.StreamHandler(sys.stderr)
    stream.setFormatter(fmt)
    log.addHandler(stream)
    log.info("start %s v%s (frozen=%s)", APP_NAME, APP_VERSION, getattr(sys, "frozen", False))
    return path


app = Flask(__name__)
app.json.ensure_ascii = False
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024
if getattr(sys, "frozen", False):
    app.template_folder = str(BUNDLE / "templates")

_engine = None
_engine_lock = threading.Lock()
_ocr_lock = threading.Lock()


def get_engine():
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                sys.path.insert(0, str(BASE))
                from models.runtime.line_engine import LineOCR
                _engine = LineOCR(str(MODEL_DIR), threads=2)
                log.info("engine ready: %s", MODEL_DIR)
    return _engine


# ---------------------------------------------------------------- image utils
def pdf_to_images(data: bytes, zoom: float = 1.6, max_pages: int = MAX_PAGES):
    import pymupdf as fitz

    doc = fitz.open(stream=data, filetype="pdf")
    total = doc.page_count
    if total > max_pages:
        raise ValueError(f"PDF มี {total} หน้า เกินขีดจำกัด {max_pages} หน้า")
    images, mat = [], fitz.Matrix(zoom, zoom)
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif pix.n == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        images.append(np.ascontiguousarray(img))
    return images


def pdf_page_count(data: bytes) -> int:
    import pymupdf as fitz

    return fitz.open(stream=data, filetype="pdf").page_count


def decode_image(data: bytes) -> np.ndarray:
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("decode image bytes failed")
    return img


def annotate_image(img: np.ndarray, lines: list[dict], max_width: int = 1200) -> str:
    img = img.copy()
    for ln in lines:
        box = np.array(ln["box"], dtype=np.int32)
        cv2.polylines(img, [box], True, (0, 180, 0), 2)
        x0, y0 = int(box[:, 0].min()), int(box[:, 1].min())
        cv2.putText(img, f"{ln['confidence']:.2f}", (x0, max(14, y0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 220), 1, cv2.LINE_AA)
    h, w = img.shape[:2]
    if w > max_width:
        img = cv2.resize(img, (max_width, max(1, int(round(h * max_width / w)))), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".png", img)
    return base64.b64encode(buf.tobytes()).decode("ascii")


_ocr_lock = threading.Lock()
_SETTING_TYPES = {
    ("det", "limit"): (int, 320, 4096),
    ("det", "v_pad"): (float, 0.0, 1.0),
    ("det", "split_gap"): (float, 0.0, 4.0),
    ("det", "box_thresh"): (float, 0.1, 0.99),
    ("rec", "drop_below"): (float, 0.0, 1.0),
    ("rec", "min_chars"): (int, 0, 50),
    ("rec", "junk_below"): (float, 0.0, 1.0),
    ("rec", "junk_invalid"): (float, 0.0, 1.0),
    ("rec", "batch"): (int, 1, 64),
}


def _sanitize_settings(raw) -> dict:
    out: dict[str, dict] = {}
    if not isinstance(raw, dict):
        return out
    for sec, vals in raw.items():
        if not isinstance(vals, dict):
            continue
        for key, value in vals.items():
            spec = _SETTING_TYPES.get((sec, key))
            try:
                if spec:
                    typ, lo, hi = spec
                    v = typ(value)
                    if lo <= v <= hi:
                        out.setdefault(sec, {})[key] = v
                elif (sec, key) == ("rec", "color") and value in ("bgr", "gray", "gray_inv", "stretch", "flatten"):
                    out.setdefault(sec, {})[key] = value
            except (TypeError, ValueError, OverflowError):
                continue
    return out


class _engine_settings:
    def __init__(self, engine, overrides: dict):
        self.engine, self.overrides, self.saved = engine, overrides, {}

    def __enter__(self):
        for sec, vals in self.overrides.items():
            target = self.engine.cfg.get(sec)
            if not isinstance(target, dict):
                continue
            for k, v in vals.items():
                if k in target:
                    self.saved.setdefault(sec, {})[k] = target[k]
                    target[k] = v
        return self.engine

    def __exit__(self, *exc):
        for sec, vals in self.saved.items():
            self.engine.cfg[sec].update(vals)
        return False


def _auto_scale(img: np.ndarray, requested) -> float:
    if isinstance(requested, (int, float)) and requested:
        return max(0.5, min(4.0, float(requested)))
    long_side = max(img.shape[:2])
    return 1.0 if long_side >= 1200 else round(max(1.0, min(2.5, 1600.0 / max(long_side, 1))), 2)


def _resize(img: np.ndarray, scale: float) -> np.ndarray:
    if abs(scale - 1.0) < 0.01:
        return img
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


def read_image(img: np.ndarray, want_image: bool, scale_requested=None, settings=None) -> dict:
    engine = get_engine()
    scale = _auto_scale(img, scale_requested)
    if scale != 1.0:
        img = _resize(img, scale)
    with _ocr_lock, _engine_settings(engine, _sanitize_settings(settings)):
        result = engine.read(img)
    result["scale"] = scale
    if want_image:
        result["image"] = annotate_image(img, result["lines"])
    return result


# ---------------------------------------------------------------- results cache
_results: "OrderedDict[str, dict]" = OrderedDict()
_results_lock = threading.Lock()


def _cache_result(result_id: str, ext: str, source: bytes, name: str, pages: list[dict], text: str):
    slim = [{k: v for k, v in p.items() if k != "image"} for p in pages]
    entry = {"ext": ext, "source": source, "name": name, "pages": slim,
             "text": text, "created": time.time(), "version": APP_VERSION}
    with _results_lock:
        _results[result_id] = entry
        _results.move_to_end(result_id)
        while len(_results) > RESULT_KEEP:
            _results.popitem(last=False)


def _get_result(result_id: str):
    with _results_lock:
        entry = _results.get(result_id)
        if entry:
            _results.move_to_end(result_id)
        return entry


# ---------------------------------------------------------------- analysis
def _analyze(ext: str, raw: bytes, options: dict, images_by_page=None):
    """Run OCR over all pages. images_by_page (list[np.ndarray]) pre-renders PDFs."""
    want_images = options.get("want_images", True)
    scale = options.get("scale")
    settings = options.get("settings")
    if ext == ".pdf":
        images = images_by_page if images_by_page is not None else pdf_to_images(raw)
    else:
        images = [decode_image(raw)]
    pages = []
    for i, img in enumerate(images):
        r = read_image(img, want_images, scale_requested=scale, settings=settings)
        r["page"] = i + 1
        r["n_lines"] = len(r["lines"])
        pages.append(r)
    text_all = "\n\n".join(f"--- หน้า {p['page']} ---\n{p['text']}" for p in pages if p["text"]).lstrip()
    return pages, text_all


# ---------------------------------------------------------------- jobs (progress/cancel)
class Job:
    def __init__(self, ext: str, raw: bytes, options: dict, name: str, total: int):
        self.id = secrets.token_hex(8)
        self.ext, self.raw, self.options, self.name = ext, raw, options, name
        self.status = "queued"
        self.progress = {"done": 0, "total": total}
        self.error = ""
        self.text = ""
        self.pages: list[dict] = []
        self.cancel = threading.Event()
        self.created = time.time()

    def snapshot(self, include_pages: bool) -> dict:
        out = {"ok": True, "job_id": self.id, "status": self.status,
               "progress": self.progress, "error": self.error}
        if self.status == "done" and include_pages:
            out.update(text=self.text, pages=self.pages, result_id=self.id)
        return out


_jobs: dict[str, Job] = {}
_jobs_lock = threading.Lock()
_job_queue: "queue.Queue[Job]" = queue.Queue()
_worker_started = False


def _ensure_worker():
    global _worker_started
    with _jobs_lock:
        if _worker_started:
            return
        t = threading.Thread(target=_job_worker, name="ocr-worker", daemon=True)
        t.start()
        _worker_started = True


def _job_worker():
    while True:
        job = _job_queue.get()
        with _jobs_lock:
            if job.cancel.is_set():
                job.status = "cancelled"
                continue
            job.status = "running"
        try:
            if job.ext == ".pdf":
                images = pdf_to_images(job.raw)
                job.progress["total"] = len(images)
            else:
                images = [decode_image(job.raw)]
            pages = []
            for i, img in enumerate(images):
                if job.cancel.is_set():
                    job.status = "cancelled"
                    break
                r = read_image(img, job.options.get("want_images", True),
                               scale_requested=job.options.get("scale"),
                               settings=job.options.get("settings"))
                r["page"] = i + 1
                r["n_lines"] = len(r["lines"])
                pages.append(r)
                job.progress["done"] = i + 1
            if job.status != "cancelled":
                job.pages = pages
                job.text = "\n\n".join(f"--- หน้า {p['page']} ---\n{p['text']}" for p in pages if p["text"]).lstrip()
                job.status = "done"
                _cache_result(job.id, job.ext, job.raw, job.name, pages, job.text)
        except Exception:
            job.status = "error"
            job.error = traceback.format_exc(limit=3).splitlines()[-1]
            log.exception("job %s failed", job.id)


def _prune_jobs():
    now = time.time()
    with _jobs_lock:
        stale = [k for k, v in _jobs.items() if now - v.created > 3600]
        for k in stale:
            _jobs.pop(k, None)


# ---------------------------------------------------------------- auth / cors
def _is_local() -> bool:
    return request.remote_addr in ("127.0.0.1", "::1")


def _auth_ok() -> bool:
    if not API_KEY:
        return True
    supplied = request.headers.get("X-API-Key") or request.args.get("key", "")
    return secrets.compare_digest(supplied, API_KEY)


@app.before_request
def _guard():
    if not API_KEY:
        return None
    path = request.path
    if path == "/" or path == "/favicon.ico" or path == "/api/health":
        return None
    if path == "/api/shutdown":
        return None if _is_local() else (jsonify({"ok": False, "error": "ปิดได้จากเครื่องนี้เท่านั้น"}), 403)
    if path.startswith("/api/") and not _auth_ok():
        return jsonify({"ok": False, "error": "ต้องระบุ API key (header X-API-Key)", "auth_required": True}), 401
    return None


@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp


@app.errorhandler(413)
def too_large(_e):
    return jsonify({"ok": False, "error": f"ไฟล์ใหญ่เกิน {MAX_CONTENT_MB} MB"}), 413


# ---------------------------------------------------------------- routes
@app.get("/")
def index():
    return render_template("index.html", version=APP_VERSION, auth_required=bool(API_KEY), max_pages=MAX_PAGES)


@app.get("/favicon.ico")
def favicon():
    path = asset_path("app.ico")
    if path.exists():
        return send_file(path, mimetype="image/x-icon")
    return ("", 404)


@app.get("/api/health")
def api_health():
    return jsonify({"ok": True, "app": APP_NAME, "version": APP_VERSION,
                    "model_dir": str(MODEL_DIR),
                    "model_ready": all((MODEL_DIR / n).exists() for n in ("det.onnx", "rec.onnx", "rec_dict.txt", "config.json")),
                    "auth_required": bool(API_KEY),
                    "limits": {"max_upload_mb": MAX_CONTENT_MB, "max_pages": MAX_PAGES}})


@app.post("/api/shutdown")
def api_shutdown():
    if not _is_local():
        return jsonify({"ok": False, "error": "ปิดได้จากเครื่องนี้เท่านั้น"}), 403
    log.info("shutdown requested via UI")
    threading.Timer(0.4, lambda: os._exit(0)).start()
    return jsonify({"ok": True, "message": "กำลังปิดโปรแกรม…"})


def _ext_from_mime(mime: str) -> str:
    return {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg",
            "image/bmp": ".bmp", "image/tiff": ".tif", "image/webp": ".webp"}.get(mime, ".png")


def _payload_from_request():
    form = request.form if request.form else (request.get_json(silent=True) or {})
    if request.files.get("file") is not None:
        f = request.files["file"]
        ext, raw, name = Path(f.filename or "").suffix.lower(), f.read(), f.filename or "upload"
    else:
        body = request.get_json(silent=True) or {}
        b64 = body.get("image_base64") or body.get("file_base64") or ""
        if not b64:
            return None, "", "upload", {}
        ext = Path(body.get("filename", "")).suffix.lower()
        if b64.startswith("data:") and ";base64," in b64:
            ext = _ext_from_mime(b64[5:b64.index(";")])
            b64 = b64.split(",", 1)[1]
        raw, name = base64.b64decode(b64), body.get("filename", "upload")
        ext = ext or ".png"
    opts = {"want_images": str(form.get("images", "1")) not in ("0", "false", "False")}
    scale = form.get("scale")
    if scale not in (None, "", "auto"):
        try:
            opts["scale"] = float(scale)
        except (TypeError, ValueError):
            pass
    settings = form.get("settings")
    if isinstance(settings, str) and settings.strip():
        try:
            settings = json.loads(settings)
        except ValueError:
            settings = None
    elif not isinstance(settings, dict):
        settings = None
    if settings:
        opts["settings"] = settings
    return raw, ext, name, opts


def _validate(raw, ext):
    if not raw:
        return "ไม่พบไฟล์ (แนบ multipart ชื่อ file หรือ JSON image_base64)"
    if ext not in ALLOWED_EXT:
        return f"นามสกุล {ext or '(ไม่มี)'} ไม่รองรับ"
    return None


@app.post("/api/ocr")
def api_ocr():
    try:
        raw, ext, name, opts = _payload_from_request()
    except Exception:
        return jsonify({"ok": False, "error": "base64 ไม่ถูกต้อง"}), 400
    problem = _validate(raw, ext)
    if problem:
        return jsonify({"ok": False, "error": problem}), 400
    try:
        if ext == ".pdf" and pdf_page_count(raw) > MAX_PAGES:
            return jsonify({"ok": False, "error": f"PDF เกิน {MAX_PAGES} หน้า"}), 400
        pages, text_all = _analyze(ext, raw, opts)
        result_id = secrets.token_hex(8)
        _cache_result(result_id, ext, raw, name, pages, text_all)
        log.info("ocr %s: %d page(s), ok", ext, len(pages))
        return jsonify({"ok": True, "pages": pages, "text": text_all, "result_id": result_id})
    except Exception:
        log.exception("ocr failed")
        return jsonify({"ok": False, "error": "อ่านไฟล์ไม่สำเร็จ: " + traceback.format_exc(limit=3).splitlines()[-1]}), 500


@app.post("/api/jobs")
def api_job_create():
    _prune_jobs()
    try:
        raw, ext, name, opts = _payload_from_request()
    except Exception:
        return jsonify({"ok": False, "error": "base64 ไม่ถูกต้อง"}), 400
    problem = _validate(raw, ext)
    if problem:
        return jsonify({"ok": False, "error": problem}), 400
    try:
        total = pdf_page_count(raw) if ext == ".pdf" else 1
        if total > MAX_PAGES:
            return jsonify({"ok": False, "error": f"PDF เกิน {MAX_PAGES} หน้า"}), 400
    except Exception:
        return jsonify({"ok": False, "error": "เปิดไฟล์ไม่สำเร็จ"}), 400
    job = Job(ext, raw, opts, name, total)
    with _jobs_lock:
        _jobs[job.id] = job
    _ensure_worker()
    _job_queue.put(job)
    return jsonify({"ok": True, "job_id": job.id, "total": total})


@app.get("/api/jobs/<job_id>")
def api_job_status(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({"ok": False, "error": "ไม่พบงานนี้ (อาจหมดอายุ)"}), 404
    return jsonify(job.snapshot(include_pages=True))


@app.post("/api/jobs/<job_id>/cancel")
def api_job_cancel(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({"ok": False, "error": "ไม่พบงานนี้"}), 404
    job.cancel.set()
    return jsonify({"ok": True})


# ---------------------------------------------------------------- export
def _export_pdf(entry: dict) -> bytes:
    import pymupdf as fitz

    font = asset_path("NotoSansThai-Regular.ttf")
    out = fitz.open()
    if entry["ext"] == ".pdf":
        src = fitz.open(stream=entry["source"], filetype="pdf")
        pages = []
        for page in src:
            pages.append(page)
        count = min(len(pages), len(entry["pages"]))
        for i in range(count):
            scale = float(entry["pages"][i].get("scale") or 1.0)
            pix = pages[i].get_pixmap(matrix=fitz.Matrix(1.6 * scale, 1.6 * scale))
            raw = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img = cv2.cvtColor(raw, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                img = cv2.cvtColor(raw, cv2.COLOR_RGB2BGR)
            else:
                img = cv2.cvtColor(raw[:, :, 0], cv2.COLOR_GRAY2BGR)
            _add_pdf_page(out, img, entry["pages"][i], font)
    else:
        page_result = entry["pages"][0]
        img = decode_image(entry["source"])
        scale = float(page_result.get("scale") or 1.0)
        if scale != 1.0:
            img = _resize(img, scale)
        _add_pdf_page(out, img, page_result, font)
    data = out.tobytes(garbage=3, deflate=True)
    out.close()
    return data


def _add_pdf_page(doc, img: np.ndarray, page_result: dict, font: Path):
    import pymupdf as fitz

    h, w = img.shape[:2]
    page = doc.new_page(width=float(w), height=float(h))
    ok, buf = cv2.imencode(".png", img)
    page.insert_image(page.rect, stream=buf.tobytes())
    if not font.exists():
        return page
    try:
        tw_font = fitz.Font(fontfile=str(font))
    except Exception:
        log.warning("cannot load export font %s", font)
        return page
    writer = fitz.TextWriter(page.rect)
    for ln in page_result.get("lines", []):
        box = np.array(ln["box"], dtype=np.float32)
        x0, y1 = float(box[:, 0].min()), float(box[:, 1].max())
        size = max(4.0, (y1 - float(box[:, 1].min())) * 0.8)
        try:
            writer.append((x0 + 1, y1 - max(1.0, size * 0.2)), ln["text"], font=tw_font, fontsize=size)
        except Exception:
            continue
    try:
        writer.write_text(page, render_mode=3)
    except Exception:
        log.exception("writing text layer failed")
    return page


def _export_csv(entry: dict) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["page", "row", "confidence", "x0", "y0", "x1", "y1", "text"])
    for p in entry["pages"]:
        for ln in p.get("lines", []):
            xs = [c[0] for c in ln["box"]]
            ys = [c[1] for c in ln["box"]]
            writer.writerow([p["page"], ln.get("row", 0), ln["confidence"],
                             round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1),
                             ln["text"]])
    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def _export_json(entry: dict) -> bytes:
    payload = {"app": APP_NAME, "version": APP_VERSION, "text": entry["text"],
               "pages": [{k: v for k, v in p.items() if k != "image"} for p in entry["pages"]]}
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def _export_txt(entry: dict) -> bytes:
    return entry["text"].encode("utf-8")


@app.get("/api/result/<result_id>/export")
def api_export(result_id):
    entry = _get_result(result_id)
    if not entry:
        return jsonify({"ok": False, "error": "ไม่พบผลลัพธ์ (อาจหมดอายุ — ให้ประมวลผลใหม่)"}), 404
    fmt = (request.args.get("format") or "pdf").lower()
    stem = Path(entry["name"]).stem or "ocr"
    try:
        if fmt == "pdf":
            return send_file(io.BytesIO(_export_pdf(entry)), mimetype="application/pdf",
                             as_attachment=True, download_name=f"{stem}-ocr.pdf")
        if fmt == "csv":
            return send_file(io.BytesIO(_export_csv(entry)), mimetype="text/csv; charset=utf-8",
                             as_attachment=True, download_name=f"{stem}-ocr.csv")
        if fmt == "json":
            return send_file(io.BytesIO(_export_json(entry)), mimetype="application/json",
                             as_attachment=True, download_name=f"{stem}-ocr.json")
        if fmt == "txt":
            return send_file(io.BytesIO(_export_txt(entry)), mimetype="text/plain; charset=utf-8",
                             as_attachment=True, download_name=f"{stem}-ocr.txt")
    except Exception:
        log.exception("export %s failed", fmt)
        return jsonify({"ok": False, "error": "สร้างไฟล์ส่งออกไม่สำเร็จ"}), 500
    return jsonify({"ok": False, "error": "format ไม่รองรับ (pdf|csv|json|txt)"}), 400


# ---------------------------------------------------------------- bootstrap
def _show_error(msg: str) -> None:
    log.error(msg.replace("\n", " | "))
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "OpenThai OCR", 0x10)
    except Exception:
        pass


def _show_info(msg: str) -> None:
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "OpenThai OCR", 0x40)
    except Exception:
        pass


def _existing_instance(ports) -> int | None:
    for port in ports:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=0.7) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("app") == APP_NAME:
                    return port
        except (urllib.error.URLError, OSError, ValueError):
            continue
    return None


def _port_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def main():
    global MODEL_DIR, PORT, API_KEY
    host = "127.0.0.1"
    ports = [PORT]
    no_browser = False
    args = sys.argv[1:]
    log_level = "INFO"
    for i, a in enumerate(args):
        if a == "--model" and i + 1 < len(args):
            MODEL_DIR = Path(args[i + 1])
        elif a == "--port" and i + 1 < len(args):
            base = int(args[i + 1])
            ports = list(range(base, base + 11))
        elif a == "--host" and i + 1 < len(args):
            host = args[i + 1]
        elif a == "--api-key" and i + 1 < len(args):
            API_KEY = args[i + 1]
        elif a == "--log-level" and i + 1 < len(args):
            log_level = args[i + 1]
        elif a == "--no-browser":
            no_browser = True

    setup_logging(log_level)
    required = ["det.onnx", "rec.onnx", "rec_dict.txt", "config.json"]
    missing = [n for n in required if not (MODEL_DIR / n).exists()]
    if missing:
        _show_error(f"ไม่พบไฟล์โมเดลในโฟลเดอร์:\n{MODEL_DIR}\n\nขาด: {', '.join(missing)}\n\n"
                    f"ตรวจสอบว่าโฟลเดอร์ models อยู่ข้าง ๆ ไฟล์โปรแกรม")
        return 1

    running = _existing_instance(ports)
    if running:
        log.info("already running on port %d — opening browser", running)
        if not no_browser:
            webbrowser.open(f"http://127.0.0.1:{running}/")
        return 0

    chosen = next((p for p in ports if _port_free(host, p)), None)
    if chosen is None:
        _show_error("พอร์ต 5000–5010 ถูกใช้งานหมด\nกรุณาปิดโปรแกรมอื่นหรือรันด้วย --port อื่น")
        return 1
    PORT = chosen

    if host not in ("127.0.0.1", "localhost", "::1") and not API_KEY:
        API_KEY = secrets.token_urlsafe(16)
        log.warning("LAN mode without --api-key: generated key %s", API_KEY)
        _show_info(f"เปิดใช้งานใน LAN — สร้าง API key อัตโนมัติ:\n\n{API_KEY}\n\n"
                   f"ใช้ header X-API-Key หรือช่อง API key ในหน้าเว็บ\n(กำหนดเองได้ด้วย --api-key)")

    if not no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()

    log.info("serving on %s:%d", host, PORT)
    from waitress import serve
    serve(app, host=host, port=PORT, threads=8)
    return 0


if __name__ == "__main__":
    sys.exit(main())