"""Energy component."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Energy:
    energy: float = 100.0
    max_energy: float = 100.0
    regen_rate: float = 12.0  # per second

    def consume(self, amount: float) -> bool:
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def recharge(self, dt: float) -> None:
        self.energy = min(self.max_energy, self.energy + self.regen_rate * dt)

    def add(self, amount: float) -> None:
        self.energy = min(self.max_energy, self.energy + amount)

    @property
    def fraction(self) -> float:
        return self.energy / self.max_energy if self.max_energy else 0.0

    @property
    def is_full(self) -> bool:
        return self.energy >= self.max_energy - 0.01
