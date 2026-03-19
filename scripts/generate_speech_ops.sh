#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <generate_speech> '<json_payload>'"
  exit 1
}

fail() {
  local error="$1"
  local output="${2:-\"\"}"
  printf '{"success":false,"error":"%s","output":%s}\n' "$error" "$output"
  exit 0
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage
[[ "$1" != "generate_speech" ]] && usage

PAYLOAD="$2"

BODY="$(python3 - "$PAYLOAD" <<'PY'
import json,sys
raw = sys.argv[1]
try:
    p = json.loads(raw)
except Exception as e:
    print(json.dumps({"_error":"Invalid JSON payload","_detail":str(e)}, ensure_ascii=False))
    sys.exit(0)
for k in ["text","provider","voice_id"]:
    if not isinstance(p.get(k), str) or not p.get(k).strip():
        print(json.dumps({"_error":f"{k} is required"}, ensure_ascii=False))
        sys.exit(0)
if p.get("provider") not in {"azure","volc","minimax","fish"}:
    print(json.dumps({"_error":"provider must be one of: azure, volc, minimax, fish"}, ensure_ascii=False)); sys.exit(0)
if p.get("provider") == "minimax":
    if not isinstance(p.get("model"), str) or not p.get("model").strip():
        print(json.dumps({"_error":"model is required when provider=minimax"}, ensure_ascii=False)); sys.exit(0)
    if p.get("model") not in {"speech-2.6-turbo","speech-2.6-hd"}:
        print(json.dumps({"_error":"model for minimax must be one of: speech-2.6-turbo, speech-2.6-hd"}, ensure_ascii=False)); sys.exit(0)
if "volume" in p and not isinstance(p.get("volume"),(int,float)):
    print(json.dumps({"_error":"volume must be a number"}, ensure_ascii=False)); sys.exit(0)
if "target_start" in p and not isinstance(p.get("target_start"),(int,float)):
    print(json.dumps({"_error":"target_start must be a number"}, ensure_ascii=False)); sys.exit(0)
if "effect_type" in p and (not isinstance(p.get("effect_type"),str) or not p.get("effect_type").strip()):
    print(json.dumps({"_error":"effect_type must be a non-empty string"}, ensure_ascii=False)); sys.exit(0)
if "effect_params" in p and not isinstance(p.get("effect_params"), list):
    print(json.dumps({"_error":"effect_params must be an array"}, ensure_ascii=False)); sys.exit(0)
print(json.dumps(p, ensure_ascii=False))
PY
)"

ERR="$(printf '%s' "$BODY" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d.get("_error", ""))' 2>/dev/null || true)"
[[ -n "$ERR" ]] && fail "$ERR"

RES="$(curl --silent --show-error --location --request POST "${BASE_URL}/generate_speech" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${BODY}")"

CHECK="$(printf '%s' "$RES" | python3 -c 'import json,sys
try:
 d=json.load(sys.stdin)
except Exception:
 print("Response is not valid JSON");sys.exit(0)
if d.get("success") is False or (isinstance(d.get("error"),str) and d.get("error").strip()):
 print(d.get("error") or "Business error");sys.exit(0)
o=d.get("output") if isinstance(d.get("output"),dict) else {}
if not o.get("audio_url"):
 print("Missing key field: output.audio_url");sys.exit(0)
has_draft_ctx = bool(o.get("draft_id") or o.get("draft_url") or o.get("material_id"))
if has_draft_ctx and not o.get("material_id"):
 print("Missing key field: output.material_id");sys.exit(0)
print("")')"
[[ -n "$CHECK" ]] && fail "$CHECK" "$(printf '%s' "$RES" | python3 -c 'import json,sys;print(json.dumps({"raw_response":sys.stdin.read()},ensure_ascii=False))')"

printf '%s\n' "$RES"