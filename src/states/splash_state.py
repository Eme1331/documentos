"""Splash screen: studio logo fade in/out."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
import settings


class SplashState(GameState):
    FADE_IN = 1.5
    HOLD = 1.0
    FADE_OUT = 1.0

    def __init__(self, game) -> None:
        self.game = game
        self._t = 0.0
        self._phase = "fade_in"
        self._alpha = 0
        try:
            self._font = pygame.font.SysFont("consolas", 52, bold=True)
            self._sub = pygame.font.SysFont("consolas", 20)
        except Exception:
            self._font = self._sub = None

    def update(self, dt: float) -> None:
        self._t += dt
        if self._phase == "fade_in":
            self._alpha = int(255 * min(1.0, self._t / self.FADE_IN))
            if self._t >= self.FADE_IN:
                self._phase = "hold"
                self._t = 0.0
        elif self._phase == "hold":
            self._alpha = 255
            if self._t >= self.HOLD:
                self._phase = "fade_out"
                self._t = 0.0
        elif self._phase == "fade_out":
            self._alpha = int(255 * (1.0 - min(1.0, self._t / self.FADE_OUT)))
            if self._t >= self.FADE_OUT:
                self._go_main()

    def _go_main(self) -> None:
        from src.states.main_menu_state import MainMenuState
        self.game.state_machine.change(MainMenuState(self.game))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._go_main()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.COLOR_BG)
        if self._font:
            t = self._font.render("GALAXY REBORN", True, settings.NEON_CYAN)
            t.set_alpha(self._alpha)
            sw, sh = settings.SCREEN_SIZE
            surface.blit(t, (sw // 2 - t.get_width() // 2, sh // 2 - 40))
        if self._sub:
            s = self._sub.render("THE LAST FRONTIER", True, settings.NEON_PURPLE)
            s.set_alpha(self._alpha)
            sw, sh = settings.SCREEN_SIZE
            surface.blit(s, (sw // 2 - s.get_width() // 2, sh // 2 + 30))
