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
                 gravity: float = 0.0, tile_rects: list | None = None) -> None:
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
        self._tile_rects = tile_rects or []
        self._surf = pygame.Surface(size, pygame.SRCALPHA)
        self._surf.fill(color)

    def update(self, dt: float) -> None:
        tr = self.get(Transform)
        col = self.get(Collider)

        if self._gravity:
            tr.velocity.y += self._gravity * dt

        # Move X
        tr.position.x += tr.velocity.x * dt
        col.rect.x = int(tr.position.x)
        for tile in self._tile_rects:
            if col.rect.colliderect(tile):
                if tr.velocity.x > 0:
                    col.rect.right = tile.left
                else:
                    col.rect.left = tile.right
                tr.position.x = float(col.rect.x)
                tr.velocity.x = 0

        # Move Y
        tr.position.y += tr.velocity.y * dt
        col.rect.y = int(tr.position.y)
        for tile in self._tile_rects:
            if col.rect.colliderect(tile):
                if tr.velocity.y > 0:
                    col.rect.bottom = tile.top
                    tr.position.y = float(col.rect.y)
                    self.active = False
                elif tr.velocity.y < 0:
                    col.rect.top = tile.bottom
                    tr.position.y = float(col.rect.y)
                tr.velocity.y = 0

        self._elapsed += dt
        if self._elapsed >= self.lifetime:
            self.active = False

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        tr = self.get(Transform)
        pos = (int(tr.position.x), int(tr.position.y))
        if camera:
            pos = camera.apply_point(pos)
        surface.blit(self._surf, pos)
