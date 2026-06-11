"""Stack-based game state machine."""
from __future__ import annotations

from abc import ABC
import pygame


class GameState(ABC):
    """Abstract base for all game states."""

    def __init__(self, game=None) -> None:
        self.game = game
        self.done = False

    def on_enter(self, **kwargs) -> None:
        """Called when state becomes active."""

    def on_exit(self) -> None:
        """Called when state is removed/paused."""

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a single pygame event."""

    def update(self, dt: float) -> None:
        """Variable timestep update."""

    def fixed_update(self, dt: float) -> None:
        """Fixed timestep update (physics)."""

    def draw(self, surface: pygame.Surface) -> None:
        """Render the state."""


class StateMachine:
    """Stack of GameStates; only the top receives input/update by default."""

    def __init__(self) -> None:
        self._stack: list[GameState] = []

    @property
    def current(self) -> GameState | None:
        return self._stack[-1] if self._stack else None

    @property
    def is_empty(self) -> bool:
        return not self._stack

    def push(self, state: GameState, **kwargs) -> None:
        self._stack.append(state)
        state.on_enter(**kwargs)

    def pop(self) -> GameState | None:
        if not self._stack:
            return None
        state = self._stack.pop()
        state.on_exit()
        return state

    def change(self, state: GameState, **kwargs) -> None:
        while self._stack:
            self.pop()
        self.push(state, **kwargs)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(dt)
            if self.current.done:
                self.current.done = False
                self.pop()

    def fixed_update(self, dt: float) -> None:
        if self.current:
            self.current.fixed_update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        # Draw whole stack bottom-up so overlays (pause) render over gameplay.
        for state in self._stack:
            state.draw(surface)
