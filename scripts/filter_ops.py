import json
import os
import re
import subprocess
from pathlib import Path


class FilterOpsClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")).rstrip("/")
        self.api_key = api_key or os.getenv("VECTCUT_API_KEY", "")
        self.skill_root = Path(__file__).resolve().parents[1]
        self.enum_file = self.skill_root / "references" / "enums" / "filter_types.json"

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        cmd = [
            "curl", "--silent", "--show-error", "--location", "--request", "POST",
            url,
            "--header", f"Authorization: Bearer {self.api_key}",
            "--header", "Content-Type: application/json",
            "--data-raw", json.dumps(payload, ensure_ascii=False),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip() or "curl failed", "output": ""}
        try:
            return json.loads(result.stdout or "{}")
        except json.JSONDecodeError:
            return {"success": False, "error": "invalid json response", "output": result.stdout}

    def get_supported_filter_types(self) -> list[str]:
        with self.enum_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return [x.get("name", "") for x in raw.get("items", []) if x.get("name")]

    def validate_filter_type(self, filter_type: str) -> bool:
        return filter_type in set(self.get_supported_filter_types())

    def add_filter(self, payload: dict) -> dict:
        ft = payload.get("filter_type", "")
        if not self.validate_filter_type(ft):
            return {"success": False, "error": f"Unknown filter type: {ft}", "output": ""}
        return self._post("add_filter", payload)

    def modify_filter(self, payload: dict) -> dict:
        ft = payload.get("filter_type")
        if ft is not None and not self.validate_filter_type(ft):
            return {"success": False, "error": f"Unknown filter type: {ft}", "output": ""}
        return self._post("modify_filter", payload)

    def remove_filter(self, payload: dict) -> dict:
        return self._post("remove_filter", payload)

    @staticmethod
    def parse_overlap_range_us(error_text: str) -> tuple[int, int] | None:
        m = re.search(r"\[start:\s*(\d+),\s*end:\s*(\d+)\]", error_text or "")
        if not m:
            return None
        return int(m.group(1)), int(m.group(2))

    @staticmethod
    def suggest_retry_for_overlap(payload: dict, error_text: str) -> dict:
        new_payload = dict(payload)
        r = FilterOpsClient.parse_overlap_range_us(error_text)
        if r is None:
            return new_payload
        _, overlap_end_us = r
        if "start" in new_payload:
            current_start_sec = float(new_payload.get("start", 0))
            suggested_start_sec = max(current_start_sec, overlap_end_us / 1_000_000 + 0.001)
            duration = float(new_payload.get("end", suggested_start_sec + 1) - current_start_sec)
            new_payload["start"] = round(suggested_start_sec, 3)
            new_payload["end"] = round(suggested_start_sec + max(duration, 0.1), 3)
        else:
            new_payload["track_name"] = f'{new_payload.get("track_name", "filter_main")}_retry'
        return new_payload