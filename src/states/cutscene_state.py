"""Cutscene state — sequence of dialogue entries."""
from __future__ import annotations
import pygame
from dataclasses import dataclass
from src.core.state_machine import GameState
from src.ui.dialogue_box import DialogueBox
import settings


@dataclass
class DialogueEntry:
    speaker: str
    text: str
    portrait_color: tuple = (0, 200, 200)


class CutsceneState(GameState):
    def __init__(self, game, entries: list[DialogueEntry],
                 on_complete=None) -> None:
        super().__init__(game)
        self._entries = entries
        self._idx = 0
        self._on_complete = on_complete
        self._box = DialogueBox(*settings.SCREEN_SIZE)
        self._advance()

    def _advance(self) -> None:
        if self._idx < len(self._entries):
            e = self._entries[self._idx]
            self._box.show(e.text, e.speaker)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
            done = self._box.advance()
            if done:
                self._idx += 1
                if self._idx >= len(self._entries):
                    if self._on_complete:
                        self._on_complete()
                    self.game.state_machine.pop()
                else:
                    self._advance()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.state_machine.pop()

    def update(self, dt: float) -> None:
        self._box.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.COLOR_BG)
        self._box.draw(surface)
