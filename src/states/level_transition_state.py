"""Level transition: black fade out → load → fade in."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
import settings


class LevelTransitionState(GameState):
    FADE = 0.5

    def __init__(self, game, next_level_id: str) -> None:
        self.game = game
        self._next = next_level_id
        self._t = 0.0
        self._phase = "out"
        self._loaded = False

    def update(self, dt: float) -> None:
        self._t += dt
        if self._phase == "out" and self._t >= self.FADE:
            game = self.game
            game.session["level_id"] = self._next
            from src.states.gameplay_state import GameplayState
            game.state_machine.change(GameplayState(game))

    def draw(self, surface: pygame.Surface) -> None:
        t = min(1.0, self._t / self.FADE)
        alpha = int(255 * t)
        overlay = pygame.Surface(settings.SCREEN_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))
