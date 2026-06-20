"""Abstract player base character with full platformer FSM."""
from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from src.entities.entity import Entity
from src.entities.components.transform import Transform
from src.entities.components.collider import Collider
from src.entities.components.health import Health
from src.entities.components.energy import Energy
from src.combat.combo_system import ComboSystem


class CharacterStats:
    def __init__(self, data: dict) -> None:
        self.hp = int(data.get("hp", 100))
        self.energy = int(data.get("energy", 100))
        self.speed = float(data.get("speed", 200))
        self.jump_force = float(data.get("jump_force", 520))
        self.dash_speed = float(data.get("dash_speed", 400))
        self.weight = float(data.get("weight", 1.0))
        self.atk_modifier = float(data.get("atk_modifier", 1.0))
        self.energy_regen = float(data.get("energy_regen", 15.0))

    def apply_modifiers(self, mods: dict) -> None:
        for key, val in mods.items():
            if hasattr(self, key):
                setattr(self, key, getattr(self, key) * float(val))


class BaseCharacter(Entity, ABC):
    # FSM state constants
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    JUMPING = "JUMPING"
    FALLING = "FALLING"
    LANDING = "LANDING"
    DASHING = "DASHING"
    WALL_SLIDING = "WALL_SLIDING"
    WALL_JUMPING = "WALL_JUMPING"
    ATTACK_LIGHT = "ATTACK_LIGHT"
    ATTACK_HEAVY = "ATTACK_HEAVY"
    ATTACK_CHARGED = "ATTACK_CHARGED"
    SPECIAL_1 = "SPECIAL_1"
    SPECIAL_2 = "SPECIAL_2"
    SPECIAL_3 = "SPECIAL_3"
    HURT = "HURT"
    DEAD = "DEAD"

    JUMP_COUNT_MAX = 2  # override per character

    def __init__(self, stats_data: dict) -> None:
        super().__init__()
        self.layer = "player"
        self.add_tag("player")

        self.stats = CharacterStats(stats_data)
        w, h = int(stats_data.get("width", 32)), int(stats_data.get("height", 48))

        tr = Transform(pygame.math.Vector2(200, 400))
        col = Collider(pygame.Rect(0, 0, w, h))
        hp_c = Health(self.stats.hp, self.stats.hp)
        en_c = Energy(self.stats.energy, self.stats.energy, self.stats.energy_regen)
        self.add(tr); self.add(col); self.add(hp_c); self.add(en_c)

        self.combo = ComboSystem()
        self._setup_combos()

        self.state = self.IDLE
        self._state_timer = 0.0
        self._attack_frame = 0
        self._jump_count = 0
        self._grounded = False
        self._dash_cd = 0.0
        self._dash_active = 0.0
        self._special_cds = [0.0, 0.0, 0.0]
        self._hurt_timer = 0.0
        self._land_timer = 0.0
        self._invincible = 0.0

        self._on_tile_rects: list[pygame.Rect] = []
        self._one_way_rects: list[pygame.Rect] = []
        self._event_bus = None

        self._char_color = tuple(stats_data.get("color", [0, 200, 220]))
        self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self._build_surface(w, h)
        self._name = stats_data.get("name", "Player")

    def _build_surface(self, w: int, h: int) -> None:
        """Draw a generic sci-fi soldier silhouette. Override per character."""
        c = self._char_color
        dark = (max(0, c[0]-60), max(0, c[1]-60), max(0, c[2]-60))
        bright = (min(255, c[0]+80), min(255, c[1]+80), min(255, c[2]+80))
        s = self._surf
        # Legs
        pygame.draw.rect(s, dark, (2, h - 16, 10, 16))
        pygame.draw.rect(s, dark, (w - 12, h - 16, 10, 16))
        # Boot detail
        pygame.draw.rect(s, bright, (2, h - 6, 12, 4))
        pygame.draw.rect(s, bright, (w - 14, h - 6, 12, 4))
        # Body
        pygame.draw.rect(s, c, (4, h // 3, w - 8, h // 2), border_radius=3)
        # Chest detail lines
        pygame.draw.line(s, bright, (w//2 - 4, h//3 + 4), (w//2 - 4, h//3 + h//2 - 8), 1)
        pygame.draw.line(s, bright, (w//2 + 4, h//3 + 4), (w//2 + 4, h//3 + h//2 - 8), 1)
        # Shoulders
        pygame.draw.rect(s, c, (0, h // 3, 6, 12), border_radius=2)
        pygame.draw.rect(s, c, (w - 6, h // 3, 6, 12), border_radius=2)
        # Helmet
        hh = h // 3
        pygame.draw.rect(s, dark, (4, 2, w - 8, hh - 2), border_radius=4)
        # Visor
        visor_col = (min(255, c[0]+120), min(255, c[1]+120), min(255, c[2]+40))
        pygame.draw.rect(s, visor_col, (7, 6, w - 14, hh // 2), border_radius=2)
        # Visor shine
        pygame.draw.line(s, (255, 255, 255), (9, 8), (w - 10, 8), 1)
        # Energy core on chest
        pygame.draw.circle(s, visor_col, (w // 2, h // 3 + h // 4), 4)
        pygame.draw.circle(s, (255, 255, 255), (w // 2, h // 3 + h // 4), 2)

    def set_event_bus(self, bus) -> None:
        self._event_bus = bus

    def set_tile_rects(self, tiles: list, one_way: list = None) -> None:
        self._on_tile_rects = tiles
        self._one_way_rects = one_way or []

    def _setup_combos(self) -> None:
        pass

    # --- Abstract interface ---
    @abstractmethod
    def special_1(self) -> None: ...

    @abstractmethod
    def special_2(self) -> None: ...

    @abstractmethod
    def special_3(self) -> None: ...

    @abstractmethod
    def get_stats(self) -> CharacterStats: ...

    # --- Input handling ---
    def handle_input(self, inp) -> None:
        if self.state in (self.DEAD, self.HURT):
            return

        tr = self.get(Transform)
        hp = self.get(Health)
        en = self.get(Energy)

        if inp.just_pressed("JUMP"):
            self.combo.push_action("JUMP")
            self._try_jump(tr)

        if inp.is_held("MOVE_LEFT"):
            if self.state not in (self.DASHING, self.WALL_JUMPING, self.DEAD):
                tr.velocity.x = -self.stats.speed
                tr.facing = -1
                if self.state in (self.IDLE, self.LANDING):
                    self.state = self.RUNNING
        elif inp.is_held("MOVE_RIGHT"):
            if self.state not in (self.DASHING, self.WALL_JUMPING, self.DEAD):
                tr.velocity.x = self.stats.speed
                tr.facing = 1
                if self.state in (self.IDLE, self.LANDING):
                    self.state = self.RUNNING
        else:
            if self.state == self.RUNNING:
                self.state = self.IDLE

        if inp.just_pressed("DASH") and self._dash_cd <= 0:
            self._start_dash(tr)

        if inp.just_pressed("ATTACK_LIGHT"):
            self.combo.push_action("LIGHT")
            if self.state not in (self.DASHING, self.DEAD):
                self._start_attack(self.ATTACK_LIGHT)

        if inp.just_pressed("ATTACK_HEAVY"):
            self.combo.push_action("HEAVY")
            if self.state not in (self.DASHING, self.DEAD):
                self._start_attack(self.ATTACK_HEAVY)

        if inp.just_pressed("SPECIAL_1") and self._special_cds[0] <= 0:
            self.special_1()
        if inp.just_pressed("SPECIAL_2") and self._special_cds[1] <= 0:
            self.special_2()
        if inp.just_pressed("SPECIAL_3") and self._special_cds[2] <= 0:
            self.special_3()

    def _try_jump(self, tr) -> None:
        if self._grounded:
            tr.velocity.y = -self.stats.jump_force
            self._grounded = False
            self._jump_count = 1
            self.state = self.JUMPING
        elif self._jump_count < self.JUMP_COUNT_MAX:
            tr.velocity.y = -self.stats.jump_force * 0.9
            self._jump_count += 1
            self.state = self.JUMPING

    def _start_dash(self, tr) -> None:
        self._dash_cd = 0.8
        self._dash_active = 0.15
        tr.velocity.x = self.stats.dash_speed * tr.facing
        self.state = self.DASHING

    def _start_attack(self, attack_state) -> None:
        self.state = attack_state
        self._attack_frame = 0
        self._state_timer = 0.3

    # --- Physics update ---
    def fixed_update(self, fdt: float) -> None:
        tr = self.get(Transform)
        col = self.get(Collider)
        if not tr or not col:
            return

        from src.physics.collision_resolver import resolve
        prev_vy = tr.velocity.y

        # Apply gravity
        if not self._grounded or tr.velocity.y < 0:
            tr.velocity.y += 980.0 * fdt
            if tr.velocity.y > 900:
                tr.velocity.y = 900

        # Move and collide
        col.rect.x += int(tr.velocity.x * fdt)
        for tile in self._on_tile_rects:
            if col.rect.colliderect(tile):
                if tr.velocity.x > 0:
                    col.rect.right = tile.left
                elif tr.velocity.x < 0:
                    col.rect.left = tile.right
                tr.velocity.x = 0

        was_grounded = self._grounded
        col.rect.y += int(tr.velocity.y * fdt)
        self._grounded = False
        for tile in self._on_tile_rects:
            if col.rect.colliderect(tile):
                if tr.velocity.y > 0:
                    col.rect.bottom = tile.top
                    self._grounded = True
                    self._jump_count = 0
                elif tr.velocity.y < 0:
                    col.rect.top = tile.bottom
                tr.velocity.y = 0

        # One-way platforms
        for tile in self._one_way_rects:
            if col.rect.colliderect(tile) and tr.velocity.y >= 0:
                prev_bottom = col.rect.bottom - int(tr.velocity.y * fdt)
                if prev_bottom <= tile.top + 4:
                    col.rect.bottom = tile.top
                    self._grounded = True
                    self._jump_count = 0
                    tr.velocity.y = 0

        tr.position.x = float(col.rect.x)
        tr.position.y = float(col.rect.y)

        if not was_grounded and self._grounded and prev_vy > 200:
            self.state = self.LANDING
            self._land_timer = 0.1

    def update(self, dt: float) -> None:
        self._state_timer = max(0.0, self._state_timer - dt)
        self._dash_cd = max(0.0, self._dash_cd - dt)
        self._dash_active = max(0.0, self._dash_active - dt)
        self._hurt_timer = max(0.0, self._hurt_timer - dt)
        self._invincible = max(0.0, self._invincible - dt)
        self._special_cds = [max(0.0, c - dt) for c in self._special_cds]

        tr = self.get(Transform)
        en = self.get(Energy)
        if en:
            en.recharge(dt)

        if self.state == self.LANDING and self._land_timer <= 0:
            self.state = self.IDLE
        if self.state in (self.ATTACK_LIGHT, self.ATTACK_HEAVY, self.ATTACK_CHARGED):
            self._attack_frame += 1
            if self._state_timer <= 0:
                self.state = self.IDLE
        if self.state in (self.SPECIAL_1, self.SPECIAL_2, self.SPECIAL_3):
            if self._state_timer <= 0:
                self.state = self.IDLE
        if self.state == self.HURT and self._hurt_timer <= 0:
            self.state = self.IDLE
        if self.state == self.DASHING and self._dash_active <= 0:
            self.state = self.IDLE if self._grounded else self.FALLING

        if tr and not self._grounded:
            if tr.velocity.y > 50 and self.state not in (
                    self.JUMPING, self.DASHING, self.WALL_JUMPING,
                    self.SPECIAL_1, self.SPECIAL_2, self.SPECIAL_3):
                self.state = self.FALLING

        if self._grounded and tr:
            tr.velocity.x *= 0.7

    def take_damage(self, amount: int, source=None) -> None:
        if self._invincible > 0:
            return
        hp = self.get(Health)
        if hp:
            hp.take_damage(amount, source)
            self._invincible = 0.3
            self._hurt_timer = 0.15
            self.state = self.HURT
            # Knockback: empurra o jogador para longe da fonte de dano
            tr = self.get(Transform)
            if tr:
                if source is not None and hasattr(source, "get"):
                    src_tr = source.get(Transform)
                    if src_tr:
                        direction = 1 if tr.position.x >= src_tr.position.x else -1
                    else:
                        direction = tr.facing * -1
                else:
                    direction = tr.facing * -1
                tr.velocity.x = 320.0 * direction
                tr.velocity.y = -220.0
            if self._event_bus:
                from src.core.event_bus import PlayerDamagedEvent
                self._event_bus.emit(PlayerDamagedEvent(amount, source, hp.hp))
            if hp.is_dead():
                self.state = self.DEAD

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        tr = self.get(Transform)
        if not tr:
            return
        pos = (int(tr.position.x), int(tr.position.y))
        if camera:
            pos = camera.apply_point(pos)

        surf = self._surf
        if tr.facing < 0:
            surf = pygame.transform.flip(self._surf, True, False)
        if self._invincible > 0:
            blink = pygame.Surface(self._surf.get_size(), pygame.SRCALPHA)
            blink.fill((255, 255, 255, 120))
            surf = surf.copy()
            surf.blit(blink, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        surface.blit(surf, pos)

        # State debug label (small)
        col = self.get(Collider)
        if col:
            hp = self.get(Health)
            if hp:
                bar_w = col.rect.width
                frac = hp.hp / hp.max_hp
                bx, by = pos[0], pos[1] - 10
                pygame.draw.rect(surface, (80, 0, 0), (bx, by, bar_w, 5))
                pygame.draw.rect(surface, (0, 220, 100),
                                 (bx, by, int(bar_w * frac), 5))
