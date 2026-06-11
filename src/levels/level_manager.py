"""Level load/unload lifecycle."""
from __future__ import annotations
import json
import os
import settings


class LevelManager:
    def __init__(self, event_bus) -> None:
        self._eb = event_bus
        self.current: "Level | None" = None

    def load(self, level_id: str) -> "Level":
        from src.levels.level import Level
        from src.levels.spawn_manager import SpawnManager

        path = os.path.join(settings.LEVELS_DIR, f"{level_id}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"id": level_id, "name": level_id,
                    "spawn_point": [128, 500], "ambient_color": [8, 8, 20]}

        if self.current:
            self.unload()

        level = Level(data, self._eb)
        spawner = SpawnManager(level.entity_manager, self._eb)
        spawner.spawn_from_level(data)
        self.current = level
        return level

    def unload(self) -> None:
        if self.current:
            self.current.entity_manager.clear()
            self.current = None
