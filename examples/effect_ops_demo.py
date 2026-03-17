import json
from pathlib import Path
import sys

CURRENT = Path(__file__).resolve()
SCRIPTS_DIR = CURRENT.parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from effect_ops import EffectOpsClient


def main():
    client = EffectOpsClient()
    add_payload = {
        "effect_type": "_1998",
        "start": 0,
        "end": 3.0,
        "track_name": "effect_01",
        "params": [15, 35, 45],
        "width": 1080,
        "height": 1920
    }
    add_res = client.add_effect(add_payload)
    print("ADD =>", json.dumps(add_res, ensure_ascii=False, indent=2))

    if not add_res.get("success"):
        return

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
        "height": 1920
    }
    mod_res = client.modify_effect(mod_payload)
    print("MODIFY =>", json.dumps(mod_res, ensure_ascii=False, indent=2))

    rm_payload = {"draft_id": draft_id, "material_id": material_id}
    rm_res = client.remove_effect(rm_payload)
    print("REMOVE =>", json.dumps(rm_res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()