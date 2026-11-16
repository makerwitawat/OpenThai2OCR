# -*- coding: utf-8 -*-
"""Smoke test: generate a small image and read it with the bundled model."""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.runtime.line_engine import LineOCR  # noqa: E402

img = np.full((260, 900, 3), 255, np.uint8)
cv2.putText(img, "Smoke test 123", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)
cv2.putText(img, "OpenThai OCR", (30, 190), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)

ocr = LineOCR(ROOT / "models", threads=1)
result = ocr.read(img)
text = result["text"].strip()
assert text, "OCR returned empty text"
print("OK:", text.replace("\n", " | "))
print("timing:", result["timing"])