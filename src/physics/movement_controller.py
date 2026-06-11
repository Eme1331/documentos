"""Grounded state, coyote time, jump buffer, wall slide."""
from __future__ import annotations
import settings


class MovementController:
    COYOTE_FRAMES = settings.COYOTE_FRAMES
    JUMP_BUFFER_FRAMES = settings.JUMP_BUFFER_FRAMES

    def __init__(self) -> None:
        self.grounded = False
        self.wall_left = False
        self.wall_right = False
        self.wall_climb_enabled = False

        self._coyote = 0
        self._jump_buffer = 0
        self._wall_slide_vel = 80.0

    def update_flags(self, flags) -> None:
        if flags.ground:
            self.grounded = True
            self._coyote = self.COYOTE_FRAMES
        else:
            if self.grounded:
                pass
            self.grounded = False
            if self._coyote > 0:
                self._coyote -= 1

        self.wall_left = flags.left
        self.wall_right = flags.right

    def request_jump(self) -> None:
        self._jump_buffer = self.JUMP_BUFFER_FRAMES

    def tick_buffer(self) -> None:
        if self._jump_buffer > 0:
            self._jump_buffer -= 1

    @property
    def can_jump(self) -> bool:
        return self.grounded or self._coyote > 0

    @property
    def buffered_jump(self) -> bool:
        return self._jump_buffer > 0

    def consume_jump(self) -> None:
        self._coyote = 0
        self._jump_buffer = 0

    @property
    def on_wall(self) -> bool:
        return (self.wall_left or self.wall_right) and self.wall_climb_enabled

    def wall_slide_velocity(self) -> float:
        return self._wall_slide_vel
