#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
ALLOWED_MODELS = {"veo3.1", "veo3.1-pro", "seedance-1.5-pro", "grok-video-3"}
SIZE_RE = re.compile(r"^\d+x\d+$")


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


def request(method, url, payload=None):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    req = urllib.request.Request(url=url, data=body, method=method, headers=headers)
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


def validate_generate(payload):
    for key in ["prompt", "resolution"]:
        if not isinstance(payload.get(key), str) or not payload.get(key).strip():
            fail(f"{key} is required")
    model = payload.get("model", "veo3.1")
    if not isinstance(model, str) or not model.strip():
        fail("model must be a non-empty string")
    if model not in ALLOWED_MODELS:
        fail("model must be one of: veo3.1, veo3.1-pro, seedance-1.5-pro, grok-video-3")
    payload["model"] = model
    if not SIZE_RE.match(payload["resolution"]):
        fail("resolution must match format: <width>x<height>")
    if "images" in payload:
        images = payload["images"]
        if not isinstance(images, list):
            fail("images must be an array<string>")
        for u in images:
            if not isinstance(u, str) or not u.startswith(("http://", "https://")):
                fail("images must contain valid urls")
    if "gen_duration" in payload:
        if not isinstance(payload["gen_duration"], (int, float)):
            fail("gen_duration must be a number")
    if "generate_audio" in payload and not isinstance(payload["generate_audio"], bool):
        fail("generate_audio must be a boolean")


def validate_status(payload):
    if not isinstance(payload.get("task_id"), str) or not payload.get("task_id").strip():
        fail("task_id is required")


def run_generate(payload):
    validate_generate(payload)
    data = request("POST", f"{BASE_URL.rstrip('/')}/llm/generate_ai_video", payload)
    if isinstance(data, dict):
        task_id = data.get("task_id")
        if not task_id and isinstance(data.get("output"), dict):
            task_id = data["output"].get("task_id")
        if not task_id:
            fail("Missing key field: task_id", {"response": data})
    else:
        fail("JSON response must be an object", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def run_status(payload):
    validate_status(payload)
    qs = urllib.parse.urlencode({"task_id": payload["task_id"]})
    data = request("GET", f"{BASE_URL.rstrip('/')}/cut_jianying/aivideo/task_status?{qs}")
    if not isinstance(data, dict):
        fail("JSON response must be an object", {"response": data})
    status = str(data.get("status", "")).lower()
    if status == "completed" and not data.get("video_url"):
        fail("Missing key field: video_url", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <generate_ai_video|ai_video_task_status> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action == "generate_ai_video":
        run_generate(payload)
        return
    if action == "ai_video_task_status":
        run_status(payload)
        return
    print(f"Usage: {sys.argv[0]} <generate_ai_video|ai_video_task_status> '<json_payload>'")
    sys.exit(1)


if __name__ == "__main__":
    main()
