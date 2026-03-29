#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:-}"
AGENT_ID="${2:-}"
URL_VALUE="${3:-}"
TEXT_VALUE="${4:-}"
ADD_MEDIA_RAW="${5:-false}"
DRAFT_ID="${6:-}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$MODE" || -z "$AGENT_ID" || -z "$URL_VALUE" ]] && echo "Usage: examples/subtitle_ops_template.sh <smart|sta> <agent_id> <url> [text] [add_media(true|false)] [draft_id]" && exit 1

extract_json_string_from_text() {
  local text="$1"
  local key="$2"
  printf '%s' "$text" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

ADD_MEDIA="false"
if [[ "${ADD_MEDIA_RAW,,}" == "true" ]]; then
  ADD_MEDIA="true"
fi

if [[ "${MODE,,}" == "smart" ]]; then
  PAYLOAD="{\"agent_id\":\"${AGENT_ID}\",\"url\":\"${URL_VALUE}\",\"add_media\":${ADD_MEDIA}"
  [[ -n "$DRAFT_ID" ]] && PAYLOAD+=",\"draft_id\":\"${DRAFT_ID}\""
  PAYLOAD+="}"
  echo "=== GENERATE_SMART_SUBTITLE ==="
  CREATE_RES="$(${ROOT}/scripts/subtitle_template_ops.sh generate_smart_subtitle "${PAYLOAD}")"
elif [[ "${MODE,,}" == "sta" ]]; then
  [[ -z "$TEXT_VALUE" ]] && echo "text is required when mode=sta" && exit 1
  PAYLOAD="{\"agent_id\":\"${AGENT_ID}\",\"url\":\"${URL_VALUE}\",\"text\":\"${TEXT_VALUE}\",\"add_media\":${ADD_MEDIA}"
  [[ -n "$DRAFT_ID" ]] && PAYLOAD+=",\"draft_id\":\"${DRAFT_ID}\""
  PAYLOAD+="}"
  echo "=== STA_SUBTITLE ==="
  CREATE_RES="$(${ROOT}/scripts/subtitle_template_ops.sh sta_subtitle "${PAYLOAD}")"
else
  echo "mode must be smart or sta"
  exit 1
fi

echo "create => ${CREATE_RES}"
TASK_ID="$(extract_json_string_from_text "$CREATE_RES" task_id)"
[[ -z "$TASK_ID" ]] && TASK_ID="$(extract_json_string_from_text "$CREATE_RES" id)"
[[ -z "$TASK_ID" ]] && echo "No task_id, stop." && exit 1

echo "=== SUBTITLE_WAIT ==="
WAIT_PAYLOAD="{\"task_id\":\"${TASK_ID}\",\"max_poll\":120,\"poll_interval\":2}"
WAIT_RES="$(${ROOT}/scripts/subtitle_template_ops.sh subtitle_wait "${WAIT_PAYLOAD}")"
echo "wait => ${WAIT_RES}"

DRAFT_URL="$(extract_json_string_from_text "$WAIT_RES" draft_url)"
VIDEO_URL="$(extract_json_string_from_text "$WAIT_RES" video_url)"
[[ -n "$DRAFT_URL" ]] && echo "DRAFT_URL => $DRAFT_URL"
[[ -n "$VIDEO_URL" ]] && echo "VIDEO_URL => $VIDEO_URL"
