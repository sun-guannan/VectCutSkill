#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
URL_INPUT="${1:-https://example.com/demo.mp4}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

echo "=== CURL DEMO: get_duration ==="
CURL_PAYLOAD="{\"url\":\"${URL_INPUT}\"}"
CURL_RES_DURATION="$("${ROOT}/scripts/material_ops.sh" get_duration "${CURL_PAYLOAD}")"
echo "CURL get_duration => ${CURL_RES_DURATION}"

echo "=== CURL DEMO: get_resolution ==="
CURL_RES_RESOLUTION="$("${ROOT}/scripts/material_ops.sh" get_resolution "${CURL_PAYLOAD}")"
echo "CURL get_resolution => ${CURL_RES_RESOLUTION}"

echo "=== PYTHON DEMO ==="
python3 "${ROOT}/examples/material_ops_demo.py" "${URL_INPUT}"