"""Character selection state."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
from src.ui.menu.character_select import CharacterSelect


class CharacterSelectState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._menu = CharacterSelect()

    def handle_event(self, event: pygame.event.Event) -> None:
        result = self._menu.handle_event(event)
        if result == "BACK":
            from src.states.main_menu_state import MainMenuState
            self.game.state_machine.change(MainMenuState(self.game))
        elif result and result != "BACK":
            self.game.session["character"] = result
            try:
                from src.states.gameplay_state import GameplayState
                self.game.state_machine.change(GameplayState(self.game))
            except Exception as exc:
                import traceback
                traceback.print_exc()
                print(f"[ERROR] Failed to load gameplay: {exc}")

    def draw(self, surface: pygame.Surface) -> None:
        self._menu.draw(surface)
