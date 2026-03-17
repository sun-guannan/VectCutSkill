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
        "effect_type": "_1998",
        "start": 0,
        "end": 3.0,
        "track_name": "effect_01",
        "params": [15, 35, 45],
        "width": 1080,
        "height": 1920,
    }
    add_res = call("add_effect", add_payload)
    print("ADD =>", json.dumps(add_res, ensure_ascii=False, indent=2))

    draft_id = add_res.get("output", {}).get("draft_id")
    material_id = add_res.get("output", {}).get("material_id")
    if not draft_id or not material_id:
        return

    mod_payload = {
        "draft_id": draft_id,
        "material_id": material_id,
        "effect_type": "BOOM",
        "start": 1,
        "end": 4,
        "track_name": "effect_01",
        "params": [15, 40, 50],
        "width": 1080,
        "height": 1920,
    }
    mod_res = call("modify_effect", mod_payload)
    print("MODIFY =>", json.dumps(mod_res, ensure_ascii=False, indent=2))

    rm_payload = {"draft_id": draft_id, "material_id": material_id}
    rm_res = call("remove_effect", rm_payload)
    print("REMOVE =>", json.dumps(rm_res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()