"""Ethan Nova — Human Soldier."""
from __future__ import annotations
import pygame
from src.characters.base_character import BaseCharacter, CharacterStats
from src.combat.combo_system import ComboDefinition


class Ethan(BaseCharacter):
    JUMP_COUNT_MAX = 2

    def __init__(self, stats_data: dict) -> None:
        merged = {"name": "Ethan Nova", "color": [0, 180, 255],
                  "width": 32, "height": 48, **stats_data}
        super().__init__(merged)

    def get_stats(self) -> CharacterStats:
        return self.stats

    def _setup_combos(self) -> None:
        self.combo.add_combo(ComboDefinition(
            "PlasmaBurst", ["LIGHT", "LIGHT", "HEAVY"],
            max_gap_ms=400, multiplier=1.5))

    def _damage_bonus(self) -> float:
        hp = self.get(__import__("src.entities.components.health",
                                  fromlist=["Health"]).Health)
        if hp and hp.hp / hp.max_hp < 0.4:
            return 1.1
        return 1.0

    def special_1(self) -> None:
        """Plasma Rifle — hitscan beam."""
        en = self.get(__import__("src.entities.components.energy",
                                   fromlist=["Energy"]).Energy)
        if not en or not en.consume(15):
            return
        self.state = self.SPECIAL_1
        self._state_timer = 0.25
        self._special_cds[0] = 0.3
        tr = self.get(__import__("src.entities.components.transform",
                                   fromlist=["Transform"]).Transform)
        if tr:
            from src.combat.projectile import Projectile
            vx = 700.0 * tr.facing
            p = Projectile(tr.position.x + 32 * tr.facing,
                           tr.position.y + 20,
                           vx, 0, int(25 * self._damage_bonus()),
                           owner_tag="player", color=(0, 220, 255),
                           size=(16, 6), lifetime=0.8, can_pierce=False)
            self._fire_projectile(p)

    def _fire_projectile(self, p) -> None:
        # Will be set if entity manager ref available
        if hasattr(self, "_entity_manager") and self._entity_manager:
            self._entity_manager.add(p, "projectiles")

    def special_2(self) -> None:
        """Aerial Dash — i-frames 3-8."""
        if self._dash_cd > 0:
            return
        tr = self.get(__import__("src.entities.components.transform",
                                   fromlist=["Transform"]).Transform)
        if not tr:
            return
        self.state = self.SPECIAL_2
        self._state_timer = 0.2
        self._special_cds[1] = 0.8
        self._dash_cd = 0.8
        self._dash_active = 0.2
        self._invincible = 0.15
        tr.velocity.x = self.stats.dash_speed * 1.2 * tr.facing
        tr.velocity.y = -100

    def special_3(self) -> None:
        """Grenade — arc trajectory, AoE, 5s cooldown."""
        en = self.get(__import__("src.entities.components.energy",
                                   fromlist=["Energy"]).Energy)
        if not en or not en.consume(20):
            return
        tr = self.get(__import__("src.entities.components.transform",
                                   fromlist=["Transform"]).Transform)
        if not tr:
            return
        self.state = self.SPECIAL_3
        self._state_timer = 0.3
        self._special_cds[2] = 5.0
        from src.combat.projectile import Projectile
        p = Projectile(tr.position.x, tr.position.y,
                       200.0 * tr.facing, -350.0,
                       int(50 * self._damage_bonus()),
                       owner_tag="player", color=(255, 200, 0),
                       size=(12, 12), lifetime=3.0)
        self._fire_projectile(p)
