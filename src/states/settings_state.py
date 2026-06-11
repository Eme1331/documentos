"""Settings state (wraps SettingsMenu)."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
from src.ui.menu.settings_menu import SettingsMenu


class SettingsState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._menu = SettingsMenu(game.config)

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self._menu.handle_event(event)
        if action == "BACK":
            self.game.state_machine.pop()

    def draw(self, surface: pygame.Surface) -> None:
        self._menu.draw(surface)
