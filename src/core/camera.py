"""LERP follow camera with screen shake and map-bound clamping."""
from __future__ import annotations

import random
import pygame
from pygame.math import Vector2


class Camera:
    def __init__(self, viewport_size: tuple | int, world_size: tuple | None = None,
                 viewport_h: int = 0) -> None:
        if isinstance(viewport_size, (tuple, list)):
            vw, vh = viewport_size
        else:
            vw, vh = viewport_size, viewport_h
        self.viewport = Vector2(vw, vh)
        if world_size:
            ww, wh = world_size
            self.bounds = pygame.Rect(0, 0, ww, wh)
        else:
            self.bounds = None
        self.position = Vector2(0, 0)
        self.target_pos = Vector2(0, 0)
        self.lerp_speed = 8.0
        self._shake_intensity = 0.0
        self._shake_time = 0.0
        self._shake_offset = Vector2(0, 0)

    def set_bounds(self, rect: pygame.Rect | None) -> None:
        self.bounds = rect

    def follow(self, target, dt: float = 0.0) -> None:
        if isinstance(target, pygame.Rect):
            world_point = Vector2(target.centerx, target.centery)
        else:
            world_point = Vector2(target)
        self.target_pos = world_point - self.viewport / 2
        if dt > 0:
            self.update(dt)

    def apply_point(self, pos: tuple) -> tuple:
        off = self.offset
        return (int(pos[0] - off.x), int(pos[1] - off.y))

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
