"""Main menu state."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
from src.ui.menu.main_menu import MainMenu


class MainMenuState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._menu = MainMenu()

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self._menu.handle_event(event)
        if action == "NEW GAME":
            from src.states.character_select_state import CharacterSelectState
            self.game.state_machine.change(CharacterSelectState(self.game))
        elif action == "LOAD GAME":
            self._try_load()
        elif action == "SETTINGS":
            from src.states.settings_state import SettingsState
            self.game.state_machine.push(SettingsState(self.game))
        elif action == "QUIT":
            self.game.quit()

    def _try_load(self) -> None:
        from src.progression.save_manager import SaveManager
        sm = SaveManager()
        data = sm.load(1)
        if data:
            self.game.session["character"] = data.get("character", "ethan")
            self.game.session["save_data"] = data
            from src.states.gameplay_state import GameplayState
            self.game.state_machine.change(GameplayState(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        self._menu.draw(surface)
