#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT_ID="${1:-}"
RESOLUTION="${2:-1080P}"
FRAMERATE="${3:-30}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$DRAFT_ID" ]] && echo "Usage: examples/generate_video_ops_demo.sh <draft_id> [resolution] [framerate]" && exit 1

echo "=== GENERATE_VIDEO ==="
GEN_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"resolution\":\"${RESOLUTION}\",\"framerate\":\"${FRAMERATE}\"}"
GEN_RES="$(${ROOT}/scripts/generate_video_ops.sh generate_video "${GEN_PAYLOAD}")"
echo "generate_video => ${GEN_RES}"

TASK_ID="$(printf '%s' "$GEN_RES" | python3 -c 'import json,sys;print(((json.load(sys.stdin).get("output") or {}).get("task_id")) or "")')"
[[ -z "$TASK_ID" ]] && echo "No task_id, stop." && exit 1

echo "=== RENDER_WAIT ==="
WAIT_PAYLOAD="{\"task_id\":\"${TASK_ID}\"}"
WAIT_RES="$(${ROOT}/scripts/generate_video_ops.sh render_wait "${WAIT_PAYLOAD}")"
echo "render_wait => ${WAIT_RES}"

PLAY_URL="$(printf '%s' "$WAIT_RES" | python3 -c 'import json,sys;print(((json.load(sys.stdin).get("output") or {}).get("result")) or "")')"
if [[ -n "$PLAY_URL" ]]; then
  echo "PLAY_URL => $PLAY_URL"
fi