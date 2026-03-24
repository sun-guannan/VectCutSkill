#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_KEY = os.getenv("VECTCUT_API_KEY", "")
ALLOWED_PROVIDERS = {"azure", "volc", "minimax", "fish"}
MINIMAX_MODELS = {"speech-2.6-turbo", "speech-2.6-hd"}
LLM_BASE_URL = os.getenv("VECTCUT_LLM_BASE_URL", "https://open.vectcut.com/llm")


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


def request_get(url):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    req = urllib.request.Request(url=url, method="GET", headers={"Authorization": f"Bearer {API_KEY}"})
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
    return data


def validate_generate_payload(payload):
    required = ["provider", "text", "voice_id", "model"]
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


def validate_clone_payload(payload):
    file_url = payload.get("file_url")
    if not isinstance(file_url, str) or not file_url.strip():
        fail("file_url is required")
    if not (file_url.startswith("http://") or file_url.startswith("https://")):
        fail("file_url must start with http:// or https://")
    if "title" in payload and not isinstance(payload.get("title"), str):
        fail("title must be a string")


def validate_assets_payload(payload):
    if "limit" in payload and not isinstance(payload.get("limit"), int):
        fail("limit must be an integer")
    if "offset" in payload and not isinstance(payload.get("offset"), int):
        fail("offset must be an integer")
    provider = payload.get("provider")
    if provider is not None and provider not in {"fish", "minimax"}:
        fail("provider must be one of: fish, minimax")


def request_post(url, req_payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    req = urllib.request.Request(
        url=url,
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

    return data


def run_tts_generate(payload):
    validate_generate_payload(payload)
    data = request_post(f"{LLM_BASE_URL.rstrip('/')}/tts/generate", dict(payload))
    if not isinstance(data.get("provider"), str) or not data.get("provider").strip():
        fail("Missing key field: provider", {"response": data})
    if not isinstance(data.get("url"), str) or not data.get("url").strip():
        fail("Missing key field: url", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def run_fish_clone(payload):
    validate_clone_payload(payload)
    req_payload = {k: v for k, v in payload.items() if k in {"file_url", "title"}}
    data = request_post(f"{LLM_BASE_URL.rstrip('/')}/tts/fish/clone_voice", req_payload)
    if not data.get("voice_id"):
        fail("Missing key field: voice_id", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def run_voice_assets(payload):
    validate_assets_payload(payload)
    query = {k: payload[k] for k in ["limit", "offset", "provider"] if k in payload}
    qs = urllib.parse.urlencode(query)
    url = f"{LLM_BASE_URL.rstrip('/')}/tts/voice_assets"
    if qs:
        url = f"{url}?{qs}"
    data = request_get(url)
    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <tts_generate|fish_clone|voice_assets> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action == "tts_generate":
        run_tts_generate(payload)
        return
    if action == "fish_clone":
        run_fish_clone(payload)
        return
    if action == "voice_assets":
        run_voice_assets(payload)
        return
    print(f"Usage: {sys.argv[0]} <tts_generate|fish_clone|voice_assets> '<json_payload>'")
    sys.exit(1)


if __name__ == "__main__":
    main()
