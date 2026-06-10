"""Transform component."""
from __future__ import annotations

from dataclasses import dataclass, field
from pygame.math import Vector2


@dataclass
class Transform:
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    facing: int = 1  # 1 right, -1 left

    def __post_init__(self) -> None:
        self.position = Vector2(self.position)
        self.velocity = Vector2(self.velocity)

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y
