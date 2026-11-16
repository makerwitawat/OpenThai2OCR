# -*- coding: utf-8 -*-
"""PDF หลายหน้าเป็นอินพุต (กันพังเมื่อตัดไฟล์ pymupdf ที่ไม่ใช้ออกจาก exe)"""
import io
import sys
from pathlib import Path

import pymupdf
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as web  # noqa: E402


@pytest.fixture()
def client():
    web.app.config["TESTING"] = True
    with web.app.test_client() as c:
        yield c


def test_two_page_pdf_ocr_and_edited_export(client):
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 100), "PDF input page one", fontsize=28)
    doc.new_page().insert_text((72, 100), "Second page here", fontsize=28)
    res = client.post("/api/ocr", data={"file": (io.BytesIO(doc.tobytes()), "t.pdf"), "overlay": "0"},
                      content_type="multipart/form-data").get_json()
    assert res["ok"] and len(res["pages"]) == 2
    assert all(p["size"] for p in res["pages"])
    assert "page one" in res["text"] and "Second page" in res["text"]

    edited = "--- หน้า 1 ---\nFIRST\n\n--- หน้า 2 ---\nSECOND"
    pdf = client.post(f"/api/result/{res['result_id']}/export?format=pdf", json={"text": edited})
    assert pdf.status_code == 200
    out = pymupdf.open(stream=pdf.data, filetype="pdf")
    assert len(out) == 2
    assert "FIRST" in out[0].get_text() and "SECOND" in out[1].get_text()
    assert "page one" not in out[0].get_text()
