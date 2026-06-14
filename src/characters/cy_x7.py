"""CY-X7 — Cyborg Warrior."""
from __future__ import annotations
import pygame
from src.characters.base_character import BaseCharacter, CharacterStats
from src.combat.combo_system import ComboDefinition


class CYX7(BaseCharacter):
    JUMP_COUNT_MAX = 2

    def __init__(self, stats_data: dict) -> None:
        merged = {"name": "CY-X7", "color": [150, 80, 220],
                  "width": 36, "height": 52, **stats_data}
        super().__init__(merged)
        self._build_surface(merged.get("width", 36), merged.get("height", 52))
        self._armor_intact = True
        self._armor_regen_timer = 0.0
        self._overclock_active = False
        self._overclock_timer = 0.0
        self._arm_mode = "cannon"  # "blade" | "cannon"

    def _build_surface(self, w: int, h: int) -> None:
        self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
        s = self._surf
        c = (150, 80, 220)
        dark = (50, 20, 90)
        metal = (80, 80, 110)
        # Heavy legs — angular cyborg
        pygame.draw.rect(s, dark, (2, h - 20, 12, 20))
        pygame.draw.rect(s, dark, (w - 14, h - 20, 12, 20))
        pygame.draw.rect(s, metal, (2, h - 8, 14, 8))
        pygame.draw.rect(s, metal, (w - 16, h - 8, 14, 8))
        # Thick body armor
        pygame.draw.rect(s, c, (2, h // 3, w - 4, h // 2 + 4), border_radius=2)
        # Armor plates
        pygame.draw.rect(s, dark, (2, h // 3, w - 4, 6))
        pygame.draw.rect(s, (180, 100, 255), (4, h//3 + 8, w - 8, 6), border_radius=1)
        # Circuit lines
        pygame.draw.line(s, (200, 150, 255), (5, h//3 + 18), (w - 5, h//3 + 18), 1)
        pygame.draw.line(s, (200, 150, 255), (w//2, h//3 + 18), (w//2, h//3 + h//2 - 6), 1)
        # Big shoulder plates
        pygame.draw.rect(s, dark, (0, h // 3 - 2, 8, 18), border_radius=2)
        pygame.draw.rect(s, dark, (w - 8, h // 3 - 2, 8, 18), border_radius=2)
        pygame.draw.line(s, (200, 150, 255), (0, h // 3 + 4), (8, h // 3 + 4), 1)
        pygame.draw.line(s, (200, 150, 255), (w - 8, h // 3 + 4), (w, h // 3 + 4), 1)
        # Mechanical arm (right side) — cannon
        pygame.draw.rect(s, metal, (w - 4, h // 3 + 8, 10, 8), border_radius=2)
        pygame.draw.circle(s, (255, 80, 80), (w + 4, h // 3 + 12), 4)
        # Blocky helmet
        pygame.draw.rect(s, dark, (2, 1, w - 4, h // 3 - 1), border_radius=2)
        pygame.draw.rect(s, (30, 10, 60), (2, 1, w - 4, 5))
        # Red eye visor
        pygame.draw.rect(s, (180, 0, 0), (5, 7, w - 10, 7), border_radius=1)
        pygame.draw.line(s, (255, 80, 80), (7, 10), (w - 8, 10), 2)
        pygame.draw.circle(s, (255, 0, 0), (w // 2, 10), 3)
        # Power core
        pygame.draw.circle(s, (180, 80, 255), (w // 2, h // 3 + h // 4), 5)
        pygame.draw.circle(s, (255, 200, 255), (w // 2, h // 3 + h // 4), 2)

    def get_stats(self) -> CharacterStats:
        return self.stats

    def _setup_combos(self) -> None:
        self.combo.add_combo(ComboDefinition(
            "OverclockSlam", ["HEAVY", "HEAVY", "SPECIAL"],
            max_gap_ms=500, multiplier=2.0))

    def update(self, dt: float) -> None:
        super().update(dt)
        # Armor regen — only when not in active combat (regen timer is long: 8s)
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
            self._armor_regen_timer = 8.0
            # Absorb but still apply brief invincibility so next hit deals damage
            self._invincible = 0.1
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
