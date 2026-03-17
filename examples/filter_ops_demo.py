import json
from pathlib import Path
import sys

CURRENT = Path(__file__).resolve()
SCRIPTS_DIR = CURRENT.parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from filter_ops import FilterOpsClient


def main():
    client = FilterOpsClient()

    add_payload = {
        "filter_type": "黑胶唱片",
        "start": 0,
        "end": 3,
        "track_name": "filter_1",
        "relative_index": 1,
        "intensity": 86
    }

    add_res = client.add_filter(add_payload)
    print("ADD =>", json.dumps(add_res, ensure_ascii=False, indent=2))

    if not add_res.get("success"):
        err = add_res.get("error", "")
        if "Unknown filter type" in err:
            valid = client.get_supported_filter_types()
            if valid:
                add_payload["filter_type"] = valid[0]
                add_res = client.add_filter(add_payload)
                print("ADD RETRY(TYPE) =>", json.dumps(add_res, ensure_ascii=False, indent=2))
        elif "New segment overlaps with existing segment" in err:
            retry_payload = client.suggest_retry_for_overlap(add_payload, err)
            add_res = client.add_filter(retry_payload)
            print("ADD RETRY(OVERLAP) =>", json.dumps(add_res, ensure_ascii=False, indent=2))

    if not add_res.get("success"):
        return

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
        "intensity": 45
    }
    mod_res = client.modify_filter(modify_payload)
    print("MODIFY =>", json.dumps(mod_res, ensure_ascii=False, indent=2))

    remove_payload = {"material_id": material_id, "draft_id": draft_id}
    rm_res = client.remove_filter(remove_payload)
    print("REMOVE =>", json.dumps(rm_res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()