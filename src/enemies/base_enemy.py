"""Abstract enemy with patrol/aggro FSM."""
from __future__ import annotations
import pygame
from src.entities.entity import Entity
from src.entities.components.transform import Transform
from src.entities.components.collider import Collider
from src.entities.components.health import Health


class BaseEnemy(Entity):
    PATROL = "PATROL"
    CHASE = "CHASE"
    ATTACK = "ATTACK"
    HURT = "HURT"
    DEAD = "DEAD"

    def __init__(self, x: float, y: float, stats: dict,
                 event_bus=None) -> None:
        super().__init__()
        self.layer = "enemies"
        self.add_tag("enemy")

        self._eb = event_bus
        self.stats = stats
        self.state = self.PATROL
        self._state_timer = 0.0

        self.speed = float(stats.get("speed", 80))
        self.aggro_range = float(stats.get("aggro_range", 250))
        self.attack_range = float(stats.get("attack_range", 60))
        self.xp_value = int(stats.get("xp_value", 10))
        self.enemy_type = stats.get("type", "grunt")

        self._patrol_dir = 1
        self._patrol_dist = float(stats.get("patrol_dist", 120))
        self._patrol_origin = pygame.math.Vector2(x, y)
        self._attack_cd = 0.0
        self._attack_rate = float(stats.get("attack_rate", 1.5))

        w, h = int(stats.get("width", 32)), int(stats.get("height", 48))
        tr = Transform(pygame.math.Vector2(x, y))
        col = Collider(pygame.Rect(0, 0, w, h))
        hp_comp = Health(int(stats.get("hp", 40)), int(stats.get("hp", 40)))
        self.add(tr); self.add(col); self.add(hp_comp)

        self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = tuple(stats.get("color", [220, 60, 60]))
        self._surf.fill(color)

        self._player_ref = None

    def set_player(self, player) -> None:
        self._player_ref = player

    def _player_dist(self) -> float:
        if not self._player_ref:
            return 9999
        tr = self.get(Transform)
        ptr = self._player_ref.get(Transform)
        if not tr or not ptr:
            return 9999
        return tr.position.distance_to(ptr.position)

    def update(self, dt: float) -> None:
        hp = self.get(Health)
        if hp and hp.is_dead():
            if self.state != self.DEAD:
                self._on_death()
            return

        self._attack_cd = max(0.0, self._attack_cd - dt)
        tr = self.get(Transform)
        col = self.get(Collider)

        dist = self._player_dist()

        if self.state == self.PATROL:
            tr.velocity.x = self.speed * self._patrol_dir
            dx = tr.position.x - self._patrol_origin.x
            if abs(dx) > self._patrol_dist:
                self._patrol_dir *= -1
                tr.facing = self._patrol_dir
            if dist < self.aggro_range:
                self.state = self.CHASE

        elif self.state == self.CHASE:
            if dist > self.aggro_range * 1.5:
                self.state = self.PATROL
            elif dist < self.attack_range:
                self.state = self.ATTACK
            else:
                ptr = self._player_ref.get(Transform) if self._player_ref else None
                if ptr:
                    dx = ptr.position.x - tr.position.x
                    tr.velocity.x = self.speed * (1 if dx > 0 else -1)
                    tr.facing = 1 if dx > 0 else -1

        elif self.state == self.ATTACK:
            tr.velocity.x = 0
            if dist > self.attack_range * 1.5:
                self.state = self.CHASE
            elif self._attack_cd <= 0:
                self._do_attack()
                self._attack_cd = self._attack_rate

        # Apply gravity
        tr.velocity.y += 980.0 * dt
        if tr.velocity.y > 900:
            tr.velocity.y = 900
        tr.position += tr.velocity * dt
        if col:
            col.rect.topleft = (int(tr.position.x), int(tr.position.y))
        tr.velocity.x *= 0.8

    def _do_attack(self) -> None:
        pass

    def _on_death(self) -> None:
        self.state = self.DEAD
        self.active = False
        if self._eb:
            from src.core.event_bus import EnemyDiedEvent
            tr = self.get(Transform)
            pos = (tr.position.x, tr.position.y) if tr else (0, 0)
            self._eb.emit(EnemyDiedEvent(
                enemy_id=self.id,
                xp_reward=self.xp_value,
                position=pos,
                enemy_type=self.enemy_type,
            ))

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        tr = self.get(Transform)
        if not tr:
            return
        pos = (int(tr.position.x), int(tr.position.y))
        if camera:
            pos = camera.apply_point(pos)
        surface.blit(self._surf, pos)

        # HP bar
        hp = self.get(Health)
        if hp:
            bar_w = self._surf.get_width()
            frac = hp.hp / hp.max_hp
            pygame.draw.rect(surface, (80, 0, 0), (pos[0], pos[1] - 8, bar_w, 5))
            pygame.draw.rect(surface, (220, 60, 60),
                             (pos[0], pos[1] - 8, int(bar_w * frac), 5))
