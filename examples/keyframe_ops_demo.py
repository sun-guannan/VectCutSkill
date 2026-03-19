#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "keyframe_ops.py")
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

    print("=== DEMO CATEGORY: keyframe ===")

    create_res = create_draft()
    print('CREATE => ' + json.dumps(create_res, ensure_ascii=False))
    draft_id = ((create_res.get('output') or {}).get('draft_id')) if isinstance(create_res, dict) else None
    if not draft_id:
        print('No draft_id, stop.')
        sys.exit(1)

    payload = {
  "draft_id": "__DRAFT_ID__",
  "track_name": "video_main",
  "property_type": "alpha",
  "time": 0,
  "value": "1.0",
  "property_types": [
    "alpha",
    "scale_x"
  ],
  "times": [
    0,
    2
  ],
  "values": [
    "1.0",
    "0.8"
  ]
}
    payload['draft_id'] = draft_id
    run_action("add_video_keyframe", payload)

if __name__ == '__main__':
    main()
