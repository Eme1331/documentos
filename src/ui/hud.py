"""HUD compositor."""
from __future__ import annotations
import pygame
from src.ui.hp_bar import HPBar
from src.ui.energy_bar import EnergyBar
from src.ui.minimap import Minimap
from src.ui.skill_display import SkillDisplay
from src.ui.quick_inventory import QuickInventory
from src.ui.objective_tracker import ObjectiveTracker
import settings


class HUD:
    def __init__(self) -> None:
        sw, sh = settings.SCREEN_SIZE
        self.hp_bar = HPBar(10, 10, 200, 16)
        self.energy_bar = EnergyBar(10, 32, 200, 10)
        self.minimap = Minimap(sw)
        self.skills = SkillDisplay(sw, sh)
        self.inventory = QuickInventory(sw, sh)
        self.objectives = ObjectiveTracker(sw)
        self._boss_hp_frac: float | None = None
        self._boss_name = ""
        self._surf = pygame.Surface(settings.SCREEN_SIZE, pygame.SRCALPHA)

    def set_objective(self, text: str) -> None:
        self.objectives.set_objective(text)

    def show_boss(self, name: str, frac: float) -> None:
        self._boss_name = name
        self._boss_hp_frac = frac

    def hide_boss(self) -> None:
        self._boss_hp_frac = None

    def update(self, player, dt: float, map_size: tuple = (2560, 960)) -> None:
        from src.entities.components.health import Health
        from src.entities.components.energy import Energy
        from src.entities.components.transform import Transform

        hp_c = player.get(Health) if player else None
        en_c = player.get(Energy) if player else None
        tr = player.get(Transform) if player else None

        if hp_c:
            self.hp_bar.update(hp_c.hp, hp_c.max_hp, dt)
        if en_c:
            self.energy_bar.update(en_c.energy, en_c.max_energy, dt)
        if tr:
            self.minimap.update((tr.position.x, tr.position.y), map_size)
        self.objectives.update(dt)

        if player:
            cds = getattr(player, "_special_cds", [0.0, 0.0, 0.0])
            self.skills.draw.__doc__  # touch
            self._cds = cds
        else:
            self._cds = [0.0, 0.0, 0.0]

    def draw(self, surface: pygame.Surface) -> None:
        self._surf.fill((0, 0, 0, 0))

        self.hp_bar.draw(self._surf)
        self.energy_bar.draw(self._surf)
        self.minimap.draw(self._surf)

        max_cds = [0.8, 0.8, 5.0]
        self.skills.draw(self._surf, getattr(self, "_cds", [0,0,0]), max_cds)
        self.inventory.draw(self._surf)
        self.objectives.draw(self._surf)

        if self._boss_hp_frac is not None:
            self._draw_boss_bar(self._surf)

        surface.blit(self._surf, (0, 0))

    def _draw_boss_bar(self, surface: pygame.Surface) -> None:
        sw = settings.SCREEN_WIDTH
        bw = sw - 200
        bx = 100
        by = settings.SCREEN_HEIGHT - 30
        pygame.draw.rect(surface, (60, 0, 0), (bx, by, bw, 14), border_radius=3)
        fw = int(bw * max(0.0, self._boss_hp_frac))
        pygame.draw.rect(surface, (255, 80, 0), (bx, by, fw, 14), border_radius=3)
        pygame.draw.rect(surface, (200, 100, 40), (bx, by, bw, 14), 1, border_radius=3)
        try:
            font = pygame.font.SysFont("consolas", 13, bold=True)
            lbl = font.render(self._boss_name, True, (255, 200, 100))
            surface.blit(lbl, (bx + bw // 2 - lbl.get_width() // 2, by - 18))
        except Exception:
            pass
