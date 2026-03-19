#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = os.getenv("VECTCUT_BASE_URL",
                     "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
ROOT = Path(__file__).resolve().parents[1]
INTRO_ANIMATION_ENUM = Path(os.getenv("INTRO_ANIMATION_ENUM", str(
    ROOT / "references/enums/intro_animation_types.json")))
OUTRO_ANIMATION_ENUM = Path(os.getenv("OUTRO_ANIMATION_ENUM", str(
    ROOT / "references/enums/outro_animation_types.json")))
COMBO_ANIMATION_ENUM = Path(os.getenv("COMBO_ANIMATION_ENUM", str(
    ROOT / "references/enums/combo_animation_types.json")))
MASK_TYPE_ENUM = Path(os.getenv("MASK_TYPE_ENUM", str(
    ROOT / "references/enums/mask_type.json")))


ACTION_ENDPOINT = {
    "add_image": "add_image",
}


def fail(error, output=None):
    data = {"success": False, "error": error,
            "output": output if output is not None else ""}
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)


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


def call_api(endpoint, payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")

    intro_animation = payload.get('intro_animation')
    outro_animation = payload.get('outro_animation')
    combo_animation = payload.get('combo_animation')
    mask_type = payload.get('mask_type')
    if intro_animation not in INTRO_ANIMATION_ENUM.read_text():
        fail(f"Invalid intro_animation: {intro_animation}")
    if outro_animation not in OUTRO_ANIMATION_ENUM.read_text():
        fail(f"Invalid outro_animation: {outro_animation}")
    if combo_animation not in COMBO_ANIMATION_ENUM.read_text():
        fail(f"Invalid combo_animation: {combo_animation}")
    if mask_type not in MASK_TYPE_ENUM.read_text():
        fail(f"Invalid mask_type: {mask_type}")

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

    success = data.get('success')
    error_msg = data.get('error')
    output = data.get('output')

    if success is False or (isinstance(error_msg, str) and error_msg.strip()):
        fail(error_msg if error_msg else "Business error",
             output if output is not None else "")

    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print("Usage: image_ops.py <get_intro_animation_types|get_outro_animation_types|get_combo_animation_types|add_image> '<json_payload>'")
        sys.exit(1)

    action = sys.argv[1]
    raw_payload = sys.argv[2]
    endpoint = ACTION_ENDPOINT.get(action)
    if not endpoint:
        print("Usage: image_ops.py add_image> '<json_payload>'")
        sys.exit(1)

    payload = parse_payload(raw_payload)
    call_api(endpoint, payload)


if __name__ == '__main__':
    main()
