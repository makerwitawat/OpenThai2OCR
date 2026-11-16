# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: OpenThai2.0-OCR Web UI — ONE FILE (models embedded)."""
import sys

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    "models.runtime.line_engine",
    "models.runtime.thai_norm",
] + collect_submodules("waitress")

if sys.platform == "win32":
    # native app window (--window) on Windows: WebView2 via pythonnet
    hiddenimports += [
        "webview",
        "webview.platforms.edgechromium",
        "webview.platforms.winforms",
        "clr",
        "clr_loader",
    ]

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("templates", "templates"),
        ("assets", "assets"),
        ("app.ico", "."),
        ("models/det.onnx", "models"),
        ("models/rec.onnx", "models"),
        ("models/rec_dict.txt", "models"),
        ("models/config.json", "models"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["openvino", "IPython", "matplotlib", "pandas", "scipy", "torch", "torchvision", "torchaudio", "llvmlite", "numba", "sklearn", "sympy", "transformers", "tensorflow", "jax", "paddle", "paddleocr", "notebook", "ipykernel"],
    noarchive=False,
)
# ตัดไฟล์ที่ไม่ได้ใช้ออกจาก exe (วัดแล้วกินพื้นที่ ~50 MB บีบอัด):
# - pymupdf\layout\resources\onnx : โมเดลวิเคราะห์เลย์เอาต์ของ pymupdf4llm — แอปนี้ใช้ pymupdf แค่เรนเดอร์/สร้าง PDF
# - pymupdf\mupdf-devel          : ไฟล์ .lib/.h สำหรับคอมไพล์ ไม่ใช้ตอนรัน
# - opencv_videoio_ffmpeg*       : ตัวถอดรหัสวิดีโอ — แอปนี้อ่านแค่ภาพนิ่ง
_DROP = ("pymupdf/layout/resources/onnx", "pymupdf/mupdf-devel", "opencv_videoio_ffmpeg")


def _keep(entry):
    return not any(s in str(entry[0]).replace("\\", "/") for s in _DROP)


a.binaries = [e for e in a.binaries if _keep(e)]
a.datas = [e for e in a.datas if _keep(e)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="OpenThai2OCR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon="app.ico",
)