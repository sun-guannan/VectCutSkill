#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/koubo_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action.upper()} => {out.strip()}")
    return json.loads(out)


def extract_task_id(data):
    if not isinstance(data, dict):
        return ""
    output = data.get("output") if isinstance(data.get("output"), dict) else {}
    for value in [data.get("task_id"), data.get("id"), output.get("task_id"), output.get("id")]:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)
    if len(sys.argv) < 3:
        print("Usage: python examples/koubo_ops_demo.py <agent_id> <video_url> [title] [text_content] [cover_url] [name]")
        raise SystemExit(1)

    agent_id = sys.argv[1].strip()
    video_url = sys.argv[2].strip()
    title = sys.argv[3].strip() if len(sys.argv) > 3 else ""
    text_content = sys.argv[4].strip() if len(sys.argv) > 4 else ""
    cover_url = sys.argv[5].strip() if len(sys.argv) > 5 else ""
    name = sys.argv[6].strip() if len(sys.argv) > 6 else ""

    params = {"video_url": [video_url]}
    if title:
        params["title"] = title
    if text_content:
        params["text_content"] = text_content
    if cover_url:
        params["cover"] = [cover_url]
    if name:
        params["name"] = name

    submit_res = run_action("submit_agent_task", {"agent_id": agent_id, "params": params})
    task_id = extract_task_id(submit_res)
    if not task_id:
        print("No task_id, stop.")
        raise SystemExit(1)

    wait_res = run_action("koubo_wait", {"task_id": task_id, "max_poll": 120, "poll_interval": 2})
    output = wait_res.get("output") if isinstance(wait_res, dict) else {}
    if isinstance(output, dict):
        if output.get("draft_url"):
            print(f"DRAFT_URL => {output.get('draft_url')}")
        if output.get("video_url"):
            print(f"VIDEO_URL => {output.get('video_url')}")


if __name__ == "__main__":
    main()
