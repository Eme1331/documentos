"""Character selection screen."""
from __future__ import annotations
import pygame
import settings

CHARACTERS = [
    {"id": "ethan",  "name": "ETHAN NOVA",  "class": "Soldier",   "color": (0, 180, 255),
     "stats": {"HP": 120, "Speed": 80, "Power": 70}},
    {"id": "cy_x7",  "name": "CY-X7",       "class": "Cyborg",    "color": (150, 80, 220),
     "stats": {"HP": 150, "Speed": 60, "Power": 90}},
    {"id": "zhyra",  "name": "ZHYRA",        "class": "Quantum",   "color": (220, 80, 255),
     "stats": {"HP": 90,  "Speed": 110, "Power": 80}},
]


class CharacterSelect:
    def __init__(self) -> None:
        self._sel = 0
        try:
            self._font_title = pygame.font.SysFont("consolas", 36, bold=True)
            self._font_name = pygame.font.SysFont("consolas", 22, bold=True)
            self._font_info = pygame.font.SysFont("consolas", 15)
        except Exception:
            self._font_title = self._font_name = self._font_info = None

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._sel = (self._sel - 1) % len(CHARACTERS)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._sel = (self._sel + 1) % len(CHARACTERS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                chosen = CHARACTERS[self._sel]["id"]
                print(f"[SELECT] Character chosen: {chosen}")
                return chosen
            elif event.key == pygame.K_ESCAPE:
                return "BACK"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        sw, sh = settings.SCREEN_SIZE
        surface.fill(settings.COLOR_BG_DARK)

        if self._font_title:
            t = self._font_title.render("SELECT YOUR HERO", True, settings.NEON_CYAN)
            surface.blit(t, (sw // 2 - t.get_width() // 2, 30))

        card_w, card_h = 260, 340
        spacing = 40
        total = len(CHARACTERS) * card_w + (len(CHARACTERS) - 1) * spacing
        start_x = sw // 2 - total // 2

        for i, char in enumerate(CHARACTERS):
            cx = start_x + i * (card_w + spacing)
            cy = sh // 2 - card_h // 2

            selected = i == self._sel
            border = char["color"] if selected else (60, 60, 100)
            thickness = 3 if selected else 1

            pygame.draw.rect(surface, (10, 10, 30), (cx, cy, card_w, card_h), border_radius=10)
            pygame.draw.rect(surface, border, (cx, cy, card_w, card_h), thickness, border_radius=10)

            # Character art placeholder
            art_rect = pygame.Rect(cx + 80, cy + 20, 100, 160)
            pygame.draw.rect(surface, char["color"], art_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 255, 255), art_rect, 1, border_radius=8)

            if self._font_name:
                name_lbl = self._font_name.render(char["name"], True, char["color"])
                surface.blit(name_lbl, (cx + card_w // 2 - name_lbl.get_width() // 2, cy + 195))
            if self._font_info:
                cls_lbl = self._font_info.render(char["class"], True, settings.COLOR_GRAY)
                surface.blit(cls_lbl, (cx + card_w // 2 - cls_lbl.get_width() // 2, cy + 222))

                y_stat = cy + 250
                stat_max = {"HP": 150, "Speed": 120, "Power": 100}
                for stat, val in char["stats"].items():
                    max_val = stat_max.get(stat, 150)
                    bar_w = int(min(val, max_val) / max_val * 160)
                    lbl = self._font_info.render(f"{stat}", True, settings.COLOR_GRAY)
                    surface.blit(lbl, (cx + 12, y_stat))
                    pygame.draw.rect(surface, (40, 40, 80), (cx + 80, y_stat + 2, 160, 10), border_radius=3)
                    pygame.draw.rect(surface, char["color"], (cx + 80, y_stat + 2, bar_w, 10), border_radius=3)
                    y_stat += 22

        if self._font_info:
            hint = self._font_info.render("← → to browse   ENTER to select", True, settings.COLOR_GRAY)
            surface.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 40))
