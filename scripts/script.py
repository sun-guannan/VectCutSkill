import json
import os
import urllib.request
from pathlib import Path

class PerceptionClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")).rstrip("/")
        self.api_key = api_key or os.getenv("VECTCUT_API_KEY", "")
        self.skill_root = Path(__file__).resolve().parents[1]

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url=url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.api_key}")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_duration(self, media_url: str) -> dict:
        return self._post("get_duration", {"url": media_url})

    def video_detail(self, media_url: str) -> dict:
        return self._post("video_detail", {"url": media_url})

    def asr_basic(self, media_url: str) -> dict:
        return self._post("asr_basic", {"url": media_url})

    def asr_nlp(self, media_url: str) -> dict:
        return self._post("asr_nlp", {"url": media_url})

    def asr_llm(self, media_url: str) -> dict:
        return self._post("asr_llm", {"url": media_url})

    def get_supported_filter_types(self) -> list[str]:
        enum_file = self.skill_root / "references" / "enums" / "filter_types.json"
        with enum_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return [item.get("name", "") for item in data.get("items", []) if item.get("name")]

    def validate_filter_type(self, filter_type: str) -> bool:
        return filter_type in set(self.get_supported_filter_types())

    def add_filter(self, payload: dict) -> dict:
        if "filter_type" in payload and not self.validate_filter_type(payload["filter_type"]):
            return {
                "success": False,
                "error": f"Unknown filter type: {payload['filter_type']}",
                "output": "",
            }
        return self._post("add_filter", payload)