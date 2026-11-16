# -*- coding: utf-8 -*-
"""OpenThai2.0-OCR-Text: web UI (Flask) + OCR engine, buildable with PyInstaller."""
import base64
import sys
import threading
import traceback
import webbrowser
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request

BASE = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent


def _resolve_model_dir() -> Path:
    if getattr(sys, "frozen", False):
        embedded = Path(getattr(sys, "_MEIPASS", BASE)) / "models"
        if (embedded / "det.onnx").exists():
            return embedded
    return BASE / "models"


MODEL_DIR = _resolve_model_dir()
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".pdf"}
PORT = 5000

app = Flask(__name__)
app.json.ensure_ascii = False

if getattr(sys, "frozen", False):
    app.template_folder = str(Path(sys._MEIPASS) / "templates")

_engine = None
_engine_lock = threading.Lock()


def get_engine():
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                sys.path.insert(0, str(BASE))
                from models.runtime.line_engine import LineOCR
                _engine = LineOCR(str(MODEL_DIR), threads=2)
    return _engine


def pdf_to_images(data: bytes, zoom: float = 1.6) -> list[np.ndarray]:
    import pymupdf as fitz
    doc = fitz.open(stream=data, filetype="pdf")
    out = []
    mat = fitz.Matrix(zoom, zoom)
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif pix.n == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        out.append(np.ascontiguousarray(img))
    return out


def decode_image(data: bytes) -> np.ndarray:
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("decode image bytes failed")
    return img


def annotate_image(img: np.ndarray, lines: list[dict]) -> str:
    img = img.copy()
    for ln in lines:
        box = np.array(ln["box"], dtype=np.int32)
        cv2.polylines(img, [box], True, (0, 180, 0), 2)
        x0, y0 = int(box[:, 0].min()), int(box[:, 1].min())
        cv2.putText(img, f"{ln['confidence']:.2f}", (x0, max(14, y0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 220), 1, cv2.LINE_AA)
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
    """Keep only known numeric overrides within safe ranges (rec.color as string)."""
    out: dict[str, dict] = {}
    if not isinstance(raw, dict):
        return out
    for sec, vals in raw.items():
        if not isinstance(vals, dict):
            continue
        for key, value in vals.items():
            kind = _SETTING_TYPES.get((sec, key))
            try:
                if kind:
                    typ, lo, hi = kind
                    v = typ(value)
                    if v < lo or v > hi:
                        continue
                    out.setdefault(sec, {})[key] = v
                elif (sec, key) == ("rec", "color") and value in ("bgr", "gray", "gray_inv", "stretch", "flatten"):
                    out.setdefault(sec, {})[key] = value
            except (TypeError, ValueError):
                continue
    return out


class _engine_settings:
    """Temporarily apply per-request overrides to the shared engine config."""

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
    h, w = img.shape[:2]
    long_side = max(h, w)
    if long_side >= 1200:
        return 1.0
    return round(max(1.0, min(2.5, 1600.0 / max(long_side, 1))), 2)


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


@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def api_health():
    return jsonify({"ok": True, "model_dir": str(MODEL_DIR),
                    "model_ready": all((MODEL_DIR / n).exists() for n in ("det.onnx", "rec.onnx", "rec_dict.txt", "config.json"))})


def _ext_from_mime(mime: str) -> str:
    return {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg",
            "image/bmp": ".bmp", "image/tiff": ".tif", "image/webp": ".webp"}.get(mime, ".png")


def _payload_from_request():
    """(raw_bytes, ext, options) from multipart upload or JSON base64."""
    form = request.form if request.form else (request.get_json(silent=True) or {})
    if request.files.get("file") is not None:
        f = request.files["file"]
        ext = Path(f.filename or "").suffix.lower()
        raw = f.read()
    else:
        body = request.get_json(silent=True) or {}
        b64 = body.get("image_base64") or body.get("file_base64") or ""
        if not b64:
            return None, "", {}
        ext = Path(body.get("filename", "")).suffix.lower()
        if b64.startswith("data:") and ";base64," in b64:
            ext = _ext_from_mime(b64[5:b64.index(";")])
            b64 = b64.split(",", 1)[1]
        raw = base64.b64decode(b64)
        if not ext:
            ext = ".png"
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
            import json as _json
            settings = _json.loads(settings)
        except ValueError:
            settings = None
    elif not isinstance(settings, dict):
        settings = None
    if settings:
        opts["settings"] = settings
    return raw, ext, opts


@app.post("/api/ocr")
def api_ocr():
    try:
        raw, ext, opts = _payload_from_request()
    except Exception:
        return jsonify({"ok": False, "error": "base64 ไม่ถูกต้อง"}), 400
    if not raw:
        return jsonify({"ok": False, "error": "ไม่พบไฟล์ (แนบ multipart ชื่อ file หรือ JSON image_base64)"}), 400
    if ext not in ALLOWED_EXT:
        return jsonify({"ok": False, "error": f"นามสกุล {ext or '(ไม่มี)'} ไม่รองรับ"}), 400
    want_images = opts.get("want_images", True)
    scale = opts.get("scale")
    settings = opts.get("settings")
    try:
        images = pdf_to_images(raw) if ext == ".pdf" else [decode_image(raw)]
        pages = []
        for i, img in enumerate(images):
            r = read_image(img, want_images, scale_requested=scale, settings=settings)
            r["page"] = i + 1
            r["n_lines"] = len(r["lines"])
            pages.append(r)
        text_all = "\n\n".join(
            f"--- หน้า {p['page']} ---\n{p['text']}" for p in pages if p["text"]
        ).lstrip()
        return jsonify({"ok": True, "pages": pages, "text": text_all})
    except Exception:
        return jsonify({"ok": False, "error": "อ่านไฟล์ไม่สำเร็จ: " + traceback.format_exc(limit=3).splitlines()[-1]}), 500


def _show_error(msg: str) -> None:
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "OpenThai OCR - เกิดข้อผิดพลาด", 0x10)
    except Exception:
        print(msg, file=sys.stderr)


def main():
    global MODEL_DIR, PORT
    host = "127.0.0.1"
    args = sys.argv[1:]
    no_browser = "--no-browser" in args
    for i, a in enumerate(args):
        if a == "--model" and i + 1 < len(args):
            MODEL_DIR = Path(args[i + 1])
        elif a == "--port" and i + 1 < len(args):
            PORT = int(args[i + 1])
        elif a == "--host" and i + 1 < len(args):
            host = args[i + 1]
    required = ["det.onnx", "rec.onnx", "rec_dict.txt", "config.json"]
    missing = [n for n in required if not (MODEL_DIR / n).exists()]
    if missing:
        _show_error(f"ไม่พบไฟล์โมเดลในโฟลเดอร์:\n{MODEL_DIR}\n\nขาด: {', '.join(missing)}\n\n"
                    f"ตรวจสอบว่าโฟลเดอร์ models อยู่ข้าง ๆ ไฟล์โปรแกรม")
        return 1

    if not no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()

    from waitress import serve
    serve(app, host=host, port=PORT, threads=8)
    return 0


if __name__ == "__main__":
    sys.exit(main())