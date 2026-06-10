"""Delta-time aware countdown timer with callbacks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Timer:
    """Countdown timer driven by delta time."""

    duration: float
    callback: Optional[Callable[[], None]] = None
    repeat: bool = False
    autostart: bool = True
    elapsed: float = 0.0
    running: bool = field(default=False)
    _started: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        if self.autostart:
            self.start()

    def start(self) -> None:
        self.elapsed = 0.0
        self.running = True
        self._started = True

    def stop(self) -> None:
        self.running = False

    def reset(self) -> None:
        self.elapsed = 0.0
        self.running = True

    @property
    def finished(self) -> bool:
        return self._started and self.elapsed >= self.duration and not self.repeat

    @property
    def progress(self) -> float:
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)

    @property
    def remaining(self) -> float:
        return max(0.0, self.duration - self.elapsed)

    def update(self, dt: float) -> None:
        if not self.running:
            return
        self.elapsed += dt
        if self.elapsed >= self.duration:
            if self.callback:
                self.callback()
            if self.repeat:
                self.elapsed -= self.duration
            else:
                self.running = False
