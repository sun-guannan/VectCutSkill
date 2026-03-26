#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <generate_ai_video|ai_video_task_status> '<json_payload>'"
  exit 1
}

fail() {
  local error="$1"
  local output="${2:-\"\"}"
  printf '{"success":false,"error":"%s","output":%s}\n' "$error" "$output"
  exit 0
}

extract_json_string() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

extract_json_number() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\(\.[0-9]\+\)\?\).*/\1/p"
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

if [[ "$ACTION" == "generate_ai_video" ]]; then
  PROMPT="$(extract_json_string prompt)"
  MODEL="$(extract_json_string model)"
  RESOLUTION="$(extract_json_string resolution)"
  GENERATE_AUDIO="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"generate_audio"[[:space:]]*:[[:space:]]*\(true\|false\).*/\1/p')"
  GEN_DURATION="$(extract_json_number gen_duration)"
  [[ -z "$PROMPT" || -z "$RESOLUTION" ]] && fail "prompt/resolution is required"
  [[ -z "$MODEL" ]] && MODEL="veo3.1"
  [[ ! "$MODEL" =~ ^(veo3.1|veo3.1-pro|seedance-1.5-pro|grok-video-3)$ ]] && fail "model must be one of: veo3.1, veo3.1-pro, seedance-1.5-pro, grok-video-3"
  [[ ! "$RESOLUTION" =~ ^[0-9]+x[0-9]+$ ]] && fail "resolution must match format: <width>x<height>"
  [[ -n "$GEN_DURATION" && ! "$GEN_DURATION" =~ ^[0-9]+(\.[0-9]+)?$ ]] && fail "gen_duration must be a number"
  [[ -n "$GENERATE_AUDIO" && ! "$GENERATE_AUDIO" =~ ^(true|false)$ ]] && fail "generate_audio must be a boolean"
  if [[ "$PAYLOAD" != *'"model"'* ]]; then
    PAYLOAD="$(printf '%s' "$PAYLOAD" | sed 's/}[[:space:]]*$/,\"model\":\"veo3.1\"}/')"
  fi
  curl --silent --show-error --location --request POST "${BASE_URL}/llm/generate_ai_video" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$PAYLOAD"
  echo
  exit 0
fi

if [[ "$ACTION" == "ai_video_task_status" ]]; then
  TASK_ID="$(extract_json_string task_id)"
  [[ -z "$TASK_ID" ]] && fail "task_id is required"
  curl --silent --show-error --location --request GET "${BASE_URL}/cut_jianying/aivideo/task_status?task_id=${TASK_ID}" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json"
  echo
  exit 0
fi

usage
