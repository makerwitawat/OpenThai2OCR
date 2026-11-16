# -*- coding: utf-8 -*-
"""ผลลัพธ์ต้องมี size ของพิกัด และ overlay=0 ให้ภาพเปล่า (ไว้วางกรอบ SVG ในหน้าเว็บ)"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as web  # noqa: E402


@pytest.fixture()
def client():
    web.app.config["TESTING"] = True
    with web.app.test_client() as c:
        yield c


@pytest.fixture(scope="module")
def png() -> bytes:
    img = np.full((200, 760, 3), 255, np.uint8)
    cv2.putText(img, "Test 123", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 0), 3, cv2.LINE_AA)
    ok, buf = cv2.imencode(".png", img)
    return buf.tobytes()


def _ocr(client, png, **extra):
    data = {"file": (io.BytesIO(png), "t.png"), **extra}
    return client.post("/api/ocr", data=data, content_type="multipart/form-data").get_json()


def test_size_is_present_and_boxes_fit(client, png):
    page = _ocr(client, png)["pages"][0]
    w, h = page["size"]
    assert w > 0 and h > 0
    for ln in page["lines"]:
        for x, y in ln["box"]:
            assert -5 <= x <= w + 5 and -5 <= y <= h + 5


def test_overlay_zero_gives_plain_image(client, png):
    with_boxes = _ocr(client, png)["pages"][0]
    plain = _ocr(client, png, overlay="0")["pages"][0]
    assert with_boxes["lines"], "ต้องอ่านได้อย่างน้อย 1 บรรทัดเพื่อให้เทียบกรอบได้"
    assert with_boxes["image"] != plain["image"]
    assert plain["size"] == with_boxes["size"]
