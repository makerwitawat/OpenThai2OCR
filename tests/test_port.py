# -*- coding: utf-8 -*-
"""ทดสอบ _existing_instance: ต้องผูกต่อเฉพาะ instance เวอร์ชันตรงกันเท่านั้น (ไม่แตะพอร์ตจริง)"""
import io
import json
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as web  # noqa: E402


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _fake_urlopen(table):
    """table: {port: dict | Exception}"""
    def fake(url, timeout=None):
        port = int(url.split(":")[2].split("/")[0])
        val = table.get(port, urllib.error.URLError("refused"))
        if isinstance(val, Exception):
            raise val
        return _Resp(json.dumps(val).encode("utf-8"))
    return fake


def test_same_version_is_reused(monkeypatch):
    monkeypatch.setattr(web.urllib.request, "urlopen", _fake_urlopen(
        {6000: {"app": web.APP_NAME, "version": web.APP_VERSION}}))
    assert web._existing_instance([6000, 6001]) == 6000


def test_other_version_is_skipped(monkeypatch):
    monkeypatch.setattr(web.urllib.request, "urlopen", _fake_urlopen(
        {6000: {"app": web.APP_NAME, "version": "0.0.1"}}))
    assert web._existing_instance([6000, 6001]) is None


def test_other_version_then_same_version(monkeypatch):
    monkeypatch.setattr(web.urllib.request, "urlopen", _fake_urlopen({
        6000: {"app": web.APP_NAME, "version": "0.0.1"},
        6001: {"app": web.APP_NAME, "version": web.APP_VERSION}}))
    assert web._existing_instance([6000, 6001]) == 6001


def test_foreign_app_and_errors_are_skipped(monkeypatch):
    monkeypatch.setattr(web.urllib.request, "urlopen", _fake_urlopen({
        6000: {"app": "something-else", "version": web.APP_VERSION},
        6001: ValueError("bad json"),
        6002: ["not", "a", "dict"]}))
    assert web._existing_instance([6000, 6001, 6002, 6003]) is None
