"""LERP follow camera with screen shake and map-bound clamping."""
from __future__ import annotations

import random
import pygame
from pygame.math import Vector2


class Camera:
    def __init__(self, viewport_w: int, viewport_h: int) -> None:
        self.viewport = Vector2(viewport_w, viewport_h)
        self.position = Vector2(0, 0)  # top-left world coord
        self.target_pos = Vector2(0, 0)
        self.lerp_speed = 8.0
        self.bounds: pygame.Rect | None = None  # world map bounds
        self._shake_intensity = 0.0
        self._shake_time = 0.0
        self._shake_offset = Vector2(0, 0)

    def set_bounds(self, rect: pygame.Rect | None) -> None:
        self.bounds = rect

    def follow(self, world_point: Vector2) -> None:
        self.target_pos = Vector2(world_point) - self.viewport / 2

    def snap(self, world_point: Vector2) -> None:
        self.follow(world_point)
        self.position = Vector2(self.target_pos)
        self._clamp()

    def screen_shake(self, intensity: float, duration: float) -> None:
        self._shake_intensity = max(self._shake_intensity, intensity)
        self._shake_time = max(self._shake_time, duration)

    def update(self, dt: float) -> None:
        t = min(1.0, self.lerp_speed * dt)
        self.position += (self.target_pos - self.position) * t
        self._clamp()
        if self._shake_time > 0:
            self._shake_time -= dt
            mag = self._shake_intensity * (self._shake_time > 0)
            self._shake_offset = Vector2(
                random.uniform(-mag, mag), random.uniform(-mag, mag)
            )
            if self._shake_time <= 0:
                self._shake_offset = Vector2(0, 0)
        else:
            self._shake_offset = Vector2(0, 0)

    def _clamp(self) -> None:
        if not self.bounds:
            return
        max_x = max(self.bounds.left, self.bounds.right - self.viewport.x)
        max_y = max(self.bounds.top, self.bounds.bottom - self.viewport.y)
        self.position.x = max(self.bounds.left, min(self.position.x, max_x))
        self.position.y = max(self.bounds.top, min(self.position.y, max_y))

    @property
    def offset(self) -> Vector2:
        return self.position - self._shake_offset

    def apply(self, world_pos) -> Vector2:
        return Vector2(world_pos) - self.offset

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        off = self.offset
        return rect.move(-int(off.x), -int(off.y))
