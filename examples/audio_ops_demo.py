#!/usr/bin/env python3
import json
import os
import random
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audio_ops.py"
BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying").rstrip("/")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

ENUM_PATH = ROOT / "references/enums/audio_effect_types.json"

def create_draft():
    url = f"{BASE_URL}/create_draft"
    req = urllib.request.Request(
        url=url,
        data=json.dumps({"name": "demo", "width": 1080, "height": 1920}, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))

def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action} => {out.strip()}")
    return json.loads(out)

def load_effect_items(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    return [x for x in items if isinstance(x, dict) and x.get("name")]

def build_effect_params(item: dict):
    params = item.get("params") or []
    if not isinstance(params, list):
        return []
    values = []
    for p in params:
        if not isinstance(p, dict):
            continue
        if "default_value" in p and isinstance(p["default_value"], (int, float)):
            v = p["default_value"]
        else:
            mn = p.get("min_value")
            mx = p.get("max_value")
            if isinstance(mn, (int, float)) and isinstance(mx, (int, float)):
                v = (mn + mx) / 2
            else:
                v = 50
        values.append(int(round(v)))
    return values

def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        sys.exit(1)

    print("=== DEMO CATEGORY: audio ===")

    create_res = create_draft()
    print('CREATE => ' + json.dumps(create_res, ensure_ascii=False))
    draft_id = ((create_res.get('output') or {}).get('draft_id')) if isinstance(create_res, dict) else None
    if not draft_id:
        print('No draft_id, stop.')
        sys.exit(1)

    items = load_effect_items(ENUM_PATH)
    if not items:
        print("No audio effect types found in enum file.")
        sys.exit(1)
    item = random.choice(items)
    effect_type = item["name"]
    effect_params = build_effect_params(item)
    print(f"Use effect_type: {effect_type}, effect_params: {effect_params}")

    add_payload = {
        "draft_id": draft_id,
        "audio_url": "https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        "target_start": 0,
        "volume": 0,
        "track_name": "audio_main",
        "effect_type": effect_type,
        "effect_params": effect_params,
        "width": 1080,
        "height": 1920,
    }
    add_res = run_action("add_audio", add_payload)
    material_id = ((add_res.get("output") or {}).get("material_id")) if isinstance(add_res, dict) else None
    if not material_id:
        print("No material_id, skip modify/remove.")
        return

    payload = {
        "draft_id": draft_id,
        "material_id": material_id,
        "volume": -10,
        "effect_type": effect_type,
        "effect_params": effect_params,
    }
    run_action("modify_audio", payload)

    payload = {
        "draft_id": draft_id,
        "material_id": material_id,
    }
    run_action("remove_audio", payload)

if __name__ == "__main__":
    main()
