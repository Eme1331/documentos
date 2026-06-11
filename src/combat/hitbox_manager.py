"""Spawn/despawn hitbox entities during attack active frames."""
from __future__ import annotations
import pygame
from src.entities.entity import Entity


class HitboxEntity(Entity):
    def __init__(self, rect: pygame.Rect, damage: int, attack,
                 owner: "Entity", owner_tag: str = "player") -> None:
        super().__init__()
        self.layer = "fx"
        self.rect = rect
        self.damage = damage
        self.attack = attack
        self.owner = owner
        self.owner_tag = owner_tag
        self._hit_ids: set[int] = set()

    def already_hit(self, entity: "Entity") -> bool:
        return entity.id in self._hit_ids

    def register_hit(self, entity: "Entity") -> None:
        self._hit_ids.add(entity.id)


class HitboxManager:
    def __init__(self, entity_manager) -> None:
        self._em = entity_manager
        self._active: list[HitboxEntity] = []

    def spawn(self, rect: pygame.Rect, damage: int, attack,
              owner, owner_tag: str = "player") -> HitboxEntity:
        hb = HitboxEntity(rect, damage, attack, owner, owner_tag)
        self._em.add(hb, "fx")
        self._active.append(hb)
        return hb

    def despawn_all(self) -> None:
        for hb in self._active:
            hb.active = False
        self._active.clear()

    def check_hits(self, targets: list, on_hit_callback) -> None:
        for hb in self._active:
            for target in targets:
                if hb.already_hit(target):
                    continue
                from src.entities.components.collider import Collider
                col = target.get(Collider)
                if col and hb.rect.colliderect(col.rect):
                    hb.register_hit(target)
                    on_hit_callback(target, hb)
