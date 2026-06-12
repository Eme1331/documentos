"""HP bar widget."""
from __future__ import annotations
import pygame


class HPBar:
    def __init__(self, x: int, y: int, w: int = 200, h: int = 16) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self._display_frac = 1.0
        self._drain_frac = 1.0
        self._drain_speed = 0.4

    def update(self, hp: int, max_hp: int, dt: float) -> None:
        target = min(1.0, hp / max(1, max_hp))
        self._drain_frac = min(1.0, max(target, self._drain_frac - self._drain_speed * dt))
        self._display_frac = target

    def draw(self, surface: pygame.Surface) -> None:
        bg = pygame.Rect(self.rect)
        pygame.draw.rect(surface, (40, 0, 0), bg, border_radius=4)

        # Drain (delayed, darker red)
        drain_w = int(self.rect.width * self._drain_frac)
        pygame.draw.rect(surface, (160, 40, 40),
                         (*self.rect.topleft, drain_w, self.rect.height),
                         border_radius=4)

        # Current HP
        frac = self._display_frac
        color = (0, 220, 80) if frac > 0.5 else (255, 180, 0) if frac > 0.25 else (255, 40, 40)
        hp_w = int(self.rect.width * frac)
        if hp_w > 0:
            pygame.draw.rect(surface, color,
                             (*self.rect.topleft, hp_w, self.rect.height),
                             border_radius=4)

        pygame.draw.rect(surface, (180, 180, 200), self.rect, 1, border_radius=4)
