"""CY-X7 — Cyborg Warrior."""
from __future__ import annotations
from src.characters.base_character import BaseCharacter, CharacterStats
from src.combat.combo_system import ComboDefinition


class CYX7(BaseCharacter):
    JUMP_COUNT_MAX = 2

    def __init__(self, stats_data: dict) -> None:
        merged = {"name": "CY-X7", "color": [150, 80, 220],
                  "width": 36, "height": 52, **stats_data}
        super().__init__(merged)
        self._armor_intact = True
        self._armor_regen_timer = 0.0
        self._overclock_active = False
        self._overclock_timer = 0.0
        self._arm_mode = "cannon"  # "blade" | "cannon"

    def get_stats(self) -> CharacterStats:
        return self.stats

    def _setup_combos(self) -> None:
        self.combo.add_combo(ComboDefinition(
            "OverclockSlam", ["HEAVY", "HEAVY", "SPECIAL"],
            max_gap_ms=500, multiplier=2.0))

    def update(self, dt: float) -> None:
        super().update(dt)
        # Armor regen
        if not self._armor_intact:
            self._armor_regen_timer -= dt
            if self._armor_regen_timer <= 0:
                self._armor_intact = True

        # Overclock drain
        if self._overclock_active:
            en = self.get(__import__("src.entities.components.energy",
                                      fromlist=["Energy"]).Energy)
            if en:
                en.consume(5 * dt)
            self._overclock_timer -= dt
            if self._overclock_timer <= 0:
                self._overclock_active = False
                self.stats.speed /= 1.3

    def take_damage(self, amount: int, source=None) -> None:
        if self._armor_intact:
            self._armor_intact = False
            self._armor_regen_timer = 3.0
            return
        super().take_damage(amount, source)

    def special_1(self) -> None:
        """Wall Climb toggle."""
        from src.physics.movement_controller import MovementController
        mc = self.get(MovementController)
        if mc:
            mc.wall_climb_enabled = not mc.wall_climb_enabled
        self._special_cds[0] = 0.5

    def special_2(self) -> None:
        """Overclock Mode — 8s buff."""
        if self._overclock_active:
            return
        en = self.get(__import__("src.entities.components.energy",
                                   fromlist=["Energy"]).Energy)
        if not en or not en.consume(30):
            return
        self._overclock_active = True
        self._overclock_timer = 8.0
        self.stats.speed *= 1.3
        self._special_cds[1] = 10.0
        self.state = self.SPECIAL_2
        self._state_timer = 0.2

    def special_3(self) -> None:
        """Arm Transform — toggle blade/cannon."""
        self._arm_mode = "cannon" if self._arm_mode == "blade" else "blade"
        self._special_cds[2] = 0.3
        self.state = self.SPECIAL_3
        self._state_timer = 0.15
