"""Room-aware enemy and item spawning."""
from __future__ import annotations


class SpawnManager:
    def __init__(self, entity_manager, event_bus) -> None:
        self._em = entity_manager
        self._eb = event_bus

    def spawn_from_level(self, level_data: dict) -> None:
        from src.enemies.enemy_factory import EnemyFactory
        factory = EnemyFactory(self._eb)
        for entry in level_data.get("enemy_placements", []):
            enemy = factory.create(
                entry.get("type", "grunt"),
                float(entry.get("x", 200)),
                float(entry.get("y", 500)),
            )
            if enemy:
                self._em.add(enemy, "enemies")
