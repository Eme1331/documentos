"""Grunt — sci-fi goomba that patrols back and forth."""
from __future__ import annotations
import pygame
import math
from src.enemies.base_enemy import BaseEnemy
from src.entities.components.transform import Transform
from src.entities.components.collider import Collider
from src.entities.components.health import Health


def _build_grunt_surf(w: int, h: int) -> pygame.Surface:
    """Draw a chunky alien grunt with the game's neon sci-fi style."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)

    body_col  = (180, 40, 40)
    dark      = (80, 10, 10)
    highlight = (255, 100, 80)
    eye_col   = (255, 200, 0)
    armor_col = (120, 20, 20)

    # Stubby legs
    pygame.draw.rect(s, dark, (4,  h - 14, 12, 14), border_radius=2)
    pygame.draw.rect(s, dark, (w - 16, h - 14, 12, 14), border_radius=2)
    # Feet
    pygame.draw.ellipse(s, armor_col, (2, h - 7, 14, 8))
    pygame.draw.ellipse(s, armor_col, (w - 16, h - 7, 14, 8))

    # Round body — wide and squat
    body_rect = pygame.Rect(2, h // 3, w - 4, h * 2 // 3 - 6)
    pygame.draw.ellipse(s, body_col, body_rect)
    # Body shading — darker bottom half
    shade_rect = pygame.Rect(4, h // 2, w - 8, h // 2 - 10)
    shade_surf = pygame.Surface((shade_rect.w, shade_rect.h), pygame.SRCALPHA)
    pygame.draw.ellipse(shade_surf, (0, 0, 0, 60), (0, 0, shade_rect.w, shade_rect.h))
    s.blit(shade_surf, (shade_rect.x, shade_rect.y))
    # Highlight on top of body
    pygame.draw.ellipse(s, highlight, (w//4, h//3 + 2, w//2, h//6))

    # Armor shoulder pads
    pygame.draw.rect(s, armor_col, (0,  h // 3 + 4, 8, 12), border_radius=2)
    pygame.draw.rect(s, armor_col, (w - 8, h // 3 + 4, 8, 12), border_radius=2)

    # Big round head
    head_r = w // 2 - 2
    head_cx = w // 2
    head_cy = h // 4 + 2
    pygame.draw.circle(s, body_col, (head_cx, head_cy), head_r)
    pygame.draw.circle(s, dark, (head_cx, head_cy), head_r, 2)
    # Head highlight
    pygame.draw.circle(s, highlight, (head_cx - head_r//3, head_cy - head_r//3), head_r//4)

    # Angry eyes (two glowing yellow slits)
    eye_y = head_cy - 2
    pygame.draw.ellipse(s, eye_col, (head_cx - head_r + 6, eye_y - 4, 10, 8))
    pygame.draw.ellipse(s, eye_col, (head_cx + head_r - 16, eye_y - 4, 10, 8))
    # Eye pupils (red)
    pygame.draw.ellipse(s, (255, 0, 0), (head_cx - head_r + 9, eye_y - 2, 5, 5))
    pygame.draw.ellipse(s, (255, 0, 0), (head_cx + head_r - 13, eye_y - 2, 5, 5))
    # Eye glow
    glow = pygame.Surface((14, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 220, 0, 60), (0, 0, 14, 10))
    s.blit(glow, (head_cx - head_r + 4, eye_y - 5))
    s.blit(glow, (head_cx + head_r - 18, eye_y - 5))

    # Angry brow lines
    pygame.draw.line(s, dark, (head_cx - head_r + 6, eye_y - 5),
                     (head_cx - head_r + 14, eye_y - 2), 2)
    pygame.draw.line(s, dark, (head_cx + head_r - 16, eye_y - 5),
                     (head_cx + head_r - 8, eye_y - 2), 2)

    # Small neon stripe on body (tech detail)
    pygame.draw.line(s, (255, 80, 40), (w//2 - 8, h//2 + 2), (w//2 + 8, h//2 + 2), 2)
    pygame.draw.circle(s, (255, 120, 0), (w//2, h//2 + 2), 3)

    return s


class Grunt(BaseEnemy):
    """Patrols left-right, charges at player when nearby."""

    _BASE_STATS = {
        "type": "grunt", "hp": 35, "speed": 75,
        "patrol_dist": 120, "aggro_range": 220,
        "attack_range": 40, "attack_rate": 1.2,
        "xp_value": 12, "width": 36, "height": 40,
    }

    def __init__(self, x: float, y: float, event_bus=None,
                 tile_rects: list | None = None) -> None:
        super().__init__(x, y, self._BASE_STATS, event_bus)
        self._tile_rects = tile_rects or []
        # Replace default placeholder surface with proper art
        w, h = self._BASE_STATS["width"], self._BASE_STATS["height"]
        self._surf = _build_grunt_surf(w, h)
        self._surf_flip = pygame.transform.flip(self._surf, True, False)
        self._anim_time = 0.0

    def set_tile_rects(self, tiles: list) -> None:
        self._tile_rects = tiles

    def update(self, dt: float) -> None:
        self._anim_time += dt
        hp = self.get(Health)
        if hp and hp.is_dead():
            if self.state != self.DEAD:
                self._on_death()
            return

        self._attack_cd = max(0.0, self._attack_cd - dt)
        tr = self.get(Transform)
        col = self.get(Collider)
        if not tr or not col:
            return

        dist = self._player_dist()

        if self.state == self.PATROL:
            tr.velocity.x = self.speed * self._patrol_dir
            dx = tr.position.x - self._patrol_origin.x
            if abs(dx) > self._patrol_dist:
                self._patrol_dir *= -1
            if dist < self.aggro_range:
                self.state = self.CHASE

        elif self.state == self.CHASE:
            if dist > self.aggro_range * 1.5:
                self.state = self.PATROL
            elif dist < self.attack_range:
                self.state = self.ATTACK
                tr.velocity.x = 0
            else:
                ptr = self._player_ref.get(Transform) if self._player_ref else None
                if ptr:
                    sign = 1 if ptr.position.x > tr.position.x else -1
                    tr.velocity.x = self.speed * 1.4 * sign

        elif self.state == self.ATTACK:
            tr.velocity.x = 0
            if dist > self.attack_range * 1.5:
                self.state = self.CHASE
            # damage dealt by gameplay_state collision check

        # Gravity
        tr.velocity.y += 980.0 * dt
        if tr.velocity.y > 900:
            tr.velocity.y = 900

        # Move X and collide
        col.rect.x += int(tr.velocity.x * dt)
        grounded = False
        for tile in self._tile_rects:
            if col.rect.colliderect(tile):
                if tr.velocity.x > 0:
                    col.rect.right = tile.left
                    self._patrol_dir = -1
                elif tr.velocity.x < 0:
                    col.rect.left = tile.right
                    self._patrol_dir = 1
                tr.velocity.x = 0

        # Move Y and collide
        col.rect.y += int(tr.velocity.y * dt)
        for tile in self._tile_rects:
            if col.rect.colliderect(tile):
                if tr.velocity.y > 0:
                    col.rect.bottom = tile.top
                    grounded = True
                elif tr.velocity.y < 0:
                    col.rect.top = tile.bottom
                tr.velocity.y = 0

        tr.position.x = float(col.rect.x)
        tr.position.y = float(col.rect.y)
        tr.velocity.x *= 0.85

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        tr = self.get(Transform)
        col = self.get(Collider)
        if not tr:
            return
        pos = (int(tr.position.x), int(tr.position.y))
        if camera:
            pos = camera.apply_point(pos)

        # Bobbing animation
        bob = int(math.sin(self._anim_time * 6.0) * 2)

        # Draw correct facing direction
        surf = self._surf_flip if self._patrol_dir < 0 else self._surf
        # Flash red when hurt
        if self.state == self.HURT:
            flash = surf.copy()
            flash.fill((255, 80, 80, 160), special_flags=pygame.BLEND_RGBA_ADD)
            surf = flash

        surface.blit(surf, (pos[0], pos[1] + bob))

        # HP bar above
        hp = self.get(Health)
        if hp and hp.hp < hp.max_hp:
            bar_w = self._surf.get_width()
            frac = hp.hp / hp.max_hp
            bx, by = pos[0], pos[1] + bob - 9
            pygame.draw.rect(surface, (60, 0, 0), (bx, by, bar_w, 5), border_radius=2)
            bar_fill = int(bar_w * frac)
            if bar_fill > 0:
                col2 = (0, 200, 80) if frac > 0.5 else (255, 160, 0) if frac > 0.25 else (255, 40, 40)
                pygame.draw.rect(surface, col2, (bx, by, bar_fill, 5), border_radius=2)
            pygame.draw.rect(surface, (180, 60, 60), (bx, by, bar_w, 5), 1, border_radius=2)
