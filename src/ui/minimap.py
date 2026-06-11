"""Minimap widget."""
from __future__ import annotations
import pygame


class Minimap:
    W, H = 120, 80

    def __init__(self, screen_w: int, margin: int = 10) -> None:
        self.x = screen_w - self.W - margin
        self.y = margin
        self._surf = pygame.Surface((self.W, self.H), pygame.SRCALPHA)

    def update(self, player_pos: tuple, map_size: tuple) -> None:
        self._surf.fill((0, 0, 20, 180))
        pygame.draw.rect(self._surf, (60, 60, 100), (0, 0, self.W, self.H), 1)

        mw, mh = map_size
        if mw > 0 and mh > 0:
            px = int(player_pos[0] / mw * self.W)
            py = int(player_pos[1] / mh * self.H)
            pygame.draw.circle(self._surf, (0, 255, 200), (px, py), 3)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._surf, (self.x, self.y))
