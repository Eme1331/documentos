"""Collider component."""
from __future__ import annotations

from dataclasses import dataclass, field
import pygame


@dataclass
class Collider:
    width: int = 32
    height: int = 32
    offset_x: int = 0
    offset_y: int = 0
    layer_mask: int = 0xFFFF
    is_trigger: bool = False

    def rect_at(self, x: float, y: float) -> pygame.Rect:
        return pygame.Rect(int(x + self.offset_x), int(y + self.offset_y),
                           self.width, self.height)
