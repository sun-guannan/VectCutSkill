#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <submit_agent_task|agent_task_status|koubo_wait> '<json_payload>'"
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

extract_json_string_from_text() {
  local text="$1"
  local key="$2"
  printf '%s' "$text" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

post_json() {
  local endpoint="$1"
  local body="$2"
  curl --silent --show-error --location --request POST "${BASE_URL}/${endpoint}" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$body"
}

get_status() {
  local task_id="$1"
  curl --silent --show-error --location --request GET "${BASE_URL}/agent/task_status?task_id=${task_id}" \
    --header "Authorization: Bearer ${API_KEY}"
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

if [[ "$ACTION" == "submit_agent_task" ]]; then
  AGENT_ID="$(extract_json_string agent_id)"
  VIDEO_URL="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"video_url"[[:space:]]*:[[:space:]]*\[[[:space:]]*"\([^"]*\)".*/\1/p')"
  [[ -z "$AGENT_ID" ]] && fail "agent_id is required"
  [[ -z "$VIDEO_URL" ]] && fail "params.video_url with one url is required"
  [[ ! "$VIDEO_URL" =~ ^https?:// ]] && fail "params.video_url[0] must be a valid url"
  RES="$(post_json "agent/submit_agent_task" "$PAYLOAD")"
  TASK_ID="$(extract_json_string_from_text "$RES" task_id)"
  [[ -z "$TASK_ID" ]] && TASK_ID="$(extract_json_string_from_text "$RES" id)"
  [[ -z "$TASK_ID" ]] && fail "Missing key field: task_id" "$RES"
  printf '%s\n' "$RES"
  exit 0
fi

if [[ "$ACTION" == "agent_task_status" ]]; then
  TASK_ID="$(extract_json_string task_id)"
  [[ -z "$TASK_ID" ]] && fail "task_id is required"
  get_status "$TASK_ID"
  echo
  exit 0
fi

if [[ "$ACTION" == "koubo_wait" ]]; then
  TASK_ID="$(extract_json_string task_id)"
  MAX_POLL="$(extract_json_number max_poll)"
  POLL_INTERVAL="$(extract_json_number poll_interval)"
  [[ -z "$TASK_ID" ]] && fail "task_id is required"
  [[ -z "$MAX_POLL" ]] && MAX_POLL=60
  [[ -z "$POLL_INTERVAL" ]] && POLL_INTERVAL=2
  LAST=""
  for ((i=0;i<MAX_POLL;i++)); do
    LAST="$(get_status "$TASK_ID")"
    STATUS="$(extract_json_string_from_text "$LAST" status)"
    DRAFT_ID="$(extract_json_string_from_text "$LAST" draft_id)"
    DRAFT_URL="$(extract_json_string_from_text "$LAST" draft_url)"
    STATUS_LOWER="$(printf '%s' "$STATUS" | tr '[:upper:]' '[:lower:]')"
    if [[ "$STATUS_LOWER" == "failed" || "$STATUS_LOWER" == "failure" || "$STATUS_LOWER" == "error" ]]; then
      fail "Koubo task failed" "$LAST"
    fi
    if [[ "$STATUS_LOWER" == "success" && ( -n "$DRAFT_ID" || -n "$DRAFT_URL" ) ]]; then
      printf '%s\n' "$LAST"
      exit 0
    fi
    sleep "$POLL_INTERVAL"
  done
  fail "Koubo polling timeout" "$LAST"
fi

usage
