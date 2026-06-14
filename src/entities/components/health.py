"""Health component."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Health:
    hp: int = 100
    max_hp: int = 100
    invincibility_frames: int = 0
    iframes_on_hit: int = 30

    def take_damage(self, amount: int, source=None) -> int:
        if amount <= 0:
            return 0
        dealt = min(self.hp, amount)
        self.hp -= dealt
        return dealt

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + max(0, amount))

    def is_dead(self) -> bool:
        return self.hp <= 0

    def tick(self) -> None:
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1

    @property
    def fraction(self) -> float:
        return self.hp / self.max_hp if self.max_hp else 0.0
