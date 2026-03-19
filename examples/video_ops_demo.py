#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "video_ops.py")
BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying").rstrip("/")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

def create_draft():
    url = f"{BASE_URL}/create_draft"
    req = urllib.request.Request(
        url=url,
        data=json.dumps({"name": "demo", "width": 1080, "height": 1920}, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))

def run_action(action, payload):
    out = subprocess.check_output([sys.executable, SCRIPT, action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action} => {out.strip()}")
    return out

def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        sys.exit(1)

    print("=== DEMO CATEGORY: video ===")

    payload = {}
    run_action("add_video", payload)

if __name__ == '__main__':
    main()
