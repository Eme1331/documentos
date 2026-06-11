"""AABB collision resolution against tile rects."""
from __future__ import annotations
import pygame
from dataclasses import dataclass, field


@dataclass
class CollisionFlags:
    ground: bool = False
    ceiling: bool = False
    left: bool = False
    right: bool = False


def resolve(rect: pygame.Rect, velocity: pygame.math.Vector2,
            tiles: list[pygame.Rect], one_way: list[pygame.Rect],
            was_grounded: bool) -> CollisionFlags:
    flags = CollisionFlags()

    # Horizontal pass
    rect.x += int(velocity.x)
    for tile in tiles:
        if rect.colliderect(tile):
            if velocity.x > 0:
                rect.right = tile.left
                flags.right = True
            elif velocity.x < 0:
                rect.left = tile.right
                flags.left = True
            velocity.x = 0

    # Vertical pass
    rect.y += int(velocity.y)
    for tile in tiles:
        if rect.colliderect(tile):
            if velocity.y > 0:
                rect.bottom = tile.top
                flags.ground = True
            elif velocity.y < 0:
                rect.top = tile.bottom
                flags.ceiling = True
            velocity.y = 0

    # One-way platforms (only from above)
    for tile in one_way:
        if rect.colliderect(tile) and velocity.y >= 0:
            prev_bottom = rect.bottom - int(velocity.y)
            if prev_bottom <= tile.top + 2:
                rect.bottom = tile.top
                flags.ground = True
                velocity.y = 0

    return flags
