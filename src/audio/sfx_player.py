"""Pooled SFX player with positional attenuation."""
from __future__ import annotations
import pygame
import math


class SFXPlayer:
    MAX_DIST = 600.0

    def __init__(self, audio_manager=None, num_channels: int = 32) -> None:
        self._am = audio_manager
        self._cache: dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.set_num_channels(num_channels)
        except Exception:
            pass

    def play(self, file_path: str, pos: tuple | None = None,
             camera_center: tuple | None = None) -> None:
        try:
            if file_path not in self._cache:
                self._cache[file_path] = pygame.mixer.Sound(file_path)
            sound = self._cache[file_path]
            vol = (self._am.sfx_vol * self._am.master) if self._am else 0.8
            if pos and camera_center:
                dx = pos[0] - camera_center[0]
                dy = pos[1] - camera_center[1]
                dist = math.hypot(dx, dy)
                vol *= max(0.0, 1.0 - dist / self.MAX_DIST)
            sound.set_volume(vol)
            sound.play()
        except Exception:
            pass
