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
        self._build_surface(merged.get("width", 30), merged.get("height", 44))
        self._gravity_field_timer = 0.0

    def _build_surface(self, w: int, h: int) -> None:
        self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
        s = self._surf
        c = (220, 80, 255)
        dark = (80, 20, 110)
        # Aura glow (outer rings, drawn first)
        aura = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (180, 50, 255, 30), (0, 0, w + 8, h + 8))
        pygame.draw.ellipse(aura, (220, 80, 255, 20), (2, 2, w + 4, h + 4))
        s.blit(aura, (-4, -4))
        # Slender legs
        pygame.draw.rect(s, dark, (4, h - 15, 8, 15))
        pygame.draw.rect(s, dark, (w - 12, h - 15, 8, 15))
        # Glowing feet
        pygame.draw.ellipse(s, c, (2, h - 6, 10, 6))
        pygame.draw.ellipse(s, c, (w - 12, h - 6, 10, 6))
        # Lithe body
        pygame.draw.rect(s, c, (4, h // 3, w - 8, h // 2), border_radius=4)
        # Energy lines on body
        pygame.draw.line(s, (255, 180, 255), (w//2, h//3 + 3), (w//2, h//3 + h//2 - 5), 1)
        pygame.draw.line(s, (255, 180, 255), (6, h//3 + h//4), (w - 6, h//3 + h//4), 1)
        # Floating hair / antenna
        pygame.draw.line(s, c, (w//2, 0), (w//2 - 4, 5), 2)
        pygame.draw.line(s, c, (w//2, 0), (w//2 + 4, 4), 2)
        pygame.draw.circle(s, (255, 200, 255), (w//2 - 5, 3), 2)
        pygame.draw.circle(s, (255, 200, 255), (w//2 + 5, 2), 2)
        # Alien head — slightly elongated
        pygame.draw.ellipse(s, dark, (3, 4, w - 6, h // 3 - 3))
        # Glowing eyes
        pygame.draw.ellipse(s, (255, 100, 255), (6, 10, 7, 5))
        pygame.draw.ellipse(s, (255, 100, 255), (w - 13, 10, 7, 5))
        pygame.draw.circle(s, (255, 255, 255), (9, 12), 2)
        pygame.draw.circle(s, (255, 255, 255), (w - 10, 12), 2)
        # Quantum orb on chest
        pygame.draw.circle(s, (255, 120, 255), (w // 2, h // 3 + h // 4), 5)
        pygame.draw.circle(s, (255, 255, 255), (w // 2, h // 3 + h // 4), 2)
        pygame.draw.circle(s, (220, 80, 255), (w // 2, h // 3 + h // 4), 5, 1)

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
