#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"
ROOT="${ROOT_PATH:-$(pwd)}"

INTRO_ANIMATION_ENUM="${INTRO_ANIMATION_ENUM:-${ROOT}/references/enums/intro_animation_types.json}"
OUTRO_ANIMATION_ENUM="${OUTRO_ANIMATION_ENUM:-${ROOT}/references/enums/outro_animation_types.json}"
COMBO_ANIMATION_ENUM="${COMBO_ANIMATION_ENUM:-${ROOT}/references/enums/combo_animation_types.json}"
MASK_TYPE_ENUM="${MASK_TYPE_ENUM:-${ROOT}/references/enums/mask_type.json}"

usage() {
  echo "Usage: $0 <get_intro_animation_types|get_outro_animation_types|get_combo_animation_types|add_image> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

case "$ACTION" in
  add_image) ENDPOINT="add_image" ;;
  *) usage ;;
esac

intro_animation=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"intro_animation"[[:space:]]*:[[:space:]]*"$[^"]*$".*/\1/p')
if [[ -n "$intro_animation" ]] && ! grep -Fq "\"name\": \"$intro_animation\"" "$INTRO_ANIMATION_ENUM"; then
  echo "{\"success\":false,\"error\":\"Unknown intro animation: $intro_animation\",\"output\":\"\"}"
  exit 0
fi

outro_animation=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"outro_animation"[[:space:]]*:[[:space:]]*"$[^"]*$".*/\1/p')
if [[ -n "$outro_animation" ]] && ! grep -Fq "\"name\": \"$outro_animation\"" "$OUTRO_ANIMATION_ENUM"; then
  echo "{\"success\":false,\"error\":\"Unknown outro animation: $outro_animation\",\"output\":\"\"}"
  exit 0
fi

combo_animation=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"combo_animation"[[:space:]]*:[[:space:]]*"$[^"]*$".*/\1/p')
if [[ -n "$combo_animation" ]] && ! grep -Fq "\"name\": \"$combo_animation\"" "$COMBO_ANIMATION_ENUM"; then
  echo "{\"success\":false,\"error\":\"Unknown combo animation: $combo_animation\",\"output\":\"\"}"
  exit 0
fi


mask_type=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"mask_type"[[:space:]]*:[[:space:]]*"$[^"]*$".*/\1/p')
if [[ -n "$mask_type" ]] && ! grep -Fq "\"name\": \"$mask_type\"" "$MASK_TYPE_ENUM"; then
  echo "{\"success\":false,\"error\":\"Unknown mask type: $mask_type\",\"output\":\"\"}"
  exit 0
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo

