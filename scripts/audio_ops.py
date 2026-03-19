#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
ROOT = Path(__file__).resolve().parents[1]
AUDIO_ENUM = Path(os.getenv("AUDIO_ENUM", str(ROOT / "references/enums/audio_effect_types.json")))

ACTION_ENDPOINT = {
    "add_audio": "add_audio",
    "modify_audio": "modify_audio",
    "remove_audio": "remove_audio",
}

def fail(error, output=None, hint=None):
    data = {"success": False, "error": error, "output": output if output is not None else ""}
    if hint:
        data["hint"] = hint
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)

def load_enum_items(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items", [])
        if not isinstance(items, list):
            return []
        return [x for x in items if isinstance(x, dict) and x.get("name")]
    except Exception as e:
        fail(f"Failed to load enum file: {path}", {"exception": str(e)})

def load_enum_names(path: Path):
    return {x.get("name") for x in load_enum_items(path) if x.get("name")}

def parse_payload(raw):
    try:
        data = json.loads(raw)
    except Exception as e:
        fail("Invalid JSON payload", {"payload": raw, "exception": str(e)})
    if not isinstance(data, dict):
        fail("Payload must be a JSON object", {"payload": data})
    return data

def parse_json_response(raw_text):
    try:
        return json.loads(raw_text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": raw_text})

def known_error_hint(msg):
    if not msg:
        return None
    if "Unknown audio effect type" in msg or ("Unknown" in msg and "effect_type" in msg):
        return "effect_type 非法，检查 references/enums/audio_effect_types.json"
    if "New segment overlaps with existing segment" in msg:
        m = re.search(r"start:\s*(\d+),\s*end:\s*(\d+)", msg)
        if m:
            return f"时间片段冲突(us): start={m.group(1)}, end={m.group(2)}；可更换 track_name 或调整 start/end"
        return "时间片段冲突；可更换 track_name 或调整 start/end"
    return None

def ensure_required_fields(action, payload):
    def require(keys):
        missing = [k for k in keys if k not in payload or payload.get(k) in (None, "")]
        if missing:
            fail(f"Missing required fields for {action}: {', '.join(missing)}", {"payload": payload})

    if action == "add_audio":
        require(["audio_url"])
    elif action == "modify_audio":
        require(["draft_id", "material_id"])
    elif action == "remove_audio":
        require(["draft_id", "material_id"])

def ensure_audio_effect_valid(payload):
    effect_type = payload.get("effect_type")
    if not effect_type:
        return
    names = load_enum_names(AUDIO_ENUM)
    if effect_type not in names:
        fail(f"Unknown audio effect type: {effect_type}", hint="effect_type 非法，检查 references/enums/audio_effect_types.json")

def call_api(action, endpoint, payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")

    url = f"{BASE_URL.rstrip('/')}/{endpoint}"
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        url=url,
        data=body,
        method='POST',
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode('utf-8', errors='replace')
            status = resp.status
    except urllib.error.HTTPError as e:
        text = e.read().decode('utf-8', errors='replace')
        fail(f"HTTP error: {e.code}", {"raw_response": text})
    except urllib.error.URLError as e:
        fail("Network error", {"reason": str(e.reason)})
    except Exception as e:
        fail("Request failed", {"exception": str(e)})

    if status < 200 or status >= 300:
        fail(f"HTTP non-2xx: {status}", {"raw_response": text})

    data = parse_json_response(text)
    if not isinstance(data, dict):
        fail("JSON response must be an object", {"response": data})

    success = data.get("success")
    error_msg = data.get("error")
    output = data.get("output")

    if success is False or (isinstance(error_msg, str) and error_msg.strip()):
        hint = known_error_hint(error_msg if isinstance(error_msg, str) else None)
        fail(error_msg if error_msg else "Business error", output if output is not None else "", hint=hint)

    if action in {"add_audio", "modify_audio"}:
        out = output if isinstance(output, dict) else None
        draft_id = out.get("draft_id") if out else None
        draft_url = out.get("draft_url") if out else None
        material_id = out.get("material_id") if out else None
        if not draft_id or not draft_url or not material_id:
            fail("Missing key fields: output.draft_id/output.draft_url/output.material_id", {"response": data})
    if action == "remove_audio":
        out = output if isinstance(output, dict) else None
        draft_id = out.get("draft_id") if out else None
        draft_url = out.get("draft_url") if out else None
        if not draft_id or not draft_url:
            fail("Missing key fields: output.draft_id/output.draft_url", {"response": data})

    print(json.dumps(data, ensure_ascii=False))

def main():
    if len(sys.argv) < 3:
        print("Usage: audio_ops.py <add_audio|modify_audio|remove_audio> '<json_payload>'")
        sys.exit(1)

    action = sys.argv[1]
    raw_payload = sys.argv[2]
    endpoint = ACTION_ENDPOINT.get(action)
    if not endpoint:
        print("Usage: audio_ops.py <add_audio|modify_audio|remove_audio> '<json_payload>'")
        sys.exit(1)

    payload = parse_payload(raw_payload)
    ensure_required_fields(action, payload)
    if action in {"add_audio", "modify_audio"}:
        ensure_audio_effect_valid(payload)
    call_api(action, endpoint, payload)

if __name__ == "__main__":
    main()
