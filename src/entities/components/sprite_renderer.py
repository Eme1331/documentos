"""Sprite renderer component."""
from __future__ import annotations

from dataclasses import dataclass, field
from pygame.math import Vector2
import pygame


@dataclass
class SpriteRenderer:
    surface: pygame.Surface | None = None
    offset: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    flip_with_facing: bool = True
    visible: bool = True

    def get_surface(self, facing: int = 1) -> pygame.Surface | None:
        if self.surface is None:
            return None
        if self.flip_with_facing and facing < 0:
            return pygame.transform.flip(self.surface, True, False)
        return self.surface
