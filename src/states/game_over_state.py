"""Game over screen."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
import settings

OPTIONS = ["RETRY", "QUIT TO MENU"]


class GameOverState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._sel = 0
        try:
            self._font_title = pygame.font.SysFont("consolas", 48, bold=True)
            self._font = pygame.font.SysFont("consolas", 24)
        except Exception:
            self._font_title = self._font = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._sel = (self._sel - 1) % len(OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._sel = (self._sel + 1) % len(OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if OPTIONS[self._sel] == "RETRY":
                    from src.states.gameplay_state import GameplayState
                    self.game.state_machine.change(GameplayState(self.game))
                else:
                    from src.states.main_menu_state import MainMenuState
                    self.game.state_machine.change(MainMenuState(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.COLOR_BG)
        sw, sh = settings.SCREEN_SIZE
        if self._font_title:
            t = self._font_title.render("GAME OVER", True, settings.NEON_RED)
            surface.blit(t, (sw // 2 - t.get_width() // 2, sh // 3))
        if self._font:
            for i, opt in enumerate(OPTIONS):
                col = settings.NEON_CYAN if i == self._sel else settings.COLOR_GRAY
                lbl = self._font.render(opt, True, col)
                surface.blit(lbl, (sw // 2 - lbl.get_width() // 2, sh // 2 + i * 50))
