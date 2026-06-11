"""Zhyra — Alien Quantum Manipulator."""
from __future__ import annotations
import pygame
from src.characters.base_character import BaseCharacter, CharacterStats
from src.combat.combo_system import ComboDefinition


class Zhyra(BaseCharacter):
    JUMP_COUNT_MAX = 3

    def __init__(self, stats_data: dict) -> None:
        merged = {"name": "Zhyra", "color": [220, 80, 255],
                  "width": 30, "height": 44, **stats_data}
        super().__init__(merged)
        self._gravity_field_timer = 0.0

    def get_stats(self) -> CharacterStats:
        return self.stats

    def _setup_combos(self) -> None:
        self.combo.add_combo(ComboDefinition(
            "TripleSlash", ["LIGHT", "LIGHT", "LIGHT"],
            max_gap_ms=400, multiplier=1.4))

    def take_damage(self, amount: int, source=None) -> None:
        # Passive: dodge window gives 0.2s intangibility
        if self._invincible > 0:
            return
        super().take_damage(amount, source)

    def special_1(self) -> None:
        """Triple jump — jump counter managed in JUMP_COUNT_MAX=3."""
        tr = self.get(__import__("src.entities.components.transform",
                                   fromlist=["Transform"]).Transform)
        if tr and self._jump_count < self.JUMP_COUNT_MAX:
            tr.velocity.y = -self.stats.jump_force * 0.85
            self._jump_count += 1
            self.state = self.JUMPING
        self._special_cds[0] = 0.1

    def special_2(self) -> None:
        """Teleport blink — 400px in facing direction."""
        en = self.get(__import__("src.entities.components.energy",
                                   fromlist=["Energy"]).Energy)
        if not en or not en.consume(25):
            return
        tr = self.get(__import__("src.entities.components.transform",
                                   fromlist=["Transform"]).Transform)
        col = self.get(__import__("src.entities.components.collider",
                                    fromlist=["Collider"]).Collider)
        if not tr:
            return
        tr.position.x += 400.0 * tr.facing
        if col:
            col.rect.x = int(tr.position.x)
        self._invincible = 0.1
        self._special_cds[1] = 1.5
        self.state = self.SPECIAL_2
        self._state_timer = 0.15

    def special_3(self) -> None:
        """Gravity Control — 4s field reversing enemy gravity."""
        en = self.get(__import__("src.entities.components.energy",
                                   fromlist=["Energy"]).Energy)
        if not en or not en.consume(40):
            return
        self._gravity_field_timer = 4.0
        self._special_cds[2] = 8.0
        self.state = self.SPECIAL_3
        self._state_timer = 0.3

    def update(self, dt: float) -> None:
        super().update(dt)
        if self._gravity_field_timer > 0:
            self._gravity_field_timer -= dt
