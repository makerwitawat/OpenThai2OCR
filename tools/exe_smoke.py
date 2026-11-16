# -*- coding: utf-8 -*-
"""Smoke test ตัว exe/binary ที่ build แล้ว: เปิดด้วย --port, รอ /api/health, ยิง OCR 1 ครั้ง, แล้วปิด

ใช้: python tools/exe_smoke.py dist/OpenThai2OCR.exe [--port 5890] [--timeout 120]
"""
import argparse
import base64
import json
import subprocess
import sys
import time
import urllib.request

import cv2
import numpy as np


def call(url, data=None, timeout=60):
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exe")
    ap.add_argument("--port", type=int, default=5890)
    ap.add_argument("--timeout", type=float, default=120.0)
    args = ap.parse_args()

    proc = subprocess.Popen([args.exe, "--no-browser", "--port", str(args.port)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{args.port}"
    ok = False
    try:
        health, deadline = None, time.time() + args.timeout
        while time.time() < deadline:
            if proc.poll() is not None:
                raise SystemExit(f"FAIL: exe ปิดตัวเองก่อนพร้อม (exit code {proc.returncode})")
            try:
                for p in range(args.port, args.port + 11):
                    try:
                        health = call(f"http://127.0.0.1:{p}/api/health", timeout=2)
                        base = f"http://127.0.0.1:{p}"
                        break
                    except Exception:
                        continue
                if health:
                    break
            except Exception:
                pass
            time.sleep(1)
        if not health:
            raise SystemExit("FAIL: /api/health ไม่ตอบภายในเวลาที่กำหนด")
        print("health:", health["app"], health["version"], "model_ready =", health["model_ready"])
        assert health["ok"] and health["model_ready"], "model ไม่พร้อมใน exe"

        img = np.full((260, 900, 3), 255, np.uint8)
        cv2.putText(img, "Smoke test 123", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(img, "OpenThai OCR", (30, 190), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)
        png = cv2.imencode(".png", img)[1].tobytes()
        body = json.dumps({"image_base64": base64.b64encode(png).decode(), "filename": "smoke.png",
                           "images": "0"}).encode()
        res = call(base + "/api/ocr", data=body, timeout=120)
        assert res.get("ok"), f"OCR ล้มเหลว: {res}"
        assert res["text"].strip(), "OCR คืนข้อความว่าง"
        shown = res["text"].strip().replace("\n", " | ").encode("ascii", "replace").decode("ascii")
        print("OCR OK:", shown)
        ok = True
    finally:
        try:
            call(base + "/api/shutdown", data=b"{}", timeout=5)
        except Exception:
            pass
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
