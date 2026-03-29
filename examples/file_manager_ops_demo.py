#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/file_manager_ops.py"
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
        print("Usage: python examples/file_manager_ops_demo.py <local_file_path> [file_name]")
        raise SystemExit(1)

    file_path = sys.argv[1].strip()
    file_name = sys.argv[2].strip() if len(sys.argv) > 2 else ""
    payload = {"file_path": file_path}
    if file_name:
        payload["file_name"] = file_name

    res = run_action("upload_file", payload)
    print(f"OBJECT_KEY => {res.get('object_key', '')}")
    print(f"PUBLIC_SIGNED_URL => {res.get('public_signed_url', '')}")


if __name__ == "__main__":
    main()
