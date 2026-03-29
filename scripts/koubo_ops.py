#!/usr/bin/env python3
import json
import os
import sys
import time
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
TEMPLATE_ENUM_PATH = Path(__file__).resolve().parents[1] / "references" / "enums" / "koubo_template_types.json"


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


def parse_json_response(text):
    try:
        data = json.loads(text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": text})
    if not isinstance(data, dict):
        fail("JSON response must be an object", {"response": data})
    return data


def request(method, endpoint, payload=None, query=None):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=body,
        method=method,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        fail(f"HTTP error: {e.code}", {"raw_response": text})
    except urllib.error.URLError as e:
        fail("Network error", {"reason": str(e.reason)})
    except Exception as e:
        fail("Request failed", {"exception": str(e)})
    if status < 200 or status >= 300:
        fail(f"HTTP non-2xx: {status}", {"raw_response": text})
    return parse_json_response(text)


def get_root_output(data):
    output = data.get("output")
    if isinstance(output, dict):
        return output
    return {}


def get_root_error(data):
    error = data.get("error")
    if isinstance(error, str) and error.strip():
        return error.strip()
    return ""


def extract_task_id(data):
    output = get_root_output(data)
    for value in [data.get("task_id"), data.get("id"), output.get("task_id"), output.get("id")]:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_status(data):
    status = data.get("status")
    if isinstance(status, str) and status.strip():
        return status.strip().lower()
    output = get_root_output(data)
    status = output.get("status")
    if isinstance(status, str) and status.strip():
        return status.strip().lower()
    return ""


def is_failure_status(status):
    return status in {"failed", "failure", "error"}


def has_draft_output(data):
    output = get_root_output(data)
    draft_id = output.get("draft_id")
    draft_url = output.get("draft_url")
    return (isinstance(draft_id, str) and draft_id.strip()) or (isinstance(draft_url, str) and draft_url.strip())


def load_koubo_templates():
    try:
        raw = TEMPLATE_ENUM_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        fail("Failed to load koubo template enums", {"path": str(TEMPLATE_ENUM_PATH), "exception": str(e)})
    items = data.get("items")
    if not isinstance(items, list):
        fail("Invalid koubo template enums: items must be array", {"path": str(TEMPLATE_ENUM_PATH)})
    mapping = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        tid = item.get("id")
        if isinstance(tid, str) and tid.strip():
            mapping[tid.strip()] = item
    return mapping


def _hint_required(value):
    if isinstance(value, str):
        return ("必填" in value) and ("选填" not in value)
    if isinstance(value, list) and value:
        return _hint_required(value[0])
    return False


def required_fields_from_example(params_example):
    required = set()
    if not isinstance(params_example, dict):
        return required
    for key, value in params_example.items():
        if _hint_required(value):
            required.add(key)
    return required


def is_non_empty_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return True


def validate_submit_payload(payload):
    agent_id = payload.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id.strip():
        fail("agent_id is required")
    agent_id = agent_id.strip()
    templates = load_koubo_templates()
    template = templates.get(agent_id)
    if template is None:
        fail("agent_id is not found in koubo_template_types.json", {"agent_id": agent_id})
    params = payload.get("params")
    if not isinstance(params, dict):
        fail("params is required and must be an object")

    required_fields = required_fields_from_example(template.get("params_example"))
    for field in required_fields:
        if field not in params or not is_non_empty_value(params.get(field)):
            fail(f"params.{field} is required for this template", {"agent_id": agent_id, "required_fields": sorted(required_fields)})

    video_url = params.get("video_url")
    if video_url is not None:
        if not isinstance(video_url, list) or len(video_url) != 1:
            fail("params.video_url must be an array with exactly one url")
        if not isinstance(video_url[0], str) or not video_url[0].startswith(("http://", "https://")):
            fail("params.video_url[0] must be a valid url")

    cover = params.get("cover")
    if cover is not None:
        if not isinstance(cover, list):
            fail("params.cover must be an array<string>")
        for item in cover:
            if not isinstance(item, str) or not item.startswith(("http://", "https://")):
                fail("params.cover must contain valid urls")

    kongjing_urls = params.get("kongjing_urls")
    if kongjing_urls is not None:
        if not isinstance(kongjing_urls, list) or len(kongjing_urls) < 1 or len(kongjing_urls) > 10:
            fail("params.kongjing_urls must be an array<string> with size 1~10")
        for item in kongjing_urls:
            if not isinstance(item, str) or not item.startswith(("http://", "https://")):
                fail("params.kongjing_urls must contain valid urls")

    for key in ["title", "text_content", "name", "author"]:
        value = params.get(key)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            fail(f"params.{key} must be a non-empty string")


def validate_status_payload(payload):
    task_id = payload.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        fail("task_id is required")


def ensure_business_ok(data):
    error_msg = get_root_error(data)
    if error_msg:
        fail(error_msg, get_root_output(data) if get_root_output(data) else data)


def call_submit(payload):
    validate_submit_payload(payload)
    body = {"agent_id": payload["agent_id"], "params": payload["params"]}
    data = request("POST", "agent/submit_agent_task", payload=body)
    ensure_business_ok(data)
    task_id = extract_task_id(data)
    if not task_id:
        fail("Missing key field: task_id", {"response": data})
    return data


def call_status(payload):
    validate_status_payload(payload)
    data = request("GET", "agent/task_status", query={"task_id": payload["task_id"]})
    ensure_business_ok(data)
    status = normalize_status(data)
    if is_failure_status(status):
        fail("Koubo task failed", {"task_id": payload["task_id"], "response": data})
    return data


def call_wait(payload):
    validate_status_payload(payload)
    max_poll = payload.get("max_poll", 60)
    poll_interval = payload.get("poll_interval", 2)
    if not isinstance(max_poll, int) or max_poll <= 0:
        fail("max_poll must be a positive integer")
    if not isinstance(poll_interval, (int, float)) or poll_interval <= 0:
        fail("poll_interval must be a positive number")
    task_id = payload["task_id"]
    last = None
    for _ in range(max_poll):
        res = call_status({"task_id": task_id})
        last = res
        status = normalize_status(res)
        if status == "success" and has_draft_output(res):
            print(json.dumps(res, ensure_ascii=False))
            return
        time.sleep(float(poll_interval))
    fail("Koubo polling timeout", {"task_id": task_id, "last_status": last})


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <submit_agent_task|agent_task_status|koubo_wait> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action == "submit_agent_task":
        print(json.dumps(call_submit(payload), ensure_ascii=False))
        return
    if action == "agent_task_status":
        print(json.dumps(call_status(payload), ensure_ascii=False))
        return
    if action == "koubo_wait":
        call_wait(payload)
        return
    print(f"Usage: {sys.argv[0]} <submit_agent_task|agent_task_status|koubo_wait> '<json_payload>'")
    sys.exit(1)


if __name__ == "__main__":
    main()
