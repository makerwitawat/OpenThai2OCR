# -*- coding: utf-8 -*-
"""ตรวจอัปเดตจาก GitHub Releases (mock เครือข่ายทั้งหมด)"""
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
    monkeypatch.setitem(web._update_cache, "at", 0.0)
    monkeypatch.setitem(web._update_cache, "data", None)
    monkeypatch.setitem(web._update_cache, "fail_at", 0.0)
    web.app.config["TESTING"] = True
    with web.app.test_client() as c:
        yield c


def _release(tag):
    return {"tag_name": tag, "html_url": f"https://github.com/x/y/releases/tag/{tag}"}


def test_version_tuple():
    assert web._version_tuple("v1.4.0") == (1, 4, 0)
    assert web._version_tuple("1.10.0") > web._version_tuple("1.9.9")
    assert web._version_tuple("garbage") == (0,)


def test_newer_release_flagged(client, monkeypatch):
    monkeypatch.setattr(web, "_fetch_latest_release", lambda: _release("v99.0.0"))
    data = client.get("/api/update-check").get_json()
    assert data["update_available"] is True
    assert data["latest"] == "99.0.0" and data["current"] == web.APP_VERSION
    assert data["url"].endswith("v99.0.0")


def test_same_or_older_not_flagged(client, monkeypatch):
    monkeypatch.setattr(web, "_fetch_latest_release", lambda: _release("v" + web.APP_VERSION))
    assert client.get("/api/update-check").get_json()["update_available"] is False
    monkeypatch.setitem(web._update_cache, "data", None)
    monkeypatch.setattr(web, "_fetch_latest_release", lambda: _release("v0.0.1"))
    assert client.get("/api/update-check").get_json()["update_available"] is False


def test_offline_is_silent(client, monkeypatch):
    def boom():
        raise OSError("offline")
    monkeypatch.setattr(web, "_fetch_latest_release", boom)
    res = client.get("/api/update-check")
    data = res.get_json()
    assert res.status_code == 200 and data["ok"] is True
    assert data["update_available"] is False and data["error"]


def test_failure_is_not_retried_immediately(client, monkeypatch):
    calls = []

    def boom():
        calls.append(1)
        raise OSError("offline")
    monkeypatch.setattr(web, "_fetch_latest_release", boom)
    client.get("/api/update-check")
    client.get("/api/update-check")
    assert len(calls) == 1
    client.get("/api/update-check?force=1")
    assert len(calls) == 2


def test_result_is_cached(client, monkeypatch):
    calls = []

    def ok():
        calls.append(1)
        return _release("v99.0.0")
    monkeypatch.setattr(web, "_fetch_latest_release", ok)
    client.get("/api/update-check")
    client.get("/api/update-check")
    assert len(calls) == 1


def test_disabled_pref_skips_network(client, monkeypatch):
    def boom():
        raise AssertionError("must not be called")
    monkeypatch.setattr(web, "_fetch_latest_release", boom)
    assert client.post("/api/prefs", json={"update_check": False}).get_json()["ok"] is True
    assert client.get("/api/prefs").get_json()["update_check"] is False
    data = client.get("/api/update-check").get_json()
    assert data["enabled"] is False and data["update_available"] is False


def test_prefs_update_check_default_true(client):
    assert client.get("/api/prefs").get_json()["update_check"] is True
