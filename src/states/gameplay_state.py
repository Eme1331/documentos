"""Core gameplay state: physics, entities, rendering, HUD."""
from __future__ import annotations
import pygame
from src.core.state_machine import GameState
from src.ui.hud import HUD
from src.fx.particle_system import ParticleSystem
from src.fx.screen_effects import ScreenEffects
from src.fx.lighting import LightingSystem, LightSource
import settings


class GameplayState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._time = 0.0
        self._paused = False

        # Subsystems
        self.hud = HUD()
        self.particles = ParticleSystem()
        self.fx = ScreenEffects()
        self.lighting = LightingSystem(settings.SCREEN_SIZE)

        # Level manager
        from src.levels.level_manager import LevelManager
        self.level_manager = LevelManager(game.event_bus)

        # Load level
        level_id = game.session.get("level_id", "level_01")
        save = game.session.get("save_data")
        if save:
            level_id = save.get("current_level_id", level_id)
        self.level = self.level_manager.load(level_id)

        # Create player
        char_id = game.session.get("character", "ethan")
        from src.characters.character_factory import create_character
        self.player = create_character(char_id)
        self.player.set_event_bus(game.event_bus)
        self.player._entity_manager = self.level.entity_manager

        # Place player at spawn
        spawn = self.level.spawn_point
        from src.entities.components.transform import Transform
        from src.entities.components.collider import Collider
        tr = self.player.get(Transform)
        col = self.player.get(Collider)
        if tr:
            tr.position.x = float(spawn[0])
            tr.position.y = float(spawn[1])
        if col:
            col.rect.topleft = (int(spawn[0]), int(spawn[1]))

        self.level.entity_manager.add(self.player, "player")
        self.level.entity_manager.flush()

        # Set tile rects on player
        self.player.set_tile_rects(
            self.level.tile_map.collision_rects,
            self.level.tile_map.one_way_rects)

        # Camera
        from src.core.camera import Camera
        self.camera = Camera(
            settings.SCREEN_SIZE,
            (self.level.tile_map.pixel_width, self.level.tile_map.pixel_height))

        # XP system
        from src.progression.xp_system import XPSystem
        self.xp_system = XPSystem(game.event_bus)

        # Subscribe events
        game.event_bus.subscribe(
            __import__("src.core.event_bus", fromlist=["PlayerDamagedEvent"]).PlayerDamagedEvent,
            self._on_player_damaged)

        # Set initial objective
        if self.level.data.get("objectives"):
            self.hud.set_objective(self.level.data["objectives"][0])

        # Boss (will be activated later)
        self._boss = None
        self._boss_spawned = False

    def on_exit(self) -> None:
        pass

    def _on_player_damaged(self, event) -> None:
        self.fx.shake(6.0, 0.2)
        self.fx.flash((255, 60, 60), 120, 0.1)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.states.pause_state import PauseState
            self.game.state_machine.push(PauseState(self.game, self))

    def fixed_update(self, fdt: float) -> None:
        self.player.fixed_update(fdt)

    def update(self, dt: float) -> None:
        effective_dt = self.fx.update(dt)
        self._time += dt

        self.player.handle_input(self.game.input)
        self.player.update(effective_dt)

        self.level.update(effective_dt)

        # Update enemy player references and tile rects
        for enemy in self.level.entity_manager.get_all("enemies"):
            if hasattr(enemy, "set_player"):
                enemy.set_player(self.player)
            if hasattr(enemy, "set_tile_rects") and not getattr(enemy, "_tiles_set", False):
                enemy.set_tile_rects(self.level.tile_map.collision_rects)
                enemy._tiles_set = True

        self._check_enemy_hits()
        self._check_boss_spawn()
        self._check_checkpoints()
        self._check_door()

        # Camera follows player
        from src.entities.components.transform import Transform
        tr = self.player.get(Transform)
        if tr:
            from src.entities.components.collider import Collider
            col = self.player.get(Collider)
            r = col.rect if col else pygame.Rect(tr.position.x, tr.position.y, 32, 48)
            self.camera.follow(r, effective_dt)

            # Player light
            self.lighting.clear()
            self.lighting.add(LightSource(tr.position.x + 16, tr.position.y + 24,
                                           settings.NEON_CYAN, 180, 1.0))

        # Particles - player trail when dashing
        if tr and self.player.state == "DASHING":
            self.particles.trail(tr.position.x + 16, tr.position.y + 24,
                                  color_start=settings.NEON_CYAN,
                                  color_end=(0, 80, 120))

        self.particles.update(effective_dt)
        self.hud.update(self.player, effective_dt,
                        (self.level.tile_map.pixel_width,
                         self.level.tile_map.pixel_height))

        # Death check
        from src.entities.components.health import Health
        hp = self.player.get(Health)
        if hp and hp.is_dead():
            from src.states.game_over_state import GameOverState
            self.game.state_machine.change(GameOverState(self.game))

    def _check_enemy_hits(self) -> None:
        from src.entities.components.collider import Collider
        from src.entities.components.health import Health
        from src.entities.components.transform import Transform
        player_tr = self.player.get(Transform)
        player_col = self.player.get(Collider)
        if not player_tr:
            return

        for enemy in list(self.level.entity_manager.get_all("enemies")):
            if not enemy.active:
                continue
            etr = enemy.get(Transform)
            ecol = enemy.get(Collider)
            if etr:
                dx = abs(player_tr.position.x - etr.position.x)
                dy = abs(player_tr.position.y - etr.position.y)
                if dx < 36 and dy < 40:
                    self.player.take_damage(10, enemy)
            # Check player projectiles hitting enemies
        for proj in list(self.level.entity_manager.get_all("projectiles")):
            if not proj.active or not proj.has_tag("player"):
                continue
            pcol = proj.get(Collider)
            if not pcol:
                continue
            for enemy in list(self.level.entity_manager.get_all("enemies")):
                if not enemy.active:
                    continue
                ecol = enemy.get(Collider)
                if ecol and pcol.rect.colliderect(ecol.rect):
                    ehp = enemy.get(Health)
                    if ehp:
                        ehp.take_damage(proj.damage)
                        self.particles.burst(
                            ecol.rect.centerx, ecol.rect.centery,
                            count=8, color_start=(255, 150, 0), color_end=(255, 50, 0))
                    if not proj.can_pierce:
                        proj.active = False

    def _check_boss_spawn(self) -> None:
        if self._boss_spawned or not self.level.boss_id:
            return
        from src.entities.components.transform import Transform
        tr = self.player.get(Transform)
        if tr and tr.position.x > self.level.tile_map.pixel_width * 0.75:
            self._spawn_boss()

    def _spawn_boss(self) -> None:
        self._boss_spawned = True
        from src.bosses.boss_factory import create_boss
        boss = create_boss(self.level.boss_id,
                            self.level.tile_map.pixel_width * 0.8,
                            self.level.tile_map.pixel_height * 0.7,
                            self.game.event_bus)
        boss.set_player(self.player)
        self.level.entity_manager.add(boss, "enemies")
        self._boss = boss
        self.hud.show_boss(boss.boss_name, 1.0)
        self.fx.flash((255, 100, 0), 180, 0.3)

        from src.states.boss_intro_state import BossIntroState
        self.game.state_machine.push(BossIntroState(self.game, boss.boss_name))

    def _update_boss_hud(self) -> None:
        if self._boss and self._boss.active:
            from src.entities.components.health import Health
            hp = self._boss.get(Health)
            if hp:
                self.hud.show_boss(self._boss.boss_name, hp.hp / hp.max_hp)
        elif self._boss and not self._boss.active:
            self.hud.hide_boss()

    def _check_checkpoints(self) -> None:
        from src.entities.components.collider import Collider
        col = self.player.get(Collider)
        if col:
            for cp in self.level.checkpoints:
                cp.check_player(col.rect)

    def _check_door(self) -> None:
        door = self.level._door
        if not door:
            return
        from src.entities.components.collider import Collider
        col = self.player.get(Collider)
        if col and door.check_player(col.rect):
            self._transition_to_next_level(door.next_level_id)

    def _transition_to_next_level(self, next_level_id: str) -> None:
        self.fx.flash((0, 200, 255), 255, 0.6)
        self.game.session["level_id"] = next_level_id
        # Small delay via level_transition state, then reload gameplay
        from src.states.level_transition_state import LevelTransitionState
        self.game.state_machine.change(
            LevelTransitionState(self.game, next_level_id))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.COLOR_BG)
        ox, oy = int(self.fx.shake_offset[0]), int(self.fx.shake_offset[1])

        self.level.draw(surface, self.camera)
        self.particles.draw(surface, self.camera)
        self.lighting.draw(surface, self.camera)

        self.fx.draw_overlay(surface)
        self.hud.draw(surface)
        self._update_boss_hud()
