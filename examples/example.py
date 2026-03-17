import argparse
import json
from skill_me.scripts.perception_client import PerceptionClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--mode", choices=["full", "audio_only", "video_only"], default="full")
    args = parser.parse_args()

    c = PerceptionClient()
    out = {"duration": c.get_duration(args.url)}

    if args.mode in ("full", "video_only"):
        out["video_detail"] = c.video_detail(args.url)

    if args.mode in ("full", "audio_only"):
        out["asr_basic"] = c.asr_basic(args.url)
        out["asr_nlp"] = c.asr_nlp(args.url)
        out["asr_llm"] = c.asr_llm(args.url)

    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()