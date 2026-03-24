#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generate_ai_image_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def run(payload):
    out = subprocess.check_output(
        [sys.executable, str(SCRIPT), "generate_ai_image", json.dumps(payload, ensure_ascii=False)],
        text=True,
    )
    data = json.loads(out)
    print(json.dumps(data, ensure_ascii=False))
    return data


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    reference_image = sys.argv[1] if len(sys.argv) > 1 else "https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/shuziren.jpg"

    text_to_image = {
        "prompt": "绘制一张卡通风格教学卡片，主题是光合作用中的二氧化碳循环",
        "model": "nano_banana_pro",
        "size": "1024x1024",
    }
    print("=== TEXT TO IMAGE ===")
    run(text_to_image)

    image_to_image = {
        "prompt": "把背景换成秋天的枫叶红色树林，画风保持一致",
        "model": "nano_banana_2",
        "reference_image": reference_image,
        "size": "1024x1024",
    }
    print("=== IMAGE TO IMAGE ===")
    run(image_to_image)


if __name__ == "__main__":
    main()
