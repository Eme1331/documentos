"""Projectile entity."""
from __future__ import annotations
import pygame
from src.entities.entity import Entity
from src.entities.components.transform import Transform
from src.entities.components.collider import Collider


class Projectile(Entity):
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 damage: int, owner_tag: str = "player",
                 color=(0, 255, 231), size=(8, 8),
                 lifetime: float = 3.0, can_pierce: bool = False,
                 gravity: float = 0.0) -> None:
        super().__init__()
        self.layer = "projectiles"
        self.add_tag("projectile")
        self.add_tag(owner_tag)

        tr = Transform(pygame.math.Vector2(x, y), pygame.math.Vector2(vx, vy))
        col = Collider(pygame.Rect(0, 0, size[0], size[1]))
        self.add(tr)
        self.add(col)

        self.damage = damage
        self.can_pierce = can_pierce
        self.lifetime = lifetime
        self._elapsed = 0.0
        self._color = color
        self._gravity = gravity
        self._surf = pygame.Surface(size, pygame.SRCALPHA)
        self._surf.fill(color)

    def update(self, dt: float) -> None:
        tr = self.get(Transform)
        if self._gravity:
            tr.velocity.y += self._gravity * dt
        tr.position += tr.velocity * dt
        col = self.get(Collider)
        col.rect.topleft = (int(tr.position.x), int(tr.position.y))

        self._elapsed += dt
        if self._elapsed >= self.lifetime:
            self.active = False

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        tr = self.get(Transform)
        pos = (int(tr.position.x), int(tr.position.y))
        if camera:
            pos = camera.apply_point(pos)
        surface.blit(self._surf, pos)
