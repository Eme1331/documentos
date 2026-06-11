"""Manages all game entities: layered lists, spatial hash, deferred add/remove."""
from __future__ import annotations

from typing import TYPE_CHECKING
import settings

if TYPE_CHECKING:
    import pygame
    from src.entities.entity import Entity


class SpatialHash:
    def __init__(self, cell_size: int = settings.SPATIAL_HASH_CELL) -> None:
        self._cell = cell_size
        self._grid: dict[tuple[int, int], list] = {}

    def _cells(self, rect) -> list[tuple[int, int]]:
        x0 = rect.left // self._cell
        y0 = rect.top // self._cell
        x1 = rect.right // self._cell
        y1 = rect.bottom // self._cell
        return [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]

    def insert(self, entity) -> None:
        from src.entities.components.collider import Collider
        col = entity.get(Collider)
        if col is None:
            return
        for cell in self._cells(col.rect):
            self._grid.setdefault(cell, []).append(entity)

    def query(self, rect) -> list:
        seen: set[int] = set()
        result = []
        x0 = rect.left // self._cell
        y0 = rect.top // self._cell
        x1 = rect.right // self._cell
        y1 = rect.bottom // self._cell
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for e in self._grid.get((x, y), []):
                    if e.id not in seen:
                        seen.add(e.id)
                        result.append(e)
        return result

    def clear(self) -> None:
        self._grid.clear()


class EntityManager:
    def __init__(self) -> None:
        self._layers: dict[str, list] = {layer: [] for layer in settings.ENTITY_LAYERS}
        self._all: dict[int, object] = {}
        self._spatial = SpatialHash()
        self._to_add: list[tuple[object, str]] = []
        self._to_remove: list[int] = []

    # --- Public API ---
    def add(self, entity, layer: str = "default") -> None:
        self._to_add.append((entity, layer))

    def remove(self, entity) -> None:
        self._to_remove.append(entity.id)

    def get_all(self, layer: str | None = None):
        if layer:
            return list(self._layers.get(layer, []))
        return list(self._all.values())

    def query_rect(self, rect) -> list:
        return self._spatial.query(rect)

    def clear(self) -> None:
        for lst in self._layers.values():
            lst.clear()
        self._all.clear()
        self._spatial.clear()
        self._to_add.clear()
        self._to_remove.clear()

    # --- Frame lifecycle ---
    def flush(self) -> None:
        for entity, layer in self._to_add:
            target = self._layers.get(layer, self._layers["default"])
            target.append(entity)
            self._all[entity.id] = entity
        self._to_add.clear()

        for eid in self._to_remove:
            entity = self._all.pop(eid, None)
            if entity:
                for lst in self._layers.values():
                    try:
                        lst.remove(entity)
                    except ValueError:
                        pass
        self._to_remove.clear()

    def update(self, dt: float) -> None:
        self.flush()
        self._spatial.clear()
        for entity in list(self._all.values()):
            if entity.active and hasattr(entity, "update"):
                entity.update(dt)
            self._spatial.insert(entity)

    def fixed_update(self, fdt: float) -> None:
        for entity in list(self._all.values()):
            if entity.active and hasattr(entity, "fixed_update"):
                entity.fixed_update(fdt)

    def draw(self, surface, camera=None) -> None:
        for layer in settings.ENTITY_LAYERS:
            for entity in self._layers[layer]:
                if entity.active and hasattr(entity, "draw"):
                    entity.draw(surface, camera)
