#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

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

echo "=== OPS DEMO: add_video_keyframe ==="
PAYLOAD='{"draft_id":"__DRAFT_ID__","track_name":"video_main","property_type":"alpha","time":0,"value":"1.0","property_types":["alpha","scale_x"],"times":[0,2],"values":["1.0","0.8"]}'
PAYLOAD="${PAYLOAD//__DRAFT_ID__/${DRAFT_ID}}"
RES="$("${ROOT}/scripts/keyframe_ops.sh" add_video_keyframe "$PAYLOAD")"
echo "add_video_keyframe => $RES"
