#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
ALLOWED_PROVIDERS = {"azure", "volc", "minimax", "fish"}
MINIMAX_MODELS = {"speech-2.6-turbo", "speech-2.6-hd"}


def fail(error, output=None):
    print(json.dumps({"success": False, "error": error, "output": output if output is not None else ""}, ensure_ascii=False))
    sys.exit(0)


def parse_payload(raw):
    try:
        data = json.loads(raw)
    except Exception as e:
        fail("Invalid JSON payload", {"payload": raw, "exception": str(e)})
    if not isinstance(data, dict):
        fail("Payload must be a JSON object", {"payload": data})
    return data


def validate_payload(payload):
    required = ["text", "provider", "voice_id"]
    for key in required:
        v = payload.get(key)
        if not isinstance(v, str) or not v.strip():
            fail(f"{key} is required")

    provider = payload.get("provider")
    if provider not in ALLOWED_PROVIDERS:
        fail("provider must be one of: azure, volc, minimax, fish")

    model = payload.get("model")
    if provider == "minimax":
        if not isinstance(model, str) or not model.strip():
            fail("model is required when provider=minimax")
        if model not in MINIMAX_MODELS:
            fail("model for minimax must be one of: speech-2.6-turbo, speech-2.6-hd")

    if "volume" in payload and not isinstance(payload.get("volume"), (int, float)):
        fail("volume must be a number")
    if "target_start" in payload and not isinstance(payload.get("target_start"), (int, float)):
        fail("target_start must be a number")
    if "effect_type" in payload:
        if not isinstance(payload.get("effect_type"), str) or not payload.get("effect_type").strip():
            fail("effect_type must be a non-empty string")
        if "effect_params" in payload and not isinstance(payload.get("effect_params"), list):
            fail("effect_params must be an array")


def request_post(payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    req_payload = dict(payload)
    req = urllib.request.Request(
        url=f"{BASE_URL.rstrip('/')}/generate_speech",
        data=json.dumps(req_payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        fail(f"HTTP error: {e.code}", {"raw_response": e.read().decode("utf-8", errors="replace")})
    except urllib.error.URLError as e:
        fail("Network error", {"reason": str(e.reason)})

    if status < 200 or status >= 300:
        fail(f"HTTP non-2xx: {status}", {"raw_response": text})

    try:
        data = json.loads(text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": text})

    if data.get("success") is False or (isinstance(data.get("error"), str) and data.get("error").strip()):
        fail(data.get("error") or "Business error", data.get("output") if data.get("output") is not None else data)

    output = data.get("output") if isinstance(data.get("output"), dict) else {}
    if not output.get("audio_url"):
        fail("Missing key field: output.audio_url", {"response": data})
    has_draft_ctx = bool(output.get("draft_id") or output.get("draft_url") or output.get("material_id"))
    if has_draft_ctx and not output.get("material_id"):
        fail("Missing key field: output.material_id", {"response": data})

    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <generate_speech> '<json_payload>'")
        sys.exit(1)
    if sys.argv[1] != "generate_speech":
        print(f"Usage: {sys.argv[0]} <generate_speech> '<json_payload>'")
        sys.exit(1)
    payload = parse_payload(sys.argv[2])
    validate_payload(payload)
    request_post(payload)


if __name__ == "__main__":
    main()