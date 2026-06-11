"""Dynamic neon lighting via surface blending."""
from __future__ import annotations
import pygame
import math
from dataclasses import dataclass, field


@dataclass
class LightSource:
    x: float
    y: float
    color: tuple = (0, 200, 255)
    radius: float = 150.0
    intensity: float = 1.0


def _make_radial(radius: int, color: tuple) -> pygame.Surface:
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(255 * (1.0 - r / radius) ** 1.5)
        c = (*color, min(255, alpha))
        pygame.draw.circle(surf, c, (radius, radius), r)
    return surf


class LightingSystem:
    DARKNESS_ALPHA = 160

    def __init__(self, screen_size: tuple) -> None:
        self._size = screen_size
        self._lights: list[LightSource] = []
        self._radial_cache: dict[tuple, pygame.Surface] = {}

    def add(self, light: LightSource) -> None:
        self._lights.append(light)

    def clear(self) -> None:
        self._lights.clear()

    def _get_radial(self, radius: int, color: tuple) -> pygame.Surface:
        key = (radius, color)
        if key not in self._radial_cache:
            self._radial_cache[key] = _make_radial(radius, color)
        return self._radial_cache[key]

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        if not self._lights:
            return
        overlay = pygame.Surface(self._size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.DARKNESS_ALPHA))

        for light in self._lights:
            x, y = light.x, light.y
            if camera:
                x, y = camera.apply_point((int(x), int(y)))
            r = int(light.radius * light.intensity)
            grad = self._get_radial(r, light.color)
            bx = int(x) - r
            by = int(y) - r
            overlay.blit(grad, (bx, by), special_flags=pygame.BLEND_RGBA_SUB)

        surface.blit(overlay, (0, 0))
