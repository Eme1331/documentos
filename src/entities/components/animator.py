"""Animator component: frame sequences keyed by state name."""
from __future__ import annotations

from dataclasses import dataclass, field
import pygame


@dataclass
class Animation:
    frames: list  # list[pygame.Surface]
    fps: float = 10.0
    loop: bool = True


@dataclass
class Animator:
    animations: dict = field(default_factory=dict)  # name -> Animation
    current: str = ""
    frame_index: int = 0
    _time: float = 0.0
    finished: bool = False

    def add(self, name: str, frames: list, fps: float = 10.0, loop: bool = True) -> None:
        self.animations[name] = Animation(frames, fps, loop)
        if not self.current:
            self.current = name

    def play(self, name: str, restart: bool = False) -> None:
        if name not in self.animations:
            return
        if name == self.current and not restart:
            return
        self.current = name
        self.frame_index = 0
        self._time = 0.0
        self.finished = False

    def update(self, dt: float) -> None:
        anim = self.animations.get(self.current)
        if not anim or not anim.frames:
            return
        self._time += dt
        frame_dur = 1.0 / max(0.001, anim.fps)
        while self._time >= frame_dur:
            self._time -= frame_dur
            self.frame_index += 1
            if self.frame_index >= len(anim.frames):
                if anim.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(anim.frames) - 1
                    self.finished = True
                    break

    def current_frame(self) -> pygame.Surface | None:
        anim = self.animations.get(self.current)
        if not anim or not anim.frames:
            return None
        idx = min(self.frame_index, len(anim.frames) - 1)
        return anim.frames[idx]
