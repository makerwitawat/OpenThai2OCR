# -*- coding: utf-8 -*-
"""API tests for the OpenThai2.0 OCR web app (pytest, no network needed)."""
import base64
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


@pytest.fixture(scope="session")
def sample_png() -> bytes:
    img = np.full((200, 760, 3), 255, np.uint8)
    cv2.putText(img, "Test 123", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 0), 3, cv2.LINE_AA)
    ok, buf = cv2.imencode(".png", img)
    return buf.tobytes()


def test_health(client):
    data = client.get("/api/health").get_json()
    assert data["ok"] is True
    assert data["app"] == web.APP_NAME
    assert data["version"] == web.APP_VERSION
    assert data["model_ready"] is True


def test_index_has_ui(client):
    html = client.get("/").get_data(as_text=True)
    assert "I18N" in html
    assert "/favicon.ico" in html
    assert "api/ocr" in html


def test_ocr_and_export(client, sample_png):
    res = client.post("/api/ocr", data={"file": (__import__("io").BytesIO(sample_png), "sample.png")},
                      content_type="multipart/form-data")
    data = res.get_json()
    assert data["ok"] is True
    assert data["pages"][0]["text"].strip()
    rid = data["result_id"]

    pdf = client.get(f"/api/result/{rid}/export?format=pdf")
    assert pdf.status_code == 200 and pdf.data[:4] == b"%PDF"
    csv_data = client.get(f"/api/result/{rid}/export?format=csv")
    assert csv_data.status_code == 200 and "confidence" in csv_data.get_data(as_text=True)
    js = client.get(f"/api/result/{rid}/export?format=json").get_json()
    assert js["version"] == web.APP_VERSION


def test_ocr_rejects_unknown_extension(client, sample_png):
    res = client.post("/api/ocr", data={"file": (__import__("io").BytesIO(sample_png), "bad.exe")},
                      content_type="multipart/form-data")
    assert res.status_code == 400
    assert res.get_json()["ok"] is False


def test_export_unknown_result(client):
    assert client.get("/api/result/nope/export?format=pdf").status_code == 404


def test_api_key_enforced(client, sample_png, monkeypatch):
    monkeypatch.setattr(web, "API_KEY", "k123")
    assert client.get("/api/health").get_json()["auth_required"] is True
    no_key = client.post("/api/ocr", data={"file": (__import__("io").BytesIO(sample_png), "sample.png")},
                         content_type="multipart/form-data")
    assert no_key.status_code == 401
    ok = client.post("/api/ocr", data={"file": (__import__("io").BytesIO(sample_png), "sample.png")},
                     content_type="multipart/form-data", headers={"X-API-Key": "k123"})
    assert ok.status_code == 200


def test_base64_payload(client, sample_png):
    body = {"image_base64": base64.b64encode(sample_png).decode(), "images": False}
    data = client.post("/api/ocr", json=body).get_json()
    assert data["ok"] is True
    assert "image" not in data["pages"][0]