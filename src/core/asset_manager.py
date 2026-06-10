"""Centralized asset loader with caching and lazy generation."""
from __future__ import annotations

import os
import pygame


class AssetManager:
    """Loads and caches surfaces, fonts and sounds. Generates placeholders."""

    def __init__(self, assets_dir: str | None = None) -> None:
        self.assets_dir = assets_dir
        self._images: dict[str, pygame.Surface] = {}
        self._fonts: dict[tuple[str | None, int], pygame.font.Font] = {}
        self._sounds: dict[str, object] = {}

    # --- Images ---
    def get_image(self, path: str) -> pygame.Surface:
        if path in self._images:
            return self._images[path]
        full = path
        if self.assets_dir and not os.path.isabs(path):
            full = os.path.join(self.assets_dir, path)
        surf: pygame.Surface
        try:
            surf = pygame.image.load(full).convert_alpha()
        except Exception:
            surf = self.placeholder(32, 32, (255, 0, 200))
        self._images[path] = surf
        return surf

    def placeholder(self, w: int, h: int, color, key: str | None = None,
                    border: bool = True) -> pygame.Surface:
        """Generate a colored rectangle surface as a placeholder asset."""
        if key and key in self._images:
            return self._images[key]
        surf = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
        surf.fill(color)
        if border and w > 4 and h > 4:
            pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
        if key:
            self._images[key] = surf
        return surf

    # --- Fonts ---
    def get_font(self, size: int, name: str | None = None) -> pygame.font.Font:
        key = (name, size)
        if key not in self._fonts:
            try:
                if name and os.path.exists(name):
                    self._fonts[key] = pygame.font.Font(name, size)
                else:
                    self._fonts[key] = pygame.font.SysFont(name or "consolas", size)
            except Exception:
                self._fonts[key] = pygame.font.Font(None, size)
        return self._fonts[key]

    # --- Sounds ---
    def get_sound(self, path: str):
        if path in self._sounds:
            return self._sounds[path]
        full = path
        if self.assets_dir and not os.path.isabs(path):
            full = os.path.join(self.assets_dir, path)
        snd = None
        try:
            snd = pygame.mixer.Sound(full)
        except Exception:
            snd = None
        self._sounds[path] = snd
        return snd

    def clear(self) -> None:
        self._images.clear()
        self._fonts.clear()
        self._sounds.clear()
