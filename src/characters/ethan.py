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
        self._attack_rect: pygame.Rect | None = None

    def update(self, dt: float) -> None:
        super().update(dt)
        from src.entities.components.transform import Transform
        from src.entities.components.collider import Collider
        tr = self.get(Transform)
        col = self.get(Collider)
        if col and tr:
            if self.state == self.ATTACK_LIGHT and self._state_timer > 0.1:
                rw, rh = 44, 36
                rx = col.rect.right if tr.facing == 1 else col.rect.left - rw
                ry = col.rect.centery - rh // 2
                self._attack_rect = pygame.Rect(rx, ry, rw, rh)
            elif self.state == self.ATTACK_HEAVY and self._state_timer > 0.15:
                rw, rh = 56, 44
                rx = col.rect.right if tr.facing == 1 else col.rect.left - rw
                ry = col.rect.centery - rh // 2
                self._attack_rect = pygame.Rect(rx, ry, rw, rh)
            else:
                self._attack_rect = None
        else:
            self._attack_rect = None

    @property
    def attack_damage(self) -> int:
        if self.state == self.ATTACK_LIGHT:
            return 15
        if self.state == self.ATTACK_HEAVY:
            return 30
        return 0

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        super().draw(surface, camera)
        if self._attack_rect and self.state in (self.ATTACK_LIGHT, self.ATTACK_HEAVY):
            tr = self.get(__import__("src.entities.components.transform",
                                      fromlist=["Transform"]).Transform)
            if tr:
                pos = (int(self._attack_rect.x), int(self._attack_rect.y))
                if camera:
                    pos = camera.apply_point(pos)
                slash = pygame.Surface((self._attack_rect.w, self._attack_rect.h), pygame.SRCALPHA)
                slash.fill((0, 220, 255, 100))
                surface.blit(slash, pos)
                pygame.draw.rect(surface, (0, 255, 255),
                                  (*pos, self._attack_rect.w, self._attack_rect.h), 2)

    def _build_surface(self, w: int, h: int) -> None:
        s = self._surf
        c = (0, 180, 255)
        dark = (0, 60, 120)
        # Legs with boots
        pygame.draw.rect(s, (0, 80, 140), (3, h - 18, 10, 18))
        pygame.draw.rect(s, (0, 80, 140), (w - 13, h - 18, 10, 18))
        pygame.draw.rect(s, dark, (2, h - 7, 13, 7))
        pygame.draw.rect(s, dark, (w - 15, h - 7, 13, 7))
        # Body armor
        pygame.draw.rect(s, c, (3, h // 3, w - 6, h // 2 + 2), border_radius=3)
        # Chest plate detail
        pygame.draw.rect(s, (0, 100, 200), (6, h//3 + 4, w - 12, 8), border_radius=2)
        pygame.draw.line(s, (100, 220, 255), (w//2, h//3 + 6), (w//2, h//3 + h//2 - 4), 1)
        # Shoulder pads
        pygame.draw.rect(s, dark, (0, h // 3, 5, 14), border_radius=2)
        pygame.draw.rect(s, dark, (w - 5, h // 3, 5, 14), border_radius=2)
        # Helmet — military style
        pygame.draw.rect(s, dark, (3, 2, w - 6, h // 3 - 2), border_radius=3)
        pygame.draw.rect(s, (0, 40, 100), (3, 2, w - 6, 5))
        # Visor — cyan
        pygame.draw.rect(s, (0, 220, 255), (6, 7, w - 12, 8), border_radius=2)
        pygame.draw.line(s, (200, 255, 255), (8, 9), (w - 9, 9), 1)
        # Plasma rifle on right side
        pygame.draw.rect(s, (20, 20, 50), (w - 3, h // 3 + 4, 8, 5))
        pygame.draw.rect(s, (0, 180, 255), (w + 1, h // 3 + 5, 6, 3))
        # Energy core
        pygame.draw.circle(s, (0, 255, 255), (w // 2, h // 3 + h // 4), 4)
        pygame.draw.circle(s, (255, 255, 255), (w // 2, h // 3 + h // 4), 2)

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
                       240.0 * tr.facing, -200.0,
                       int(50 * self._damage_bonus()),
                       owner_tag="player", color=(255, 200, 0),
                       size=(12, 12), lifetime=2.5, gravity=700.0)
        self._fire_projectile(p)
