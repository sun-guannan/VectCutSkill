#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/subtitle_template_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action.upper()} => {out.strip()}")
    return json.loads(out)


def extract_task_id(data):
    if not isinstance(data, dict):
        return ""
    for key in ["task_id", "id"]:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    result = data.get("result")
    if isinstance(result, dict):
        for key in ["task_id", "id"]:
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        output = result.get("output")
        if isinstance(output, dict):
            for key in ["task_id", "id"]:
                value = output.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    output = data.get("output")
    if isinstance(output, dict):
        for key in ["task_id", "id"]:
            value = output.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)
    if len(sys.argv) < 4:
        print("Usage: python examples/subtitle_ops_template.py <smart|sta> <agent_id> <url> [text] [add_media(true|false)] [draft_id]")
        raise SystemExit(1)

    mode = sys.argv[1].strip().lower()
    agent_id = sys.argv[2].strip()
    url = sys.argv[3].strip()
    text = sys.argv[4].strip() if len(sys.argv) > 4 else ""
    add_media_raw = sys.argv[5].strip().lower() if len(sys.argv) > 5 else "false"
    draft_id = sys.argv[6].strip() if len(sys.argv) > 6 else ""
    add_media = add_media_raw == "true"

    if mode not in {"smart", "sta"}:
        print("mode must be smart or sta")
        raise SystemExit(1)

    if mode == "smart":
        payload = {"agent_id": agent_id, "url": url, "add_media": add_media}
        if draft_id:
            payload["draft_id"] = draft_id
        create_res = run_action("generate_smart_subtitle", payload)
    else:
        if not text:
            print("text is required when mode=sta")
            raise SystemExit(1)
        payload = {"agent_id": agent_id, "url": url, "text": text, "add_media": add_media}
        if draft_id:
            payload["draft_id"] = draft_id
        create_res = run_action("sta_subtitle", payload)

    task_id = extract_task_id(create_res)
    if not task_id:
        print("No task_id, stop.")
        raise SystemExit(1)

    wait_res = run_action("subtitle_wait", {"task_id": task_id, "max_poll": 120, "poll_interval": 2})
    result = wait_res.get("result") if isinstance(wait_res, dict) else {}
    output = result.get("output") if isinstance(result, dict) else {}
    if isinstance(output, dict):
        if output.get("draft_url"):
            print(f"DRAFT_URL => {output.get('draft_url')}")
        if output.get("video_url"):
            print(f"VIDEO_URL => {output.get('video_url')}")


if __name__ == "__main__":
    main()
