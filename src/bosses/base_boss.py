"""Abstract boss with phase system and arena lock."""
from __future__ import annotations
import pygame
from src.entities.entity import Entity
from src.entities.components.transform import Transform
from src.entities.components.collider import Collider
from src.entities.components.health import Health
from src.bosses.phase_controller import BossPhase, AttackPattern


class BaseBoss(Entity):
    def __init__(self, x: float, y: float, stats: dict,
                 event_bus=None) -> None:
        super().__init__()
        self.layer = "enemies"
        self.add_tag("boss")

        self._eb = event_bus
        self.stats = stats
        self.boss_name = stats.get("name", "Boss")
        self.phases: list[BossPhase] = []
        self.current_phase_idx = 0
        self.arena_rect: pygame.Rect | None = None
        self._arena_locked = False
        self._dead = False
        self._enraged = False

        w, h = int(stats.get("width", 64)), int(stats.get("height", 96))
        self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = tuple(stats.get("color", [255, 80, 0]))
        self._surf.fill(color)

        tr = Transform(pygame.math.Vector2(x, y))
        col = Collider(pygame.Rect(0, 0, w, h))
        max_hp = int(stats.get("hp", 500))
        hp_comp = Health(max_hp, max_hp)
        self.add(tr); self.add(col); self.add(hp_comp)

        self._player_ref = None
        self._setup_phases()

    def _setup_phases(self) -> None:
        self.phases = [
            BossPhase(1, 1.0, [AttackPattern("basic_attack", 1.0, 2.0)]),
            BossPhase(2, 0.5, [AttackPattern("phase2_attack", 1.0, 1.5),
                               AttackPattern("special_attack", 0.5, 4.0)],
                      speed_multiplier=1.3, damage_multiplier=1.2),
        ]

    def set_player(self, player) -> None:
        self._player_ref = player

    @property
    def current_phase(self) -> BossPhase:
        return self.phases[min(self.current_phase_idx, len(self.phases) - 1)]

    def enter_arena(self) -> None:
        self._arena_locked = True

    def check_phase_transition(self) -> bool:
        hp = self.get(Health)
        if not hp:
            return False
        frac = hp.hp / hp.max_hp
        next_idx = self.current_phase_idx + 1
        if next_idx < len(self.phases):
            if frac <= self.phases[next_idx].hp_threshold:
                self.current_phase_idx = next_idx
                self._on_phase_change(next_idx)
                return True
        return False

    def _on_phase_change(self, phase_idx: int) -> None:
        if self._eb:
            from src.core.event_bus import BossPhaseChangedEvent
            self._eb.emit(BossPhaseChangedEvent(
                boss_name=self.boss_name,
                new_phase=phase_idx + 1,
                total_phases=len(self.phases),
            ))

    def on_death(self) -> None:
        self._dead = True
        self._arena_locked = False
        self.active = False

    def execute_current_pattern(self, dt: float) -> None:
        phase = self.current_phase
        for p in phase.attack_patterns:
            p.tick(dt)
        pattern = phase.pick_pattern()
        if pattern:
            self._execute_pattern(pattern)
            pattern.reset()

    def _execute_pattern(self, pattern: AttackPattern) -> None:
        pass

    def update(self, dt: float) -> None:
        hp = self.get(Health)
        if hp and hp.is_dead() and not self._dead:
            self.on_death()
            return

        self.check_phase_transition()
        self._update_movement(dt)
        self.execute_current_pattern(dt)

        tr = self.get(Transform)
        col = self.get(Collider)
        if tr and col:
            tr.velocity.y += 980.0 * dt
            if tr.velocity.y > 900:
                tr.velocity.y = 900
            tr.position += tr.velocity * dt
            col.rect.topleft = (int(tr.position.x), int(tr.position.y))
            tr.velocity.x *= 0.85

    def _update_movement(self, dt: float) -> None:
        if not self._player_ref:
            return
        tr = self.get(Transform)
        ptr = self._player_ref.get(Transform)
        if not tr or not ptr:
            return
        phase = self.current_phase
        spd = 60.0 * phase.speed_multiplier
        dx = ptr.position.x - tr.position.x
        tr.velocity.x = spd * (1 if dx > 0 else -1)
        tr.facing = 1 if dx > 0 else -1

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        tr = self.get(Transform)
        if not tr:
            return
        pos = (int(tr.position.x), int(tr.position.y))
        if camera:
            pos = camera.apply_point(pos)
        surface.blit(self._surf, pos)

        hp = self.get(Health)
        if hp:
            bar_w = self._surf.get_width()
            frac = hp.hp / hp.max_hp
            pygame.draw.rect(surface, (100, 0, 0), (pos[0], pos[1] - 12, bar_w, 8))
            pygame.draw.rect(surface, (255, 80, 0),
                             (pos[0], pos[1] - 12, int(bar_w * frac), 8))
