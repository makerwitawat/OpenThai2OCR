# -*- coding: utf-8 -*-
"""API tests for the OpenThai2.0 OCR web app (pytest, no network needed)."""
import base64
import io
import os
import sys
import time
import zipfile
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


def test_docx_export(client, sample_png):
    res = client.post("/api/ocr", data={"file": (io.BytesIO(sample_png), "sample.png")},
                      content_type="multipart/form-data")
    rid = res.get_json()["result_id"]
    docx = client.get(f"/api/result/{rid}/export?format=docx")
    assert docx.status_code == 200
    assert docx.data[:2] == b"PK"
    with zipfile.ZipFile(io.BytesIO(docx.data)) as z:
        assert {"[Content_Types].xml", "word/document.xml", "word/styles.xml"} <= set(z.namelist())
        assert "w:body" in z.read("word/document.xml").decode("utf-8")


def test_watch_folder(tmp_path, monkeypatch, sample_png):
    inbox, out = tmp_path / "in", tmp_path / "out"
    inbox.mkdir()
    monkeypatch.setattr(web, "WATCH_DIR", str(inbox))
    monkeypatch.setattr(web, "WATCH_OUT", str(out))
    monkeypatch.setattr(web, "WATCH_INTERVAL", 1.0)
    src = inbox / "doc.png"
    src.write_bytes(sample_png)
    old = time.time() - 60
    os.utime(src, (old, old))

    assert web._watch_scan() == ["doc.png"]
    assert (out / "doc-ocr.txt").read_text(encoding="utf-8").strip()
    assert (out / "doc-ocr.docx").read_bytes()[:2] == b"PK"
    assert (out / "doc-ocr.json").exists()
assert web._watch_scan() == []  # unchanged file is not processed twice


def test_pages_render(client):
    for path in ("/", "/docs", "/playground", "/status"):
        res = client.get(path)
        assert res.status_code == 200, path
        html = res.get_data(as_text=True)
        assert "OpenThai2.0 OCR" in html


def test_status_api(client):
    data = client.get("/api/status").get_json()
    assert data["ok"] is True
    assert data["version"] == web.APP_VERSION
    assert data["model_ready"] is True
    assert "jobs" in data and "results_cached" in data
    assert isinstance(data["uptime_s"], (int, float))


def test_prefs_roundtrip(client, tmp_path, monkeypatch):
    monkeypatch.setattr(web, "SETTINGS_FILE", tmp_path / "settings.json")
    monkeypatch.setattr(web, "FALLBACK_SETTINGS", tmp_path / "fallback.json")
    monkeypatch.setattr(web, "OPEN_BROWSER", True)
    res = client.post("/api/prefs", json={"open_browser": False}).get_json()
    assert res["ok"] is True and res["open_browser"] is False
    assert (tmp_path / "settings.json").exists()
    data = client.get("/api/prefs").get_json()
    assert data["open_browser"] is False
    assert data["saved_open_browser"] is False
    assert client.post("/api/prefs", json={}).status_code == 400
