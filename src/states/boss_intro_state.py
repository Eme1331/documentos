"""Boss name card intro."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
import settings


class BossIntroState(GameState):
    DURATION = 2.5

    def __init__(self, game, boss_name: str) -> None:
        self.game = game
        self._name = boss_name
        self._t = 0.0
        try:
            self._font = pygame.font.SysFont("consolas", 42, bold=True)
            self._sub = pygame.font.SysFont("consolas", 18)
        except Exception:
            self._font = self._sub = None

    def update(self, dt: float) -> None:
        self._t += dt
        if self._t >= self.DURATION:
            self.game.state_machine.pop()

    def draw(self, surface: pygame.Surface) -> None:
        sw, sh = settings.SCREEN_SIZE
        t = self._t / self.DURATION
        alpha = int(255 * min(1.0, min(t * 4, (1 - t) * 4)))

        if self._font:
            lbl = self._font.render(self._name, True, (255, 80, 0))
            lbl.set_alpha(alpha)
            x = int(sw * (1.0 - min(1.0, self._t * 3))) if self._t < 0.3 else 0
            surface.blit(lbl, (sw // 2 - lbl.get_width() // 2 + x,
                                sh // 2 - lbl.get_height() // 2))
        if self._sub:
            s = self._sub.render("BOSS BATTLE", True, settings.NEON_RED)
            s.set_alpha(alpha)
            surface.blit(s, (sw // 2 - s.get_width() // 2, sh // 2 + 40))
