"""Pause state — overlay on gameplay."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
from src.ui.menu.pause_menu import PauseMenu


class PauseState(GameState):
    def __init__(self, game, gameplay_state=None) -> None:
        self.game = game
        self._gameplay = gameplay_state
        self._menu = PauseMenu()

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self._menu.handle_event(event)
        if action == "RESUME":
            self.game.state_machine.pop()
        elif action == "SKILL TREE":
            pass
        elif action == "MAIN MENU":
            from src.states.main_menu_state import MainMenuState
            self.game.state_machine.change(MainMenuState(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        if self._gameplay:
            self._gameplay.draw(surface)
        self._menu.draw(surface)
