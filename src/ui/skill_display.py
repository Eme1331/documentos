"""Skill cooldown icons (bottom-right)."""
from __future__ import annotations
import pygame
import math

SKILL_COLORS = [(0, 200, 255), (160, 60, 255), (255, 80, 200)]
SKILL_LABELS = ["Q", "W", "E"]


class SkillDisplay:
    SLOT_SIZE = 44
    MARGIN = 6

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.screen_w = screen_w
        self.screen_h = screen_h

    def draw(self, surface: pygame.Surface, cooldowns: list[float],
             max_cooldowns: list[float]) -> None:
        n = len(cooldowns)
        total_w = n * self.SLOT_SIZE + (n - 1) * self.MARGIN
        sx = self.screen_w - total_w - 12
        sy = self.screen_h - self.SLOT_SIZE - 12

        for i, (cd, max_cd) in enumerate(zip(cooldowns, max_cooldowns)):
            x = sx + i * (self.SLOT_SIZE + self.MARGIN)
            col = SKILL_COLORS[i % len(SKILL_COLORS)]

            pygame.draw.rect(surface, (20, 20, 40),
                             (x, sy, self.SLOT_SIZE, self.SLOT_SIZE), border_radius=6)

            if max_cd > 0 and cd > 0:
                frac = cd / max_cd
                # Radial overlay
                overlay = pygame.Surface((self.SLOT_SIZE, self.SLOT_SIZE), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                angle = int(360 * (1 - frac))
                start_angle = -math.pi / 2
                pygame.draw.arc(overlay, (255, 255, 255, 200),
                                (4, 4, self.SLOT_SIZE - 8, self.SLOT_SIZE - 8),
                                start_angle, start_angle + math.radians(360 * frac), 4)
                surface.blit(overlay, (x, sy))
            else:
                border_col = col
                pygame.draw.rect(surface, border_col,
                                 (x, sy, self.SLOT_SIZE, self.SLOT_SIZE), 2, border_radius=6)

            try:
                font = pygame.font.SysFont("consolas", 14, bold=True)
                lbl = font.render(SKILL_LABELS[i], True, col)
                surface.blit(lbl, (x + self.SLOT_SIZE // 2 - lbl.get_width() // 2,
                                   sy + self.SLOT_SIZE // 2 - lbl.get_height() // 2))
            except Exception:
                pass
