import json
import os
import subprocess


def call(path: str, payload: dict) -> dict:
    base_url = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying").rstrip("/")
    api_key = os.getenv("VECTCUT_API_KEY", "")
    cmd = [
        "curl", "--silent", "--show-error", "--location", "--request", "POST",
        f"{base_url}/{path}",
        "--header", f"Authorization: Bearer {api_key}",
        "--header", "Content-Type: application/json",
        "--data-raw", json.dumps(payload, ensure_ascii=False),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"success": False, "error": result.stderr.strip() or "curl failed", "output": ""}
    return json.loads(result.stdout or "{}")


def main():
    add_payload = {
        "filter_type": "黑胶唱片",
        "start": 0,
        "end": 3,
        "track_name": "filter_1",
        "relative_index": 1,
        "intensity": 86,
    }
    add_res = call("add_filter", add_payload)
    print("ADD =>", json.dumps(add_res, ensure_ascii=False, indent=2))

    draft_id = add_res.get("output", {}).get("draft_id")
    material_id = add_res.get("output", {}).get("material_id")
    if not draft_id or not material_id:
        return

    modify_payload = {
        "material_id": material_id,
        "draft_id": draft_id,
        "filter_type": "黑胶唱片",
        "start": 3,
        "end": 8,
        "track_name": "filter_1",
        "relative_index": 1,
        "intensity": 45,
    }
    mod_res = call("modify_filter", modify_payload)
    print("MODIFY =>", json.dumps(mod_res, ensure_ascii=False, indent=2))

    remove_payload = {"material_id": material_id, "draft_id": draft_id}
    rm_res = call("remove_filter", remove_payload)
    print("REMOVE =>", json.dumps(rm_res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()