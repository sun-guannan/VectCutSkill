#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENT_ID="${1:-}"
VIDEO_URL="${2:-}"
TITLE="${3:-}"
TEXT_CONTENT="${4:-}"
COVER_URL="${5:-}"
NAME="${6:-}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$AGENT_ID" || -z "$VIDEO_URL" ]] && echo "Usage: examples/koubo_ops_demo.sh <agent_id> <video_url> [title] [text_content] [cover_url] [name]" && exit 1

extract_json_string_from_text() {
  local text="$1"
  local key="$2"
  printf '%s' "$text" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

PAYLOAD="{\"agent_id\":\"${AGENT_ID}\",\"params\":{\"video_url\":[\"${VIDEO_URL}\"]"
[[ -n "$TITLE" ]] && PAYLOAD+=",\"title\":\"${TITLE}\""
[[ -n "$TEXT_CONTENT" ]] && PAYLOAD+=",\"text_content\":\"${TEXT_CONTENT}\""
[[ -n "$COVER_URL" ]] && PAYLOAD+=",\"cover\":[\"${COVER_URL}\"]"
[[ -n "$NAME" ]] && PAYLOAD+=",\"name\":\"${NAME}\""
PAYLOAD+="}}"

echo "=== SUBMIT_AGENT_TASK ==="
SUBMIT_RES="$(${ROOT}/scripts/koubo_ops.sh submit_agent_task "${PAYLOAD}")"
echo "submit => ${SUBMIT_RES}"

TASK_ID="$(extract_json_string_from_text "$SUBMIT_RES" task_id)"
[[ -z "$TASK_ID" ]] && TASK_ID="$(extract_json_string_from_text "$SUBMIT_RES" id)"
[[ -z "$TASK_ID" ]] && echo "No task_id, stop." && exit 1

echo "=== KOUBO_WAIT ==="
WAIT_PAYLOAD="{\"task_id\":\"${TASK_ID}\",\"max_poll\":120,\"poll_interval\":2}"
WAIT_RES="$(${ROOT}/scripts/koubo_ops.sh koubo_wait "${WAIT_PAYLOAD}")"
echo "wait => ${WAIT_RES}"

DRAFT_URL="$(extract_json_string_from_text "$WAIT_RES" draft_url)"
VIDEO_RESULT_URL="$(extract_json_string_from_text "$WAIT_RES" video_url)"
[[ -n "$DRAFT_URL" ]] && echo "DRAFT_URL => $DRAFT_URL"
[[ -n "$VIDEO_RESULT_URL" ]] && echo "VIDEO_URL => $VIDEO_RESULT_URL"
