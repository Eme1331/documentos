"""Energy bar widget."""
from __future__ import annotations
import pygame
import math


class EnergyBar:
    def __init__(self, x: int, y: int, w: int = 200, h: int = 10) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self._frac = 1.0
        self._pulse_t = 0.0

    def update(self, energy: float, max_energy: float, dt: float) -> None:
        self._frac = energy / max(1, max_energy)
        if self._frac >= 1.0:
            self._pulse_t += dt * 3
        else:
            self._pulse_t = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (0, 30, 50), self.rect, border_radius=3)
        w = int(self.rect.width * self._frac)
        if w > 0:
            pulse = int(20 * math.sin(self._pulse_t)) if self._frac >= 1.0 else 0
            color = (0, min(255, 200 + pulse), min(255, 230 + pulse))
            pygame.draw.rect(surface, color,
                             (*self.rect.topleft, w, self.rect.height),
                             border_radius=3)
        pygame.draw.rect(surface, (0, 120, 160), self.rect, 1, border_radius=3)
