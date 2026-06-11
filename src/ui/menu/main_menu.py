"""Main menu UI."""
from __future__ import annotations
import pygame
import settings

OPTIONS = ["NEW GAME", "LOAD GAME", "SETTINGS", "QUIT"]


class MainMenu:
    def __init__(self) -> None:
        self._selected = 0
        self._font_title = None
        self._font_item = None
        self._init_fonts()

    def _init_fonts(self):
        try:
            self._font_title = pygame.font.SysFont("consolas", 48, bold=True)
            self._font_item = pygame.font.SysFont("consolas", 24)
        except Exception:
            pass

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._selected = (self._selected - 1) % len(OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected + 1) % len(OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                return OPTIONS[self._selected]
        return None

    def draw(self, surface: pygame.Surface) -> None:
        sw, sh = settings.SCREEN_SIZE
        surface.fill(settings.COLOR_BG)

        if self._font_title:
            title = self._font_title.render("GALAXY REBORN", True, settings.NEON_CYAN)
            sub = pygame.font.SysFont("consolas", 18).render(
                "THE LAST FRONTIER", True, settings.NEON_PURPLE)
            surface.blit(title, (sw // 2 - title.get_width() // 2, sh // 4))
            surface.blit(sub, (sw // 2 - sub.get_width() // 2, sh // 4 + 60))

        if self._font_item:
            for i, opt in enumerate(OPTIONS):
                color = settings.NEON_CYAN if i == self._selected else settings.COLOR_GRAY
                lbl = self._font_item.render(opt, True, color)
                y = sh // 2 + i * 44
                surface.blit(lbl, (sw // 2 - lbl.get_width() // 2, y))
                if i == self._selected:
                    pygame.draw.rect(surface, settings.NEON_CYAN,
                                     (sw // 2 - 140, y - 2, 280, 36), 1, border_radius=4)
