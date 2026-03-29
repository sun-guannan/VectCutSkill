#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_SCRAPT_BASE_URL:-https://open.vectcut.com/scrapt}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <parse_auto|parse_xiaohongshu|parse_douyin|parse_kuaishou|parse_bilibili|parse_tiktok|parse_youtube> '<json_payload>'"
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

detect_action() {
  local url_lower
  url_lower="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
  if [[ "$url_lower" == *"xiaohongshu.com"* ]]; then echo "parse_xiaohongshu"; return; fi
  if [[ "$url_lower" == *"douyin.com"* ]]; then echo "parse_douyin"; return; fi
  if [[ "$url_lower" == *"kuaishou.com"* ]]; then echo "parse_kuaishou"; return; fi
  if [[ "$url_lower" == *"bilibili.com"* || "$url_lower" == *"b23.tv"* ]]; then echo "parse_bilibili"; return; fi
  if [[ "$url_lower" == *"tiktok.com"* ]]; then echo "parse_tiktok"; return; fi
  if [[ "$url_lower" == *"youtube.com"* || "$url_lower" == *"youtu.be"* ]]; then echo "parse_youtube"; return; fi
  echo ""
}

extract_first_url() {
  local raw="$1"
  local first
  first="$(printf '%s' "$raw" | grep -Eo 'https?://[^[:space:]]+' | head -n 1 || true)"
  if [[ -n "$first" ]]; then
    printf '%s' "$first"
  else
    printf '%s' "$raw"
  fi
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"
URL_VALUE="$(extract_json_string url)"
URL_VALUE="$(extract_first_url "$URL_VALUE")"
[[ -z "$URL_VALUE" ]] && fail "url is required"
[[ ! "$URL_VALUE" =~ ^https?:// ]] && fail "url must start with http:// or https://"

if [[ "$ACTION" == "parse_auto" ]]; then
  ACTION="$(detect_action "$URL_VALUE")"
  [[ -z "$ACTION" ]] && fail "Cannot detect platform from url" "{\"url\":\"$URL_VALUE\"}"
fi

case "$ACTION" in
  parse_xiaohongshu|parse_douyin|parse_kuaishou|parse_bilibili|parse_tiktok|parse_youtube)
    ;;
  *)
    usage
    ;;
esac

BODY="{\"url\":\"$URL_VALUE\"}"
curl --silent --show-error --location --request POST "${BASE_URL}/${ACTION}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "$BODY"
echo
