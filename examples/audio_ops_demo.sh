#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

pick_random_audio_effect() {
  local file="${ROOT}/references/enums/audio_effect_types.json"
  grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$file" \
    | sed 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' \
    | awk 'BEGIN{srand()} {a[NR]=$0} END{if(NR>0) print a[int(rand()*NR)+1]}'
}

pick_default_params_for_effect() {
  local effect_type="$1"
  python - "$effect_type" <<'PY'
import json, sys
effect_type = sys.argv[1]
with open("references/enums/audio_effect_types.json", "r", encoding="utf-8") as f:
    data = json.load(f)
items = data.get("items", [])
item = next((x for x in items if isinstance(x, dict) and x.get("name") == effect_type), None)
params = (item or {}).get("params") or []
vals = []
for p in params:
    if not isinstance(p, dict):
        continue
    if isinstance(p.get("default_value"), (int, float)):
        v = p["default_value"]
    elif isinstance(p.get("min_value"), (int, float)) and isinstance(p.get("max_value"), (int, float)):
        v = (p["min_value"] + p["max_value"]) / 2
    else:
        v = 50
    vals.append(int(round(v)))
print(json.dumps(vals, ensure_ascii=False))
PY
}

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

echo "=== CREATE DRAFT ==="
CREATE_RES="$(curl --silent --show-error --location --request POST "${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}/create_draft" \
  --header "Authorization: Bearer ${VECTCUT_API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw '{"name":"demo","width":1080,"height":1920}')"
echo "CREATE => ${CREATE_RES}"
DRAFT_ID="$(json_get draft_id "$CREATE_RES")"
[[ -z "$DRAFT_ID" ]] && echo "No draft_id, stop." && exit 1

EFFECT_TYPE="$(pick_random_audio_effect)"
EFFECT_PARAMS="$(pick_default_params_for_effect "$EFFECT_TYPE")"
echo "Use effect_type: ${EFFECT_TYPE}, effect_params: ${EFFECT_PARAMS}"

echo "=== OPS DEMO: add_audio ==="
PAYLOAD='{"draft_id":"__DRAFT_ID__","audio_url":"https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh","target_start":0,"volume":0,"track_name":"audio_main","effect_type":"__EFFECT_TYPE__","effect_params":__EFFECT_PARAMS__,"width":1080,"height":1920}'
PAYLOAD="${PAYLOAD//__DRAFT_ID__/${DRAFT_ID}}"
PAYLOAD="${PAYLOAD//__EFFECT_TYPE__/${EFFECT_TYPE}}"
PAYLOAD="${PAYLOAD//__EFFECT_PARAMS__/${EFFECT_PARAMS}}"
RES="$("${ROOT}/scripts/audio_ops.sh" add_audio "$PAYLOAD")"
echo "add_audio => $RES"

MATERIAL_ID="$(json_get material_id "$RES")"
[[ -z "$MATERIAL_ID" ]] && echo "No material_id, skip modify/remove." && exit 0

echo "=== OPS DEMO: modify_audio ==="
PAYLOAD='{"draft_id":"__DRAFT_ID__","material_id":"__MATERIAL_ID__","volume":-10,"effect_type":"__EFFECT_TYPE__","effect_params":__EFFECT_PARAMS__}'
PAYLOAD="${PAYLOAD//__DRAFT_ID__/${DRAFT_ID}}"
PAYLOAD="${PAYLOAD//__MATERIAL_ID__/${MATERIAL_ID}}"
PAYLOAD="${PAYLOAD//__EFFECT_TYPE__/${EFFECT_TYPE}}"
PAYLOAD="${PAYLOAD//__EFFECT_PARAMS__/${EFFECT_PARAMS}}"
RES="$("${ROOT}/scripts/audio_ops.sh" modify_audio "$PAYLOAD")"
echo "modify_audio => $RES"

echo "=== OPS DEMO: remove_audio ==="
PAYLOAD='{"draft_id":"__DRAFT_ID__","material_id":"__MATERIAL_ID__"}'
PAYLOAD="${PAYLOAD//__DRAFT_ID__/${DRAFT_ID}}"
PAYLOAD="${PAYLOAD//__MATERIAL_ID__/${MATERIAL_ID}}"
RES="$("${ROOT}/scripts/audio_ops.sh" remove_audio "$PAYLOAD")"
echo "remove_audio => $RES"
