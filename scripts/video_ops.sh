#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <add_video> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

case "$ACTION" in
  add_video) ENDPOINT="add_video" ;;
  *) usage ;;
esac

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo
