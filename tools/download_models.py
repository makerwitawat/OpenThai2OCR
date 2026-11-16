# -*- coding: utf-8 -*-
"""Download OpenThai2.0-OCR-Text files from Hugging Face into ./models."""
import sys
import urllib.request
from pathlib import Path

REPO = "iapp/OpenThai2.0-OCR-Text"
BASE = f"https://huggingface.co/{REPO}/resolve/main"
FILES = ["det.onnx", "rec.onnx", "rec_dict.txt", "config.json",
         "runtime/line_engine.py", "runtime/thai_norm.py"]

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"


def main() -> int:
    MODELS.mkdir(exist_ok=True)
    (MODELS / "runtime").mkdir(exist_ok=True)
    for name in FILES:
        dest = MODELS / name
        if dest.exists() and dest.stat().st_size > 0:
            print(f"skip  {name} ({dest.stat().st_size} bytes)")
            continue
        print(f"get   {name}")
        urllib.request.urlretrieve(f"{BASE}/{name}", dest)
        print(f"done  {name} ({dest.stat().st_size} bytes)")
    for pkg in (MODELS / "__init__.py", MODELS / "runtime" / "__init__.py"):
        pkg.write_text("# -*- coding: utf-8 -*-\n", encoding="utf-8")
    print("models ready at", MODELS)
    return 0


if __name__ == "__main__":
    sys.exit(main())