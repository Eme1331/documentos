"""Keyboard abstraction mapping actions to keys."""
from __future__ import annotations

import pygame

# Action constants
MOVE_LEFT = "MOVE_LEFT"
MOVE_RIGHT = "MOVE_RIGHT"
JUMP = "JUMP"
DASH = "DASH"
ATTACK_LIGHT = "ATTACK_LIGHT"
ATTACK_HEAVY = "ATTACK_HEAVY"
SPECIAL_1 = "SPECIAL_1"
SPECIAL_2 = "SPECIAL_2"
SPECIAL_3 = "SPECIAL_3"
DODGE = "DODGE"
PAUSE = "PAUSE"

DEFAULT_BINDINGS = {
    MOVE_LEFT: pygame.K_a,
    MOVE_RIGHT: pygame.K_d,
    JUMP: pygame.K_SPACE,
    DASH: pygame.K_LSHIFT,
    ATTACK_LIGHT: pygame.K_j,
    ATTACK_HEAVY: pygame.K_k,
    SPECIAL_1: pygame.K_u,
    SPECIAL_2: pygame.K_i,
    SPECIAL_3: pygame.K_o,
    DODGE: pygame.K_l,
    PAUSE: pygame.K_ESCAPE,
}


class InputHandler:
    """Tracks held / just-pressed / just-released actions."""

    def __init__(self, bindings: dict[str, int] | None = None) -> None:
        self.bindings: dict[str, int] = dict(DEFAULT_BINDINGS)
        if bindings:
            for action, key in bindings.items():
                if action in self.bindings and isinstance(key, int):
                    self.bindings[action] = key
        self._held: set[str] = set()
        self._pressed: set[str] = set()
        self._released: set[str] = set()

    def begin_frame(self) -> None:
        self._pressed.clear()
        self._released.clear()

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            for action, key in self.bindings.items():
                if event.key == key:
                    if action not in self._held:
                        self._pressed.add(action)
                    self._held.add(action)
        elif event.type == pygame.KEYUP:
            for action, key in self.bindings.items():
                if event.key == key:
                    self._held.discard(action)
                    self._released.add(action)

    def is_held(self, action: str) -> bool:
        return action in self._held

    def just_pressed(self, action: str) -> bool:
        return action in self._pressed

    def just_released(self, action: str) -> bool:
        return action in self._released

    def axis_x(self) -> float:
        x = 0.0
        if self.is_held(MOVE_LEFT):
            x -= 1.0
        if self.is_held(MOVE_RIGHT):
            x += 1.0
        return x

    def rebind(self, action: str, key: int) -> None:
        if action in self.bindings:
            self.bindings[action] = key
