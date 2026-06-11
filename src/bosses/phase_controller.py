"""Boss phase data."""
from __future__ import annotations
from dataclasses import dataclass, field
import random


@dataclass
class AttackPattern:
    name: str
    weight: float = 1.0
    cooldown: float = 2.0
    _timer: float = 0.0

    def ready(self) -> bool:
        return self._timer <= 0

    def reset(self) -> None:
        self._timer = self.cooldown

    def tick(self, dt: float) -> None:
        self._timer = max(0.0, self._timer - dt)


@dataclass
class BossPhase:
    phase_num: int
    hp_threshold: float        # 0.0–1.0 (triggers when HP drops below)
    attack_patterns: list[AttackPattern] = field(default_factory=list)
    movement_behavior: str = "aggressive"
    enrage_threshold: float = 0.2
    speed_multiplier: float = 1.0
    damage_multiplier: float = 1.0

    def pick_pattern(self) -> AttackPattern | None:
        ready = [p for p in self.attack_patterns if p.ready()]
        if not ready:
            return None
        total = sum(p.weight for p in ready)
        r = random.uniform(0, total)
        cumulative = 0.0
        for p in ready:
            cumulative += p.weight
            if r <= cumulative:
                return p
        return ready[0]
