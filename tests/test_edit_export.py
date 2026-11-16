# -*- coding: utf-8 -*-
"""ส่งออกด้วยข้อความที่ผู้ใช้แก้ (POST /api/result/<id>/export พร้อม text)"""
import csv
import io
import json
import sys
import zipfile
from pathlib import Path

import cv2
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as web  # noqa: E402


def _quad(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


@pytest.fixture()
def client():
    web.app.config["TESTING"] = True
    with web.app.test_client() as c:
        yield c


@pytest.fixture()
def rid():
    """ผลลัพธ์สังเคราะห์: ภาพ 400x200 มี 2 row (row 0 มี 2 กล่อง)"""
    img = np.full((200, 400, 3), 255, np.uint8)
    ok, buf = cv2.imencode(".png", img)
    lines = [
        {"text": "hello", "confidence": 0.9, "row": 0, "box": _quad(10, 10, 100, 40)},
        {"text": "world", "confidence": 0.8, "row": 0, "box": _quad(120, 10, 200, 40)},
        {"text": "second line", "confidence": 0.7, "row": 1, "box": _quad(10, 80, 200, 110)},
    ]
    page = {"page": 1, "text": "hello world\nsecond line", "lines": lines, "scale": 1.0, "n_lines": 3}
    result_id = "test-edit-0001"
    web._cache_result(result_id, ".png", buf.tobytes(), "sample.png", [page],
                      "--- หน้า 1 ---\nhello world\nsecond line")
    return result_id


def _post(client, rid, fmt, text):
    return client.post(f"/api/result/{rid}/export?format={fmt}", json={"text": text})


def test_txt_uses_edited_text(client, rid):
    res = _post(client, rid, "txt", "แก้แล้ว\nบรรทัดสอง")
    assert res.status_code == 200
    assert res.data.decode("utf-8") == "แก้แล้ว\nบรรทัดสอง"


def test_get_without_text_keeps_original(client, rid):
    res = client.get(f"/api/result/{rid}/export?format=txt")
    assert "hello world" in res.data.decode("utf-8")


def test_json_marks_edited(client, rid):
    res = _post(client, rid, "json", "AAA\nBBB")
    data = json.loads(res.data.decode("utf-8"))
    assert data["text"] == "AAA\nBBB"
    assert [ln["text"] for ln in data["pages"][0]["lines"]] == ["AAA", "BBB"]
    assert data["pages"][0]["edited"] is True


def test_csv_aligned_rows_use_row_boxes(client, rid):
    res = _post(client, rid, "csv", "AAA\nBBB")
    rows = list(csv.reader(io.StringIO(res.data.decode("utf-8-sig"))))
    assert rows[0][-1] == "text"
    assert [r[-1] for r in rows[1:]] == ["AAA", "BBB"]
    # row 0 = รวมกล่อง 2 ใบ → x0=10, x1=200
    assert float(rows[1][3]) == 10.0 and float(rows[1][5]) == 200.0


def test_csv_line_count_mismatch_still_exports(client, rid):
    res = _post(client, rid, "csv", "A\nB\nC\nD")
    rows = list(csv.reader(io.StringIO(res.data.decode("utf-8-sig"))))
    assert [r[-1] for r in rows[1:]] == ["A", "B", "C", "D"]


def test_docx_uses_edited_text(client, rid):
    res = _post(client, rid, "docx", "ข้อความใหม่\nอีกบรรทัด")
    assert res.data[:2] == b"PK"
    with zipfile.ZipFile(io.BytesIO(res.data)) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    assert "ข้อความใหม่" in xml and "hello" not in xml


def test_pdf_text_layer_uses_edited_text(client, rid):
    import pymupdf as fitz
    res = _post(client, rid, "pdf", "EditedOne\nEditedTwo")
    assert res.data[:4] == b"%PDF"
    doc = fitz.open(stream=res.data, filetype="pdf")
    text = doc[0].get_text()
    assert "EditedOne" in text and "hello" not in text


def test_page_headers_are_stripped(client, rid):
    res = _post(client, rid, "txt", "=== sample.png ===\n--- Page 1 ---\nX")
    assert res.status_code == 200
    # txt ส่งข้อความตามที่ผู้ใช้ส่งมาทั้งก้อน
    assert "X" in res.data.decode("utf-8")
    csv_res = _post(client, rid, "csv", "=== sample.png ===\n--- Page 1 ---\nX\nY")
    rows = list(csv.reader(io.StringIO(csv_res.data.decode("utf-8-sig"))))
    assert [r[-1] for r in rows[1:]] == ["X", "Y"]


def test_bad_text_type_rejected(client, rid):
    res = client.post(f"/api/result/{rid}/export?format=txt", json={"text": 123})
    assert res.status_code == 400


def test_too_long_text_rejected(client, rid, monkeypatch):
    monkeypatch.setattr(web, "MAX_EDIT_CHARS", 10)
    res = _post(client, rid, "txt", "x" * 11)
    assert res.status_code == 413


def test_edit_does_not_mutate_cache(client, rid):
    _post(client, rid, "json", "AAA\nBBB")
    again = client.get(f"/api/result/{rid}/export?format=json")
    data = json.loads(again.data.decode("utf-8"))
    assert "hello world" in data["text"]
    assert data["pages"][0].get("edited") is None
