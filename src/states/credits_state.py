"""Scrolling credits."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
import settings

CREDITS = [
    "GALAXY REBORN: THE LAST FRONTIER",
    "",
    "DESIGN & PROGRAMMING",
    "Galaxy Reborn Team",
    "",
    "ART DIRECTION",
    "Pixel Art HD Division",
    "",
    "MUSIC",
    "Synthwave Collective",
    "",
    "SOUND DESIGN",
    "Cyber Audio Labs",
    "",
    "SPECIAL THANKS",
    "The Players",
    "",
    "Thank you for playing!",
]


class CreditsState(GameState):
    SCROLL_SPEED = 40.0

    def __init__(self, game) -> None:
        self.game = game
        self._y = float(settings.SCREEN_HEIGHT)
        try:
            self._font_title = pygame.font.SysFont("consolas", 28, bold=True)
            self._font = pygame.font.SysFont("consolas", 18)
        except Exception:
            self._font_title = self._font = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.states.main_menu_state import MainMenuState
            self.game.state_machine.change(MainMenuState(self.game))

    def update(self, dt: float) -> None:
        self._y -= self.SCROLL_SPEED * dt
        total_h = len(CREDITS) * 32
        if self._y < -total_h:
            from src.states.main_menu_state import MainMenuState
            self.game.state_machine.change(MainMenuState(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.COLOR_BG)
        sw = settings.SCREEN_WIDTH
        y = int(self._y)
        for line in CREDITS:
            if not line:
                y += 20
                continue
            font = self._font_title if line.isupper() else self._font
            if font:
                col = settings.NEON_CYAN if line.isupper() else settings.COLOR_WHITE
                lbl = font.render(line, True, col)
                surface.blit(lbl, (sw // 2 - lbl.get_width() // 2, y))
            y += 32
