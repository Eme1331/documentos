"""Settings menu."""
from __future__ import annotations
import pygame
import settings

OPTIONS = ["Music Volume", "SFX Volume", "Fullscreen", "Back"]


class SettingsMenu:
    def __init__(self, config: dict) -> None:
        self._sel = 0
        self._music_vol = float(config.get("volume", {}).get("music", 0.7))
        self._sfx_vol = float(config.get("volume", {}).get("sfx", 0.8))
        self._fullscreen = False
        try:
            self._font = pygame.font.SysFont("consolas", 20)
            self._font_title = pygame.font.SysFont("consolas", 30, bold=True)
        except Exception:
            self._font = self._font_title = None

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._sel = (self._sel - 1) % len(OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._sel = (self._sel + 1) % len(OPTIONS)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._adjust(-0.1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._adjust(0.1)
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                if OPTIONS[self._sel] == "Back" or event.key == pygame.K_ESCAPE:
                    return "BACK"
        return None

    def _adjust(self, delta: float) -> None:
        if self._sel == 0:
            self._music_vol = max(0.0, min(1.0, self._music_vol + delta))
        elif self._sel == 1:
            self._sfx_vol = max(0.0, min(1.0, self._sfx_vol + delta))
        elif self._sel == 2:
            self._fullscreen = not self._fullscreen

    def draw(self, surface: pygame.Surface) -> None:
        sw, sh = settings.SCREEN_SIZE
        surface.fill(settings.COLOR_BG)

        if self._font_title:
            t = self._font_title.render("SETTINGS", True, settings.NEON_CYAN)
            surface.blit(t, (sw // 2 - t.get_width() // 2, 60))

        if self._font:
            values = [f"{int(self._music_vol * 100)}%",
                      f"{int(self._sfx_vol * 100)}%",
                      "ON" if self._fullscreen else "OFF",
                      ""]
            for i, (opt, val) in enumerate(zip(OPTIONS, values)):
                col = settings.NEON_CYAN if i == self._sel else settings.COLOR_GRAY
                y = 160 + i * 50
                lbl = self._font.render(opt, True, col)
                surface.blit(lbl, (sw // 2 - 200, y))
                if val:
                    vlbl = self._font.render(val, True, settings.NEON_YELLOW)
                    surface.blit(vlbl, (sw // 2 + 100, y))
                    bar_x = sw // 2 - 60
                    bar_w = 140
                    if i in (0, 1):
                        frac = self._music_vol if i == 0 else self._sfx_vol
                        pygame.draw.rect(surface, (40, 40, 80), (bar_x, y + 6, bar_w, 10), border_radius=3)
                        pygame.draw.rect(surface, col, (bar_x, y + 6, int(bar_w * frac), 10), border_radius=3)
