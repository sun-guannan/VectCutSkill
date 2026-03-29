#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_FILE_BASE_URL:-${STS_BASE_URL:-https://open.vectcut.com}}"
API_KEY="${VECTCUT_API_KEY:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  echo "Usage: $0 <upload_init|upload_complete|upload_file> '<json_payload>'"
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
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p"
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

if [[ "$ACTION" == "upload_init" ]]; then
  FILE_NAME="$(extract_json_string file_name)"
  FILE_SIZE="$(extract_json_number file_size_bytes)"
  [[ -z "$FILE_NAME" ]] && fail "file_name is required"
  [[ -z "$FILE_SIZE" || "$FILE_SIZE" -le 0 ]] && fail "file_size_bytes must be positive integer"
  BODY="{\"file_name\":\"$FILE_NAME\",\"file_size_bytes\":$FILE_SIZE}"
  curl --silent --show-error --location --request POST "${BASE_URL}/sts/upload/init" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$BODY"
  echo
  exit 0
fi

if [[ "$ACTION" == "upload_complete" ]]; then
  OBJECT_KEY="$(extract_json_string object_key)"
  [[ -z "$OBJECT_KEY" ]] && fail "object_key is required"
  BODY="{\"object_key\":\"$OBJECT_KEY\"}"
  curl --silent --show-error --location --request POST "${BASE_URL}/sts/upload/complete" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$BODY"
  echo
  exit 0
fi

if [[ "$ACTION" == "upload_file" ]]; then
  python3 "${ROOT}/scripts/file_manager_ops.py" upload_file "$PAYLOAD"
  exit 0
fi

usage
