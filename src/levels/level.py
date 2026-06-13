"""Active level container."""
from __future__ import annotations
import pygame
from src.levels.tile_map import TileMap
from src.entities.entity_manager import EntityManager
import settings


class Level:
    def __init__(self, data: dict, event_bus) -> None:
        self.id: str = data.get("id", "level_01")
        self.name: str = data.get("name", "Unknown")
        self.boss_id: str = data.get("boss_id", "")
        self.spawn_point: tuple = tuple(data.get("spawn_point", [128, 500]))
        self.data = data

        ambient = tuple(data.get("ambient_color", [8, 8, 20]))
        tmx_file = data.get("tilemap_file") or data.get("map_file")
        self.tile_map = TileMap(tmx_file, ambient_color=ambient)

        self.entity_manager = EntityManager()
        self._event_bus = event_bus

        self.checkpoints: list = []
        self.secrets: list = []
        self._setup_checkpoints(data)
        self._spawn_default_grunts()

    def _setup_checkpoints(self, data: dict) -> None:
        from src.levels.checkpoint import Checkpoint
        for cp in data.get("checkpoints", []):
            pos = cp.get("position", cp.get("coords", [200, 500]))
            c = Checkpoint(cp["id"], float(pos[0]), float(pos[1]),
                           self._event_bus)
            self.checkpoints.append(c)
            self.entity_manager.add(c, "default")

    def _spawn_default_grunts(self) -> None:
        from src.enemies.grunt import Grunt
        floor_y = (self.tile_map.height_tiles - 3) * self.tile_map.tile_size
        # Spawn positions spread across the level on the floor
        spawn_xs = [300, 550, 820, 1100, 1400, 1700, 2000, 2300]
        for sx in spawn_xs:
            grunt = Grunt(float(sx), float(floor_y - 42),
                          event_bus=self._event_bus,
                          tile_rects=self.tile_map.collision_rects)
            self.entity_manager.add(grunt, "enemies")

    def update(self, dt: float) -> None:
        self.entity_manager.update(dt)

    def fixed_update(self, fdt: float) -> None:
        self.entity_manager.fixed_update(fdt)

    def draw(self, surface: pygame.Surface, camera) -> None:
        self.tile_map.render_layer(surface, settings.LAYER_BACKGROUND, camera)
        self.tile_map.render_layer(surface, settings.LAYER_MIDGROUND, camera)
        self.tile_map.render_layer(surface, settings.LAYER_COLLISION, camera)
        self.entity_manager.draw(surface, camera)
        self.tile_map.render_layer(surface, settings.LAYER_FOREGROUND, camera)
