"""Mission objective fade-in/out display."""
from __future__ import annotations
import pygame


class ObjectiveTracker:
    FADE_DURATION = 0.5
    HOLD_DURATION = 3.0

    def __init__(self, screen_w: int) -> None:
        self._sw = screen_w
        self._text = ""
        self._alpha = 0.0
        self._state = "hidden"  # hidden | fade_in | hold | fade_out
        self._timer = 0.0

    def set_objective(self, text: str) -> None:
        self._text = text
        self._state = "fade_in"
        self._timer = self.FADE_DURATION

    def update(self, dt: float) -> None:
        self._timer -= dt
        if self._state == "fade_in":
            self._alpha = 255 * (1.0 - self._timer / self.FADE_DURATION)
            if self._timer <= 0:
                self._state = "hold"
                self._timer = self.HOLD_DURATION
                self._alpha = 255
        elif self._state == "hold":
            if self._timer <= 0:
                self._state = "fade_out"
                self._timer = self.FADE_DURATION
        elif self._state == "fade_out":
            self._alpha = 255 * (self._timer / self.FADE_DURATION)
            if self._timer <= 0:
                self._state = "hidden"
                self._alpha = 0

    def draw(self, surface: pygame.Surface) -> None:
        if self._state == "hidden" or not self._text:
            return
        try:
            font = pygame.font.SysFont("consolas", 16, bold=True)
            lbl = font.render(f"► {self._text}", True, (0, 220, 200))
            lbl.set_alpha(int(self._alpha))
            x = self._sw // 2 - lbl.get_width() // 2
            surface.blit(lbl, (x, 12))
        except Exception:
            pass
