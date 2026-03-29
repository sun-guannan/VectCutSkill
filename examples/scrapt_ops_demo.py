#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/scrapt_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(out.strip())
    return json.loads(out)


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)
    if len(sys.argv) < 2:
        print("Usage: python examples/scrapt_ops_demo.py <share_url_or_text> [platform]")
        raise SystemExit(1)
    raw = sys.argv[1].strip()
    platform = sys.argv[2].strip().lower() if len(sys.argv) > 2 else "auto"
    action_map = {
        "auto": "parse_auto",
        "xiaohongshu": "parse_xiaohongshu",
        "douyin": "parse_douyin",
        "kuaishou": "parse_kuaishou",
        "bilibili": "parse_bilibili",
        "tiktok": "parse_tiktok",
        "youtube": "parse_youtube",
    }
    action = action_map.get(platform, "parse_auto")
    res = run_action(action, {"url": raw})
    data = res.get("data") if isinstance(res, dict) else {}
    if isinstance(data, dict):
        video = data.get("video") if isinstance(data.get("video"), dict) else {}
        print(f"PLATFORM => {data.get('platform', '')}")
        print(f"ORIGINAL_URL => {data.get('original_url', '')}")
        print(f"VIDEO_URL => {video.get('url', '')}")
        print(f"TITLE => {data.get('title', '')}")


if __name__ == "__main__":
    main()
