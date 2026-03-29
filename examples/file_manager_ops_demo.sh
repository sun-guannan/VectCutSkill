#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILE_PATH="${1:-}"
FILE_NAME="${2:-}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$FILE_PATH" ]] && echo "Usage: examples/file_manager_ops_demo.sh <local_file_path> [file_name]" && exit 1

PAYLOAD="{\"file_path\":\"${FILE_PATH}\""
[[ -n "$FILE_NAME" ]] && PAYLOAD+=",\"file_name\":\"${FILE_NAME}\""
PAYLOAD+="}"

RES="$(${ROOT}/scripts/file_manager_ops.sh upload_file "$PAYLOAD")"
echo "$RES"

extract_json_string_from_text() {
  local text="$1"
  local key="$2"
  printf '%s' "$text" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

OBJECT_KEY="$(extract_json_string_from_text "$RES" object_key)"
PUBLIC_URL="$(extract_json_string_from_text "$RES" public_signed_url)"
echo "OBJECT_KEY => $OBJECT_KEY"
echo "PUBLIC_SIGNED_URL => $PUBLIC_URL"
