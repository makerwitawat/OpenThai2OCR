# -*- coding: utf-8 -*-
"""ทดสอบหน้า/ API ตั้งค่า: GET/POST /api/config + /settings (เขียนลง settings.json จำลองใน tmp)"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as web  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(web, "SETTINGS_FILE", tmp_path / "settings.json")
    monkeypatch.setattr(web, "FALLBACK_SETTINGS", tmp_path / "fallback.json")
    web.app.config["TESTING"] = True
    with web.app.test_client() as c:
        yield c


def _post(client, payload, **kw):
    return client.post("/api/config", data=json.dumps(payload), content_type="application/json", **kw)


def test_settings_page_renders_and_linked(client):
    html = client.get("/settings").get_data(as_text=True)
    assert "/api/config" in html
    assert 'href="/settings"' in client.get("/status").get_data(as_text=True)
    assert 'href="/settings"' in client.get("/").get_data(as_text=True)


def test_get_lists_every_schema_key_with_defaults(client):
    data = client.get("/api/config").get_json()
    assert data["ok"]
    keys = {i["key"] for i in data["items"]}
    assert keys == set(web.CONFIG_SCHEMA)
    by = {i["key"]: i for i in data["items"]}
    assert by["port"]["default"] == 5000 and by["port"]["is_set"] is False
    assert by["log_level"]["choices"] == ["DEBUG", "INFO", "WARNING", "ERROR"]
    assert by["update_ttl_hours"]["default"] == 6


def test_post_saves_and_get_reflects(client, tmp_path):
    res = _post(client, {"values": {"port": 6200, "log_level": "debug", "model_dir": " my-models ",
                                    "max_pages": 12.0}})
    body = res.get_json()
    assert res.status_code == 200 and body["restart_required"] is True
    saved = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert saved["port"] == 6200 and saved["log_level"] == "DEBUG"
    assert saved["model_dir"] == "my-models" and saved["max_pages"] == 12
    assert isinstance(saved["max_pages"], int)
    by = {i["key"]: i for i in client.get("/api/config").get_json()["items"]}
    assert by["port"]["is_set"] and by["port"]["saved"] == 6200
    # ค่าที่ใช้งานอยู่ยังไม่เปลี่ยนจนกว่าจะรีสตาร์ต
    assert by["port"]["effective"] == web.PORT


def test_saved_values_roundtrip_through_apply_config(client, monkeypatch):
    for name in ("PORT", "MAX_PAGES"):
        monkeypatch.setattr(web, name, getattr(web, name))
    _post(client, {"values": {"port": 6300, "max_pages": 4}})
    assert web.apply_config() == []
    assert web.PORT == 6300 and web.MAX_PAGES == 4


def test_invalid_values_rejected_nothing_written(client, tmp_path):
    res = _post(client, {"values": {"port": 99999, "pdf_zoom": "x", "nope": 1, "max_pages": 5}})
    body = res.get_json()
    assert res.status_code == 400 and set(body["errors"]) == {"port", "pdf_zoom", "nope"}
    assert not (tmp_path / "settings.json").exists()


def test_reset_removes_key_and_keeps_others(client, tmp_path):
    _post(client, {"values": {"port": 6200, "max_pages": 9}})
    res = _post(client, {"reset": ["port", "bogus"]})
    assert res.status_code == 200 and res.get_json()["reset"] == ["port"]
    saved = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert "port" not in saved and saved["max_pages"] == 9


def test_existing_prefs_are_preserved(client, tmp_path):
    (tmp_path / "settings.json").write_text(json.dumps({"start_mode": "none", "update_check": False}),
                                            encoding="utf-8")
    _post(client, {"values": {"port": 6400}})
    saved = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert saved == {"start_mode": "none", "update_check": False, "port": 6400}


def test_empty_request_rejected(client):
    assert _post(client, {}).status_code == 400
    assert _post(client, {"values": []}).status_code == 400


def test_remote_client_forbidden(client):
    env = {"REMOTE_ADDR": "192.168.1.9"}
    assert client.get("/api/config", environ_overrides=env).status_code == 403
    assert _post(client, {"values": {"port": 6200}}, environ_overrides=env).status_code == 403


def test_cross_origin_post_forbidden(client, tmp_path):
    res = _post(client, {"values": {"port": 6200}}, headers={"Origin": "http://evil.example"})
    assert res.status_code == 403
    assert not (tmp_path / "settings.json").exists()
    ok = _post(client, {"values": {"port": 6200}}, headers={"Origin": "http://localhost"})
    assert ok.status_code == 200  # same-origin (Host ของ test client = localhost)


def test_api_key_required_when_enabled(client, monkeypatch):
    monkeypatch.setattr(web, "API_KEY", "k123")
    assert client.get("/api/config").status_code == 401
    assert client.get("/api/config", headers={"X-API-Key": "k123"}).status_code == 200
