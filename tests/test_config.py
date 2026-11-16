# -*- coding: utf-8 -*-
"""ทดสอบระบบ config: settings.json (apply_config) และ flag CLI (parse_cli)"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as web  # noqa: E402


@pytest.fixture(autouse=True)
def restore_globals(monkeypatch):
    """apply_config แก้ global — เก็บค่าเดิมไว้คืนหลังทุกเทสต์"""
    for name in {spec[3] for spec in web.CONFIG_SCHEMA.values()}:
        monkeypatch.setattr(web, name, getattr(web, name))
    monkeypatch.setitem(web.app.config, "MAX_CONTENT_LENGTH", web.app.config["MAX_CONTENT_LENGTH"])


def test_empty_prefs_keep_defaults():
    before = (web.PORT, web.HOST, web.MAX_PAGES, web.MODEL_DIR)
    assert web.apply_config({}) == []
    assert (web.PORT, web.HOST, web.MAX_PAGES, web.MODEL_DIR) == before


def test_apply_numbers_and_strings():
    warnings = web.apply_config({
        "port": 6001, "port_tries": 3, "host": "0.0.0.0", "max_pages": 7, "max_upload_mb": 10,
        "pdf_zoom": 2, "server_threads": 4, "engine_threads": 1, "api_key": "k",
        "cors_origin": "", "log_level": "debug", "annotate_max_width": 800})
    assert warnings == []
    assert (web.PORT, web.PORT_TRIES, web.HOST) == (6001, 3, "0.0.0.0")
    assert web.MAX_PAGES == 7 and web.MAX_CONTENT_MB == 10
    assert web.app.config["MAX_CONTENT_LENGTH"] == 10 * 1024 * 1024
    assert web.PDF_ZOOM == 2 and web.SERVER_THREADS == 4 and web.ENGINE_THREADS == 1
    assert web.API_KEY == "k" and web.CORS_ORIGIN == "" and web.LOG_LEVEL == "DEBUG"
    assert web.ANNOTATE_MAX_WIDTH == 800


def test_update_ttl_hours_converted_to_seconds():
    web.apply_config({"update_ttl_hours": 2, "update_timeout": 9})
    assert web.UPDATE_TTL == 2 * 3600
    assert web.UPDATE_TIMEOUT == 9


def test_paths_relative_to_base_and_absolute(tmp_path):
    web.apply_config({"model_dir": "my-models", "log_dir": str(tmp_path / "lg"),
                      "watch_dir": "inbox", "watch_out": ""})
    assert web.MODEL_DIR == web.BASE / "my-models"
    assert web.LOG_DIR == tmp_path / "lg"
    assert web.WATCH_DIR == str(web.BASE / "inbox")
    assert web.WATCH_OUT == ""


@pytest.mark.parametrize("key,value", [
    ("port", 70000), ("port", 0), ("port", "5000"), ("port", True), ("port", 5000.5),
    ("max_pages", -1), ("pdf_zoom", "big"), ("log_level", "loud"),
    ("model_dir", ""), ("host", " "), ("api_key", 123), ("watch_interval", 0.1),
])
def test_invalid_values_ignored_with_warning(key, value):
    before = getattr(web, web.CONFIG_SCHEMA[key][3])
    warnings = web.apply_config({key: value})
    assert len(warnings) == 1 and key in warnings[0]
    assert getattr(web, web.CONFIG_SCHEMA[key][3]) == before


def test_unknown_key_warns_but_known_prefs_do_not():
    warnings = web.apply_config({"prot": 1, "start_mode": "none", "open_browser": False, "update_check": True})
    assert len(warnings) == 1 and "prot" in warnings[0]


def test_pdf_and_annotate_use_configured_defaults(monkeypatch):
    import numpy as np
    monkeypatch.setattr(web, "ANNOTATE_MAX_WIDTH", 300)
    img = np.zeros((100, 600, 3), np.uint8)
    import base64
    import cv2
    out = web.annotate_image(img, [], draw=False)
    decoded = cv2.imdecode(np.frombuffer(base64.b64decode(out), np.uint8), cv2.IMREAD_COLOR)
    assert decoded.shape[1] == 300


# ---------------------------------------------------------------- CLI
def test_cli_parses_values_and_modes(tmp_path):
    values, mode, errors = web.parse_cli(
        ["--port", "6100", "--host", "0.0.0.0", "--max-pages", "9", "--window",
         "--watch-interval", "0.2", "--model", "rel-models", "--threads", "3"])
    assert errors == []
    assert mode == "window"
    assert values["port"] == 6100 and values["host"] == "0.0.0.0" and values["max_pages"] == 9
    assert values["watch_interval"] == 1.0  # clamp ขั้นต่ำเหมือนเดิม
    assert values["model_dir"] == Path.cwd() / "rel-models"  # CLI อิงโฟลเดอร์ปัจจุบัน
    assert values["server_threads"] == 3


def test_cli_bad_values_do_not_crash():
    values, mode, errors = web.parse_cli(["--port", "abc", "--bogus", "--max-pages"])
    assert values == {} and mode is None
    assert len(errors) == 3


def test_local_host_mapping():
    assert web._local_host("0.0.0.0") == "127.0.0.1"
    assert web._local_host("localhost") == "127.0.0.1"
    assert web._local_host("192.168.1.5") == "192.168.1.5"
    assert web._local_host("::1") == "[::1]"
