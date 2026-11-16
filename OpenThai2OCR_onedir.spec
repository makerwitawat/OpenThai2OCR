# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: OpenThai2.0-OCR Web UI — onedir (models folder beside exe)."""
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
    datas=[("templates", "templates"), ("assets", "assets"), ("app.ico", ".")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["openvino", "IPython", "matplotlib", "pandas", "scipy", "torch", "torchvision", "torchaudio", "llvmlite", "numba", "sklearn", "sympy", "transformers", "tensorflow", "jax", "paddle", "paddleocr", "notebook", "ipykernel",
              # ไม่ใช้ในแอป: cryptography ถูกดึงมาจาก webview/werkzeug (ทำใบรับรอง HTTPS), Pillow/Cython/fontTools หลุดมาจาก Python ของเครื่อง
              "cryptography", "PIL", "Cython", "fontTools", "pymupdf4llm", "pymupdf_layout"],
    noarchive=False,
)
# ตัดไฟล์ที่ไม่ได้ใช้ออก (เหมือน OpenThai2OCR.spec — ดูเหตุผลที่นั่น)
_DROP = ("pymupdf/layout/resources/onnx", "pymupdf/mupdf-devel", "opencv_videoio_ffmpeg")


def _keep(entry):
    return not any(s in str(entry[0]).replace("\\", "/") for s in _DROP)


a.binaries = [e for e in a.binaries if _keep(e)]
a.datas = [e for e in a.datas if _keep(e)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="OpenThai2OCR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon="app.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="OpenThai2OCR",
)