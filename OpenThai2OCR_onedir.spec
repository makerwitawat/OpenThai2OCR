# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: OpenThai2.0-OCR Web UI — onedir (models folder beside exe)."""
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    "models.runtime.line_engine",
    "models.runtime.thai_norm",
] + collect_submodules("waitress")

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[("templates", "templates")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["openvino", "IPython", "matplotlib", "pandas", "scipy", "torch", "torchvision", "torchaudio", "llvmlite", "numba", "sklearn", "sympy", "transformers", "tensorflow", "jax", "paddle", "paddleocr", "notebook", "ipykernel"],
    noarchive=False,
)
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