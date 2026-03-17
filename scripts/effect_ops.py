import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


class EffectOpsClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")).rstrip("/")
        self.api_key = api_key or os.getenv("VECTCUT_API_KEY", "")
        self.root = Path(__file__).resolve().parents[1]
        self.character_enum = self.root / "references" / "enums" / "character_effect_types.json"
        self.scene_enum = self.root / "references" / "enums" / "scene_effect_types.json"

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url=url, data=data, method="POST")
        req.add_header("Authorization", f"Bearer {self.api_key}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _get(self, path: str, query: dict | None = None) -> dict:
        q = f"?{urllib.parse.urlencode(query)}" if query else ""
        url = f"{self.base_url}/{path.lstrip('/')}{q}"
        req = urllib.request.Request(url=url, method="GET")
        req.add_header("Authorization", f"Bearer {self.api_key}")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_supported_effect_types(self) -> set[str]:
        names: set[str] = set()
        for p in (self.character_enum, self.scene_enum):
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                for item in raw.get("output", []):
                    name = item.get("name")
                    if name:
                        names.add(name)
        return names

    def add_effect(self, payload: dict) -> dict:
        et = payload.get("effect_type")
        if et and et not in self.get_supported_effect_types():
            return {"success": False, "error": f"Unknown effect type: {et}", "output": ""}
        return self._post("add_effect", payload)

    def modify_effect(self, payload: dict) -> dict:
        et = payload.get("effect_type")
        if et and et not in self.get_supported_effect_types():
            return {"success": False, "error": f"Unknown effect type: {et}", "output": ""}
        return self._post("modify_effect", payload)

    def remove_effect(self, payload: dict) -> dict:
        return self._post("remove_effect", payload)

    def get_scene_effect_types(self) -> dict:
        return self._get("get_video_scene_effect_types")

    def get_character_effect_types(self) -> dict:
        return self._get("get_video_character_effect_types")