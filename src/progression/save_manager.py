"""Save/load game state to JSON slots."""
from __future__ import annotations
import json
import os
import datetime
import settings


class SaveManager:
    def __init__(self) -> None:
        os.makedirs(settings.SAVES_DIR, exist_ok=True)

    def _path(self, slot: int) -> str:
        return os.path.join(settings.SAVES_DIR, f"slot_{slot}.json")

    def save(self, slot: int, data: dict) -> bool:
        data["timestamp"] = datetime.datetime.utcnow().isoformat()
        try:
            with open(self._path(slot), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def load(self, slot: int) -> dict | None:
        try:
            with open(self._path(slot), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def list_slots(self) -> dict[int, dict]:
        result = {}
        for i in range(1, 4):
            data = self.load(i)
            if data:
                result[i] = data
        return result

    def delete(self, slot: int) -> None:
        path = self._path(slot)
        if os.path.exists(path):
            os.remove(path)

    def build_save_data(self, character_id: str, level: int, xp: int,
                        current_level_id: str, checkpoints: dict,
                        completed: list, skill_ids: list,
                        inventory: dict, playtime: float) -> dict:
        return {
            "character": character_id,
            "level": level,
            "xp": xp,
            "current_level_id": current_level_id,
            "checkpoints_reached": checkpoints,
            "levels_completed": completed,
            "unlocked_skills": skill_ids,
            "inventory": inventory,
            "playtime_seconds": playtime,
        }
