"""Pause menu."""
from __future__ import annotations
import pygame
import settings

OPTIONS = ["RESUME", "SKILL TREE", "INVENTORY", "SETTINGS", "MAIN MENU"]


class PauseMenu:
    def __init__(self) -> None:
        self._selected = 0
        try:
            self._font = pygame.font.SysFont("consolas", 22)
            self._font_title = pygame.font.SysFont("consolas", 32, bold=True)
        except Exception:
            self._font = self._font_title = None

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._selected = (self._selected - 1) % len(OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected + 1) % len(OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return OPTIONS[self._selected]
            elif event.key == pygame.K_ESCAPE:
                return "RESUME"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        sw, sh = settings.SCREEN_SIZE
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 180))
        surface.blit(overlay, (0, 0))

        panel_w, panel_h = 320, 340
        px = sw // 2 - panel_w // 2
        py = sh // 2 - panel_h // 2
        pygame.draw.rect(surface, (10, 10, 30), (px, py, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surface, settings.NEON_PURPLE, (px, py, panel_w, panel_h), 2, border_radius=8)

        if self._font_title:
            t = self._font_title.render("PAUSED", True, settings.NEON_CYAN)
            surface.blit(t, (sw // 2 - t.get_width() // 2, py + 20))

        if self._font:
            for i, opt in enumerate(OPTIONS):
                col = settings.NEON_CYAN if i == self._selected else settings.COLOR_GRAY
                lbl = self._font.render(opt, True, col)
                surface.blit(lbl, (sw // 2 - lbl.get_width() // 2, py + 80 + i * 44))
