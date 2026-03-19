#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEXT="${1:-今天的视频，就给大家带来一个福利。}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

PAYLOAD="$(python3 - "$TEXT" <<'PY'
import json,sys
print(json.dumps({
  "text": sys.argv[1],
  "provider": "minimax",
  "model": "speech-2.6-turbo",
  "voice_id": "audiobook_male_1",
  "volume": 10,
  "target_start": 3,
  "effect_type": "麦霸",
  "effect_params": [45, 80]
}, ensure_ascii=False))
PY
)"

echo "=== SHELL DEMO ==="
RES="$(${ROOT}/scripts/generate_speech_ops.sh generate_speech "${PAYLOAD}")"
echo "generate_speech => ${RES}"

echo "=== PYTHON DEMO ==="
python3 "${ROOT}/examples/generate_speech_demo.py" "${TEXT}"