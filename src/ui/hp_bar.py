"""HP bar widget."""
from __future__ import annotations
import pygame


class HPBar:
    def __init__(self, x: int, y: int, w: int = 200, h: int = 16) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self._display_frac = 1.0
        self._drain_frac = 1.0
        self._drain_speed = 0.4
        try:
            self._font = pygame.font.SysFont("consolas", 11, bold=True)
        except Exception:
            self._font = None

    def update(self, hp: int, max_hp: int, dt: float) -> None:
        target = min(1.0, hp / max(1, max_hp))
        self._drain_frac = min(1.0, max(target, self._drain_frac - self._drain_speed * dt))
        self._display_frac = target

    def draw(self, surface: pygame.Surface) -> None:
        r = self.rect

        # Outer glow when low HP
        frac = self._display_frac
        if frac < 0.25:
            glow = pygame.Surface((r.w + 6, r.h + 6), pygame.SRCALPHA)
            glow.fill((255, 40, 40, 40))
            surface.blit(glow, (r.x - 3, r.y - 3))

        # Background
        pygame.draw.rect(surface, (30, 0, 0), r, border_radius=4)

        # Drain bar (delayed)
        drain_w = int(r.width * self._drain_frac)
        if drain_w > 0:
            pygame.draw.rect(surface, (130, 30, 30),
                             (r.x, r.y, drain_w, r.h), border_radius=4)

        # HP fill
        color = (0, 210, 70) if frac > 0.5 else (255, 170, 0) if frac > 0.25 else (255, 40, 40)
        hp_w = int(r.width * frac)
        if hp_w > 0:
            pygame.draw.rect(surface, color, (r.x, r.y, hp_w, r.h), border_radius=4)
            # Shine strip
            pygame.draw.line(surface, (255, 255, 255),
                             (r.x + 2, r.y + 2), (r.x + hp_w - 2, r.y + 2), 1)

        # Segment dividers every 25%
        for seg in (0.25, 0.50, 0.75):
            sx = r.x + int(r.width * seg)
            pygame.draw.line(surface, (0, 0, 0), (sx, r.y), (sx, r.y + r.h), 1)

        # Border
        pygame.draw.rect(surface, (160, 160, 200), r, 1, border_radius=4)

        # "HP" label
        if self._font:
            lbl = self._font.render("HP", True, (200, 200, 220))
            surface.blit(lbl, (r.x - lbl.get_width() - 4, r.y + r.h // 2 - lbl.get_height() // 2))
