"""Create enemies from data/enemies.json."""
from __future__ import annotations
import json
import os
import settings
from src.enemies.base_enemy import BaseEnemy


class EnemyFactory:
    _data: dict = {}

    def __init__(self, event_bus=None) -> None:
        self._eb = event_bus
        if not EnemyFactory._data:
            path = os.path.join(settings.DATA_DIR, "enemies.json")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    EnemyFactory._data = {e["id"]: e for e in raw.get("enemies", raw) if isinstance(e, dict)}
            except Exception:
                pass

    def create(self, enemy_type: str, x: float, y: float) -> BaseEnemy | None:
        stats = EnemyFactory._data.get(enemy_type, {})
        if not stats:
            stats = {"type": enemy_type, "hp": 30, "speed": 70,
                     "aggro_range": 200, "attack_range": 50, "xp_value": 8}
        enemy = BaseEnemy(x, y, stats, self._eb)
        return enemy
