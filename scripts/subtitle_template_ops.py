#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")


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


def get_root_result(data):
    if isinstance(data.get("result"), dict):
        return data["result"]
    return data


def get_root_output(data):
    root = get_root_result(data)
    if isinstance(root.get("output"), dict):
        return root["output"]
    return {}


def get_root_error(data):
    root = get_root_result(data)
    err = root.get("error")
    if isinstance(err, str) and err.strip():
        return err.strip()
    err = data.get("error")
    if isinstance(err, str) and err.strip():
        return err.strip()
    return ""


def get_task_id(data):
    candidates = []
    root = get_root_result(data)
    output = get_root_output(data)
    for obj, key in [(data, "task_id"), (data, "id"), (root, "task_id"), (root, "id"), (output, "task_id"), (output, "id")]:
        value = obj.get(key) if isinstance(obj, dict) else None
        candidates.append(value)
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_status(data):
    root = get_root_result(data)
    output = get_root_output(data)
    for value in [output.get("status"), root.get("status"), data.get("status")]:
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return ""


def is_failure_status(status):
    return status in {"failed", "failure", "error"}


def has_final_draft(data):
    output = get_root_output(data)
    draft_id = output.get("draft_id")
    draft_url = output.get("draft_url")
    return isinstance(draft_id, str) and draft_id.strip() or isinstance(draft_url, str) and draft_url.strip()


def validate_common_fields(payload, need_text, agent_prefix):
    for key in ["agent_id", "url"]:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(f"{key} is required")
    agent_id = payload["agent_id"].strip()
    if not agent_id.startswith(agent_prefix):
        fail(f"agent_id must start with {agent_prefix}")
    if not payload["url"].startswith(("http://", "https://")):
        fail("url must start with http:// or https://")
    if "draft_id" in payload and payload["draft_id"] is not None:
        if not isinstance(payload["draft_id"], str) or not payload["draft_id"].strip():
            fail("draft_id must be a non-empty string")
    if "add_media" in payload and not isinstance(payload["add_media"], bool):
        fail("add_media must be a boolean")
    if need_text:
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            fail("text is required")


def validate_status_payload(payload):
    task_id = payload.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        fail("task_id is required")


def ensure_business_ok(data):
    error_msg = get_root_error(data)
    if error_msg:
        fail(error_msg, get_root_output(data) if get_root_output(data) else data)


def call_generate_smart_subtitle(payload):
    validate_common_fields(payload, need_text=False, agent_prefix="asr_")
    body = {k: v for k, v in payload.items() if k in {"agent_id", "url", "draft_id", "add_media"}}
    data = request("POST", "generate_smart_subtitle", payload=body)
    ensure_business_ok(data)
    task_id = get_task_id(data)
    if not task_id:
        fail("Missing key field: task_id", {"response": data})
    return data


def call_sta_subtitle(payload):
    validate_common_fields(payload, need_text=True, agent_prefix="sta_")
    body = {k: v for k, v in payload.items() if k in {"agent_id", "url", "text", "draft_id", "add_media"}}
    data = request("POST", "sta_subtitle", payload=body)
    ensure_business_ok(data)
    task_id = get_task_id(data)
    if not task_id:
        fail("Missing key field: task_id", {"response": data})
    return data


def call_status(payload):
    validate_status_payload(payload)
    data = request("GET", "smart_subtitle_task_status", query={"task_id": payload["task_id"]})
    ensure_business_ok(data)
    status = normalize_status(data)
    if is_failure_status(status):
        fail("Subtitle task failed", {"task_id": payload["task_id"], "response": data})
    if status in {"success", "completed", "done"} and not has_final_draft(data):
        fail("Missing key field: output.draft_id or output.draft_url", {"response": data})
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
        if has_final_draft(res):
            print(json.dumps(res, ensure_ascii=False))
            return
        time.sleep(float(poll_interval))
    fail("Subtitle polling timeout", {"task_id": task_id, "last_status": last})


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <generate_smart_subtitle|sta_subtitle|smart_subtitle_task_status|subtitle_wait> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action == "generate_smart_subtitle":
        print(json.dumps(call_generate_smart_subtitle(payload), ensure_ascii=False))
        return
    if action == "sta_subtitle":
        print(json.dumps(call_sta_subtitle(payload), ensure_ascii=False))
        return
    if action == "smart_subtitle_task_status":
        print(json.dumps(call_status(payload), ensure_ascii=False))
        return
    if action == "subtitle_wait":
        call_wait(payload)
        return
    print(f"Usage: {sys.argv[0]} <generate_smart_subtitle|sta_subtitle|smart_subtitle_task_status|subtitle_wait> '<json_payload>'")
    sys.exit(1)


if __name__ == "__main__":
    main()
