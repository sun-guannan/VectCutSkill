#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUDIO_ENUM="${AUDIO_ENUM:-${ROOT}/references/enums/audio_effect_types.json}"

usage() {
  echo "Usage: $0 <add_audio|modify_audio|remove_audio> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

case "$ACTION" in
  add_audio) ENDPOINT="add_audio" ;;
  modify_audio) ENDPOINT="modify_audio" ;;
  remove_audio) ENDPOINT="remove_audio" ;;
  *) usage ;;
esac

if [[ "$ACTION" == "add_audio" ]]; then
  [[ -z "$(json_get audio_url "$PAYLOAD")" ]] && echo '{"success":false,"error":"Missing required fields for add_audio: audio_url","output":""}' && exit 0
fi
if [[ "$ACTION" == "modify_audio" || "$ACTION" == "remove_audio" ]]; then
  [[ -z "$(json_get draft_id "$PAYLOAD")" ]] && echo "{\"success\":false,\"error\":\"Missing required fields for ${ACTION}: draft_id\",\"output\":\"\"}" && exit 0
  [[ -z "$(json_get material_id "$PAYLOAD")" ]] && echo "{\"success\":false,\"error\":\"Missing required fields for ${ACTION}: material_id\",\"output\":\"\"}" && exit 0
fi

if [[ "$ACTION" == "add_audio" || "$ACTION" == "modify_audio" ]]; then
  ET="$(json_get effect_type "$PAYLOAD")"
  if [[ -n "$ET" ]] && ! grep -Fq "\"name\": \"${ET}\"" "$AUDIO_ENUM"; then
    echo "{\"success\":false,\"error\":\"Unknown audio effect type: ${ET}\",\"output\":\"\",\"hint\":\"effect_type 非法，检查 references/enums/audio_effect_types.json\"}"
    exit 0
  fi
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo
