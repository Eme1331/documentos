"""Quick inventory (4 slots, bottom-center)."""
from __future__ import annotations
import pygame

SLOT_SIZE = 40
MARGIN = 4


class QuickInventory:
    def __init__(self, screen_w: int, screen_h: int, slots: int = 4) -> None:
        self._sw = screen_w
        self._sh = screen_h
        self._slots = slots
        self._items: list[dict | None] = [None] * slots
        self._active = 0

    def set_item(self, slot: int, item: dict | None) -> None:
        if 0 <= slot < self._slots:
            self._items[slot] = item

    def set_active(self, slot: int) -> None:
        self._active = slot % self._slots

    def draw(self, surface: pygame.Surface) -> None:
        total_w = self._slots * SLOT_SIZE + (self._slots - 1) * MARGIN
        sx = self._sw // 2 - total_w // 2
        sy = self._sh - SLOT_SIZE - 10

        for i in range(self._slots):
            x = sx + i * (SLOT_SIZE + MARGIN)
            border = (0, 220, 200) if i == self._active else (80, 80, 120)
            pygame.draw.rect(surface, (20, 20, 40), (x, sy, SLOT_SIZE, SLOT_SIZE), border_radius=4)
            pygame.draw.rect(surface, border, (x, sy, SLOT_SIZE, SLOT_SIZE), 2, border_radius=4)

            item = self._items[i]
            if item:
                try:
                    font = pygame.font.SysFont("consolas", 10)
                    lbl = font.render(item.get("name", "?")[:4], True, (200, 200, 220))
                    surface.blit(lbl, (x + 2, sy + SLOT_SIZE // 2 - lbl.get_height() // 2))
                except Exception:
                    pass
