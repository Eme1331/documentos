"""Screen shake, flash, and slow-mo effects."""
from __future__ import annotations
import random
import pygame


class ScreenEffects:
    def __init__(self) -> None:
        self._shake_intensity = 0.0
        self._shake_duration = 0.0
        self._shake_offset = (0, 0)

        self._flash_color = (255, 255, 255)
        self._flash_alpha = 0.0
        self._flash_duration = 0.0
        self._flash_elapsed = 0.0

        self.time_scale = 1.0
        self._slowmo_duration = 0.0
        self._slowmo_scale = 1.0

    def shake(self, intensity: float = 8.0, duration: float = 0.3) -> None:
        self._shake_intensity = intensity
        self._shake_duration = duration

    def flash(self, color=(255, 255, 255), alpha: float = 200.0,
              duration: float = 0.15) -> None:
        self._flash_color = color
        self._flash_alpha = alpha
        self._flash_duration = duration
        self._flash_elapsed = 0.0

    def slow_mo(self, scale: float = 0.3, duration: float = 0.5) -> None:
        self.time_scale = scale
        self._slowmo_scale = scale
        self._slowmo_duration = duration

    def update(self, dt: float) -> float:
        # Screen shake
        if self._shake_duration > 0:
            self._shake_duration -= dt
            decay = max(0.0, self._shake_duration)
            mag = self._shake_intensity * (decay / max(decay, 0.001))
            self._shake_offset = (
                random.uniform(-mag, mag),
                random.uniform(-mag, mag))
        else:
            self._shake_offset = (0, 0)

        # Flash
        if self._flash_duration > 0:
            self._flash_elapsed += dt
            t = self._flash_elapsed / self._flash_duration
            self._flash_alpha = max(0.0, 200.0 * (1.0 - t))
            if t >= 1.0:
                self._flash_duration = 0.0
                self._flash_alpha = 0.0

        # Slow-mo
        if self._slowmo_duration > 0:
            self._slowmo_duration -= dt
            if self._slowmo_duration <= 0:
                self.time_scale = 1.0
        else:
            self.time_scale = 1.0

        return dt * self.time_scale  # effective dt

    @property
    def shake_offset(self) -> tuple:
        return self._shake_offset

    def draw_overlay(self, surface: pygame.Surface) -> None:
        if self._flash_alpha > 0:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((*self._flash_color, int(self._flash_alpha)))
            surface.blit(overlay, (0, 0))
