#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

INTRO_ANIMATION_ENUM="${INTRO_ANIMATION_ENUM:-${ROOT}/references/enums/intro_animation_types.json}"
OUTRO_ANIMATION_ENUM="${OUTRO_ANIMATION_ENUM:-${ROOT}/references/enums/outro_animation_types.json}"
COMBO_ANIMATION_ENUM="${COMBO_ANIMATION_ENUM:-${ROOT}/references/enums/combo_animation_types.json}"
MASK_TYPE_ENUM="${MASK_TYPE_ENUM:-${ROOT}/references/enums/mask_types.json}"

usage() {
  echo "Usage: $0 <add_image> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p"
}

case "$ACTION" in
  add_image) ENDPOINT="add_image" ;;
  *) usage ;;
esac

IMAGE_URL="$(json_get image_url "$PAYLOAD")"
[[ -z "$IMAGE_URL" ]] && echo '{"success":false,"error":"Missing required fields for add_image: image_url","output":""}' && exit 0

intro_animation="$(json_get intro_animation "$PAYLOAD")"
if [[ -n "$intro_animation" ]] && ! grep -Fq "\"name\": \"${intro_animation}\"" "$INTRO_ANIMATION_ENUM"; then
  echo "{\"success\":false,\"error\":\"Unknown intro animation: ${intro_animation}\",\"output\":\"\",\"hint\":\"检查 references/enums/intro_animation_types.json\"}"
  exit 0
fi

outro_animation="$(json_get outro_animation "$PAYLOAD")"
if [[ -n "$outro_animation" ]] && ! grep -Fq "\"name\": \"${outro_animation}\"" "$OUTRO_ANIMATION_ENUM"; then
  echo "{\"success\":false,\"error\":\"Unknown outro animation: ${outro_animation}\",\"output\":\"\",\"hint\":\"检查 references/enums/outro_animation_types.json\"}"
  exit 0
fi

combo_animation="$(json_get combo_animation "$PAYLOAD")"
if [[ -n "$combo_animation" ]] && ! grep -Fq "\"name\": \"${combo_animation}\"" "$COMBO_ANIMATION_ENUM"; then
  echo "{\"success\":false,\"error\":\"Unknown combo animation: ${combo_animation}\",\"output\":\"\",\"hint\":\"检查 references/enums/combo_animation_types.json\"}"
  exit 0
fi

mask_type="$(json_get mask_type "$PAYLOAD")"
if [[ -n "$mask_type" ]] && ! grep -Fq "\"name\": \"${mask_type}\"" "$MASK_TYPE_ENUM"; then
  echo "{\"success\":false,\"error\":\"Unknown mask type: ${mask_type}\",\"output\":\"\",\"hint\":\"检查 references/enums/mask_types.json\"}"
  exit 0
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo

