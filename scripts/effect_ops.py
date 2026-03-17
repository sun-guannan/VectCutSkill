import json
import os
import subprocess
from pathlib import Path


class EffectOpsClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")).rstrip("/")
        self.api_key = api_key or os.getenv("VECTCUT_API_KEY", "")
        self.root = Path(__file__).resolve().parents[1]
        self.character_enum = self.root / "references" / "enums" / "character_effect_types.json"
        self.scene_enum = self.root / "references" / "enums" / "scene_effect_types.json"

    def _curl(self, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        cmd = [
            "curl", "--silent", "--show-error", "--location", "--request", method,
            url,
            "--header", f"Authorization: Bearer {self.api_key}",
        ]
        if payload is not None:
            cmd.extend(["--header", "Content-Type: application/json", "--data-raw", json.dumps(payload, ensure_ascii=False)])
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip() or "curl failed", "output": ""}
        try:
            return json.loads(result.stdout or "{}")
        except json.JSONDecodeError:
            return {"success": False, "error": "invalid json response", "output": result.stdout}

    def get_supported_effect_types(self) -> set[str]:
        names: set[str] = set()
        for p in (self.character_enum, self.scene_enum):
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                for item in raw.get("items", []):
                    name = item.get("name")
                    if name:
                        names.add(name)
        return names

    def add_effect(self, payload: dict) -> dict:
        et = payload.get("effect_type")
        if et and et not in self.get_supported_effect_types():
            return {"success": False, "error": f"Unknown effect type: {et}", "output": ""}
        return self._curl("POST", "add_effect", payload)

    def modify_effect(self, payload: dict) -> dict:
        et = payload.get("effect_type")
        if et and et not in self.get_supported_effect_types():
            return {"success": False, "error": f"Unknown effect type: {et}", "output": ""}
        return self._curl("POST", "modify_effect", payload)

    def remove_effect(self, payload: dict) -> dict:
        return self._curl("POST", "remove_effect", payload)

    def get_scene_effect_types(self) -> dict:
        return self._curl("GET", "get_video_scene_effect_types")

    def get_character_effect_types(self) -> dict:
        return self._curl("GET", "get_video_character_effect_types")