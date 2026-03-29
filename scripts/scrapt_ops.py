#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("VECTCUT_SCRAPT_BASE_URL", "https://open.vectcut.com/scrapt")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

ACTION_TO_ENDPOINT = {
    "parse_xiaohongshu": "parse_xiaohongshu",
    "parse_douyin": "parse_douyin",
    "parse_kuaishou": "parse_kuaishou",
    "parse_bilibili": "parse_bilibili",
    "parse_tiktok": "parse_tiktok",
    "parse_youtube": "parse_youtube",
}


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


def extract_url(text):
    if not isinstance(text, str):
        return ""
    m = re.search(r"https?://[^\s]+", text)
    if m:
        return m.group(0)
    return text.strip()


def detect_action(url):
    u = url.lower()
    if "xiaohongshu.com" in u:
        return "parse_xiaohongshu"
    if "douyin.com" in u:
        return "parse_douyin"
    if "kuaishou.com" in u:
        return "parse_kuaishou"
    if "bilibili.com" in u or "b23.tv" in u:
        return "parse_bilibili"
    if "tiktok.com" in u:
        return "parse_tiktok"
    if "youtube.com" in u or "youtu.be" in u:
        return "parse_youtube"
    return ""


def request(endpoint, payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=body,
        method="POST",
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


def validate_payload(payload):
    url = extract_url(payload.get("url", ""))
    if not isinstance(url, str) or not url.strip():
        fail("url is required")
    if not url.startswith(("http://", "https://")):
        fail("url must start with http:// or https://")
    return {"url": url}


def ensure_business_ok(data):
    success = data.get("success")
    if success is False:
        fail("Parse failed: success=false", {"response": data})
    err = data.get("error")
    if isinstance(err, str) and err.strip():
        fail(err.strip(), {"response": data})
    d = data.get("data")
    if not isinstance(d, dict):
        fail("Missing key field: data", {"response": data})
    if not isinstance(d.get("platform"), str) or not d.get("platform", "").strip():
        fail("Missing key field: data.platform", {"response": data})
    if not isinstance(d.get("original_url"), str) or not d.get("original_url", "").strip():
        fail("Missing key field: data.original_url", {"response": data})
    video = d.get("video")
    if not isinstance(video, dict):
        fail("Missing key field: data.video", {"response": data})
    if not isinstance(video.get("url"), str):
        fail("Missing key field: data.video.url", {"response": data})


def execute(action, payload):
    endpoint = ACTION_TO_ENDPOINT.get(action)
    if not endpoint:
        fail("Unsupported action", {"action": action})
    body = validate_payload(payload)
    data = request(endpoint, body)
    ensure_business_ok(data)
    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <parse_auto|parse_xiaohongshu|parse_douyin|parse_kuaishou|parse_bilibili|parse_tiktok|parse_youtube> '<json_payload>'"
        )
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action == "parse_auto":
        url = extract_url(payload.get("url", ""))
        detected = detect_action(url)
        if not detected:
            fail("Cannot detect platform from url", {"url": url})
        execute(detected, payload)
        return
    execute(action, payload)


if __name__ == "__main__":
    main()
