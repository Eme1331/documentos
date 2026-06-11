"""Level 1 boss: Titan-X Drone."""
from __future__ import annotations
import pygame
from src.bosses.base_boss import BaseBoss
from src.bosses.phase_controller import BossPhase, AttackPattern


class TitanXDrone(BaseBoss):
    def __init__(self, x, y, stats, event_bus=None):
        merged = {"name": "Titan-X Drone", "hp": 400, "width": 64, "height": 64,
                  "color": [100, 150, 220], **stats}
        super().__init__(x, y, merged, event_bus)

    def _setup_phases(self):
        self.phases = [
            BossPhase(1, 1.0, [
                AttackPattern("missile_barrage", 1.0, 2.5),
                AttackPattern("laser_sweep", 0.6, 5.0),
            ]),
            BossPhase(2, 0.5, [
                AttackPattern("missile_barrage", 1.0, 1.5),
                AttackPattern("dual_laser", 1.0, 3.5),
                AttackPattern("dash_ram", 0.7, 4.0),
            ], speed_multiplier=1.4, damage_multiplier=1.3),
        ]

    def _execute_pattern(self, pattern):
        tr = self.get(__import__("src.entities.components.transform", fromlist=["Transform"]).Transform)
        if not tr or not self._player_ref:
            return
        from src.combat.projectile import Projectile
        import math
        ptr = self._player_ref.get(type(tr))
        if not ptr:
            return
        if "missile" in pattern.name:
            for offset in [-30, 0, 30]:
                dx = ptr.position.x - tr.position.x + offset
                dy = ptr.position.y - tr.position.y
                l = max((dx*dx+dy*dy)**0.5, 1)
                p = Projectile(tr.position.x, tr.position.y,
                               dx/l*250, dy/l*250, 20,
                               owner_tag="enemy", color=(255,120,0))
                # projectiles would be added via entity manager if available
        elif "laser" in pattern.name:
            tr.velocity.x = 0
