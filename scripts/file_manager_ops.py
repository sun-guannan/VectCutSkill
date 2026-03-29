#!/usr/bin/env python3
import base64
import hashlib
import hmac
import json
import os
import sys
from email.utils import formatdate
from urllib.parse import quote
import urllib.error
import urllib.request

BASE_URL = os.getenv("VECTCUT_FILE_BASE_URL", os.getenv("STS_BASE_URL", "https://open.vectcut.com")).rstrip("/")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
OSS_ENDPOINT = os.getenv("MP4_OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")


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


def request_json(path, payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    url = f"{BASE_URL}/{path.lstrip('/')}"
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
        fail(f"HTTP error: {e.code}", {"endpoint": path, "raw_response": text})
    except urllib.error.URLError as e:
        fail("Network error", {"endpoint": path, "reason": str(e.reason)})
    except Exception as e:
        fail("Request failed", {"endpoint": path, "exception": str(e)})
    if status < 200 or status >= 300:
        fail(f"HTTP non-2xx: {status}", {"endpoint": path, "raw_response": text})
    data = parse_json_response(text)
    if data.get("success") is False:
        fail("Business failed", {"endpoint": path, "response": data})
    return data


def validate_upload_init_payload(payload):
    file_name = payload.get("file_name")
    file_size_bytes = payload.get("file_size_bytes")
    if not isinstance(file_name, str) or not file_name.strip():
        fail("file_name is required")
    if not isinstance(file_size_bytes, int) or file_size_bytes <= 0:
        fail("file_size_bytes must be a positive integer")
    return {"file_name": file_name.strip(), "file_size_bytes": int(file_size_bytes)}


def validate_upload_complete_payload(payload):
    object_key = payload.get("object_key")
    if not isinstance(object_key, str) or not object_key.strip():
        fail("object_key is required")
    return {"object_key": object_key.strip()}


def call_upload_init(payload):
    body = validate_upload_init_payload(payload)
    data = request_json("/sts/upload/init", body)
    if not isinstance(data.get("credentials"), dict):
        fail("Missing key field: credentials", {"response": data})
    if not isinstance(data.get("bucket_name"), str) or not data.get("bucket_name", "").strip():
        fail("Missing key field: bucket_name", {"response": data})
    if not isinstance(data.get("object_key"), str) or not data.get("object_key", "").strip():
        fail("Missing key field: object_key", {"response": data})
    return data


def call_upload_complete(payload):
    body = validate_upload_complete_payload(payload)
    data = request_json("/sts/upload/complete", body)
    if not isinstance(data.get("public_signed_url"), str) or not data.get("public_signed_url", "").strip():
        fail("Missing key field: public_signed_url", {"response": data})
    return data


def upload_via_sts(init_data, file_path):
    creds = init_data.get("credentials") if isinstance(init_data.get("credentials"), dict) else {}
    access_key_id = creds.get("AccessKeyId")
    access_key_secret = creds.get("AccessKeySecret")
    security_token = creds.get("SecurityToken")
    object_key = init_data.get("object_key")
    bucket_name = init_data.get("bucket_name")
    if not all(isinstance(x, str) and x.strip() for x in [access_key_id, access_key_secret, security_token, object_key, bucket_name]):
        fail("Missing key fields in init_data", {"init_data": init_data})

    gmt_date = formatdate(usegmt=True)
    content_type = "application/octet-stream"
    canonical_headers = f"x-oss-security-token:{security_token}\n"
    canonical_resource = f"/{bucket_name}/{object_key}"
    string_to_sign = f"PUT\n\n{content_type}\n{gmt_date}\n{canonical_headers}{canonical_resource}"
    digest = hmac.new(access_key_secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha1).digest()
    signature = base64.b64encode(digest).decode("utf-8")

    encoded_key = quote(object_key, safe="/-_.~")
    upload_url = f"https://{bucket_name}.{OSS_ENDPOINT}/{encoded_key}"
    headers = {
        "Date": gmt_date,
        "Content-Type": content_type,
        "x-oss-security-token": security_token,
        "Authorization": f"OSS {access_key_id}:{signature}",
    }

    try:
        with open(file_path, "rb") as f:
            data_bytes = f.read()
    except Exception as e:
        fail("Cannot read local file", {"file_path": file_path, "exception": str(e)})

    req = urllib.request.Request(url=upload_url, data=data_bytes, method="PUT", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            text = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        fail(f"oss put_object failed: {e.code}", {"raw_response": text, "upload_url": upload_url})
    except urllib.error.URLError as e:
        fail("oss put_object network error", {"reason": str(e.reason), "upload_url": upload_url})
    except Exception as e:
        fail("oss put_object failed", {"exception": str(e), "upload_url": upload_url})
    if status not in (200, 201):
        fail(f"oss put_object failed: {status}", {"raw_response": text, "upload_url": upload_url})
    return object_key


def call_upload_file(payload):
    file_path = payload.get("file_path")
    if not isinstance(file_path, str) or not file_path.strip():
        fail("file_path is required")
    file_path = file_path.strip()
    if not os.path.exists(file_path):
        fail("Local file not found", {"file_path": file_path})
    if not os.path.isfile(file_path):
        fail("file_path must be a regular file", {"file_path": file_path})

    file_name = payload.get("file_name")
    if not isinstance(file_name, str) or not file_name.strip():
        file_name = os.path.basename(file_path)
    file_size_bytes = os.path.getsize(file_path)

    init_data = call_upload_init({"file_name": file_name, "file_size_bytes": int(file_size_bytes)})
    object_key = upload_via_sts(init_data, file_path)
    complete_data = call_upload_complete({"object_key": object_key})

    result = {
        "success": True,
        "base_url": BASE_URL,
        "bucket_name": init_data.get("bucket_name"),
        "local_file": file_path,
        "object_key": object_key,
        "file_size_bytes": file_size_bytes,
        "public_signed_url": complete_data.get("public_signed_url"),
    }
    return result


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <upload_init|upload_complete|upload_file> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])

    if action == "upload_init":
        print(json.dumps(call_upload_init(payload), ensure_ascii=False))
        return
    if action == "upload_complete":
        print(json.dumps(call_upload_complete(payload), ensure_ascii=False))
        return
    if action == "upload_file":
        print(json.dumps(call_upload_file(payload), ensure_ascii=False))
        return

    print(f"Usage: {sys.argv[0]} <upload_init|upload_complete|upload_file> '<json_payload>'")
    sys.exit(1)


if __name__ == "__main__":
    main()
