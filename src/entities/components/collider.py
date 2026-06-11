"""Collider component."""
from __future__ import annotations
import pygame


class Collider:
    def __init__(self, rect: pygame.Rect | None = None,
                 layer_mask: int = 0xFFFF,
                 is_trigger: bool = False) -> None:
        self.rect = rect if rect is not None else pygame.Rect(0, 0, 32, 32)
        self.layer_mask = layer_mask
        self.is_trigger = is_trigger
