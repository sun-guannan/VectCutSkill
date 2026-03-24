#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REF_IMAGE_URL="${1:-https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/shuziren.jpg}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

echo "=== TEXT TO IMAGE ==="
PAYLOAD_1='{"prompt":"绘制一张卡通风格教学卡片，主题是光合作用中的二氧化碳循环","model":"nano_banana_pro","size":"1024x1024"}'
RES_1="$(${ROOT}/scripts/generate_ai_image_ops.sh generate_ai_image "$PAYLOAD_1")"
echo "text_to_image => ${RES_1}"

echo "=== IMAGE TO IMAGE ==="
PAYLOAD_2="{\"prompt\":\"把背景换成秋天的枫叶红色树林，画风保持一致\",\"model\":\"nano_banana_2\",\"reference_image\":\"${REF_IMAGE_URL}\",\"size\":\"1024x1024\"}"
RES_2="$(${ROOT}/scripts/generate_ai_image_ops.sh generate_ai_image "$PAYLOAD_2")"
echo "image_to_image => ${RES_2}"
