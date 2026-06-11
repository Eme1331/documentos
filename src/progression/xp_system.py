"""XP gain and level-up logic."""
from __future__ import annotations

XP_THRESHOLDS = [0, 100, 250, 500, 900, 1500, 2400, 3700, 5500, 8000, 12000]


class XPSystem:
    def __init__(self, event_bus=None) -> None:
        self._eb = event_bus
        self.xp = 0
        self.level = 1
        self.skill_points = 0
        if event_bus:
            from src.core.event_bus import EnemyDiedEvent
            event_bus.subscribe(EnemyDiedEvent, self._on_enemy_died)

    def _on_enemy_died(self, event) -> None:
        self.add_xp(event.xp_reward)

    def add_xp(self, amount: int) -> None:
        self.xp += amount
        if self._eb:
            from src.core.event_bus import XPGainedEvent
            self._eb.emit(XPGainedEvent(amount=amount, total_xp=self.xp))
        self._check_level_up()

    def _check_level_up(self) -> None:
        while (self.level < len(XP_THRESHOLDS) - 1 and
               self.xp >= XP_THRESHOLDS[self.level]):
            self.level += 1
            self.skill_points += 2

    @property
    def xp_to_next(self) -> int:
        if self.level >= len(XP_THRESHOLDS) - 1:
            return 0
        return XP_THRESHOLDS[self.level] - self.xp

    @property
    def level_progress(self) -> float:
        if self.level >= len(XP_THRESHOLDS) - 1:
            return 1.0
        prev = XP_THRESHOLDS[self.level - 1]
        next_ = XP_THRESHOLDS[self.level]
        return (self.xp - prev) / max(1, next_ - prev)
