#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAW_URL="${1:-}"
PLATFORM="${2:-auto}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$RAW_URL" ]] && echo "Usage: examples/scrapt_ops_demo.sh <share_url_or_text> [platform]" && exit 1

case "${PLATFORM,,}" in
  auto) ACTION="parse_auto" ;;
  xiaohongshu) ACTION="parse_xiaohongshu" ;;
  douyin) ACTION="parse_douyin" ;;
  kuaishou) ACTION="parse_kuaishou" ;;
  bilibili) ACTION="parse_bilibili" ;;
  tiktok) ACTION="parse_tiktok" ;;
  youtube) ACTION="parse_youtube" ;;
  *) ACTION="parse_auto" ;;
esac

PAYLOAD="{\"url\":\"${RAW_URL}\"}"
RES="$(${ROOT}/scripts/scrapt_ops.sh "${ACTION}" "${PAYLOAD}")"
echo "$RES"

extract_json_string_from_text() {
  local text="$1"
  local key="$2"
  printf '%s' "$text" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

PLATFORM_VALUE="$(extract_json_string_from_text "$RES" platform)"
ORIGINAL_URL="$(extract_json_string_from_text "$RES" original_url)"
VIDEO_URL="$(extract_json_string_from_text "$RES" url)"
echo "PLATFORM => $PLATFORM_VALUE"
echo "ORIGINAL_URL => $ORIGINAL_URL"
echo "VIDEO_URL => $VIDEO_URL"
