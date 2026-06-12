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

    def _card_rect(self, i: int) -> pygame.Rect:
        sw, sh = settings.SCREEN_SIZE
        card_w, card_h = 260, 340
        spacing = 40
        total = len(CHARACTERS) * card_w + (len(CHARACTERS) - 1) * spacing
        start_x = sw // 2 - total // 2
        cx = start_x + i * (card_w + spacing)
        cy = sh // 2 - card_h // 2
        return pygame.Rect(cx, cy, card_w, card_h)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._sel = (self._sel - 1) % len(CHARACTERS)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._sel = (self._sel + 1) % len(CHARACTERS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                return CHARACTERS[self._sel]["id"]
            elif event.key == pygame.K_ESCAPE:
                return "BACK"
        elif event.type == pygame.MOUSEMOTION:
            for i in range(len(CHARACTERS)):
                if self._card_rect(i).collidepoint(event.pos):
                    self._sel = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(CHARACTERS)):
                if self._card_rect(i).collidepoint(event.pos):
                    return CHARACTERS[i]["id"]
        return None

    def _draw_character_art(self, surface: pygame.Surface, char_id: str,
                            color: tuple, cx: int, cy: int) -> None:
        """Draw a detailed character portrait using pygame shapes."""
        if char_id == "ethan":
            self._draw_ethan(surface, color, cx, cy)
        elif char_id == "cy_x7":
            self._draw_cyx7(surface, color, cx, cy)
        else:
            self._draw_zhyra(surface, color, cx, cy)

    def _draw_ethan(self, s, c, cx, cy):
        dark = (0, 60, 120)
        # Legs
        pygame.draw.rect(s, (0, 80, 140), (cx+85, cy+125, 18, 35))
        pygame.draw.rect(s, (0, 80, 140), (cx+157, cy+125, 18, 35))
        pygame.draw.rect(s, dark, (cx+83, cy+152, 22, 10))
        pygame.draw.rect(s, dark, (cx+155, cy+152, 22, 10))
        # Body
        pygame.draw.rect(s, c, (cx+78, cy+60, 104, 72), border_radius=5)
        pygame.draw.rect(s, (0, 100, 200), (cx+82, cy+66, 96, 14), border_radius=3)
        pygame.draw.line(s, (100, 220, 255), (cx+130, cy+66), (cx+130, cy+128), 2)
        # Shoulders
        pygame.draw.rect(s, dark, (cx+68, cy+60, 14, 24), border_radius=3)
        pygame.draw.rect(s, dark, (cx+178, cy+60, 14, 24), border_radius=3)
        # Rifle
        pygame.draw.rect(s, (20, 20, 50), (cx+188, cy+72, 24, 10), border_radius=2)
        pygame.draw.rect(s, (0, 180, 255), (cx+208, cy+74, 10, 5))
        # Head/helmet
        pygame.draw.rect(s, dark, (cx+90, cy+6, 80, 58), border_radius=6)
        pygame.draw.rect(s, (0, 40, 100), (cx+90, cy+6, 80, 10))
        # Visor
        pygame.draw.rect(s, (0, 220, 255), (cx+96, cy+20, 68, 18), border_radius=3)
        pygame.draw.line(s, (200, 255, 255), (cx+100, cy+24), (cx+158, cy+24), 2)
        # Energy core
        pygame.draw.circle(s, (0, 255, 255), (cx+130, cy+100), 8)
        pygame.draw.circle(s, (255, 255, 255), (cx+130, cy+100), 4)

    def _draw_cyx7(self, s, c, cx, cy):
        dark = (50, 20, 90)
        metal = (80, 80, 110)
        # Heavy legs
        pygame.draw.rect(s, dark, (cx+82, cy+122, 20, 38))
        pygame.draw.rect(s, dark, (cx+158, cy+122, 20, 38))
        pygame.draw.rect(s, metal, (cx+80, cy+150, 24, 12))
        pygame.draw.rect(s, metal, (cx+156, cy+150, 24, 12))
        # Body
        pygame.draw.rect(s, c, (cx+76, cy+58, 108, 72), border_radius=3)
        pygame.draw.rect(s, dark, (cx+76, cy+58, 108, 10))
        pygame.draw.rect(s, (180, 100, 255), (cx+80, cy+72, 100, 10), border_radius=2)
        pygame.draw.line(s, (200, 150, 255), (cx+82, cy+90), (cx+178, cy+90), 1)
        pygame.draw.line(s, (200, 150, 255), (cx+130, cy+90), (cx+130, cy+126), 1)
        # Big shoulders
        pygame.draw.rect(s, dark, (cx+62, cy+56, 18, 28), border_radius=3)
        pygame.draw.rect(s, dark, (cx+180, cy+56, 18, 28), border_radius=3)
        pygame.draw.line(s, (200, 150, 255), (cx+62, cy+68), (cx+80, cy+68), 1)
        # Mechanical cannon arm
        pygame.draw.rect(s, metal, (cx+192, cy+70, 26, 14), border_radius=3)
        pygame.draw.circle(s, (255, 80, 80), (cx+216, cy+77), 6)
        pygame.draw.circle(s, (255, 180, 180), (cx+216, cy+77), 3)
        # Blocky head
        pygame.draw.rect(s, dark, (cx+88, cy+4, 84, 58), border_radius=3)
        pygame.draw.rect(s, (30, 10, 60), (cx+88, cy+4, 84, 10))
        # Red visor
        pygame.draw.rect(s, (160, 0, 0), (cx+94, cy+18, 72, 14), border_radius=2)
        pygame.draw.line(s, (255, 80, 80), (cx+98, cy+24), (cx+162, cy+24), 3)
        pygame.draw.circle(s, (255, 0, 0), (cx+130, cy+25), 5)
        # Power core
        pygame.draw.circle(s, (180, 80, 255), (cx+130, cy+98), 10)
        pygame.draw.circle(s, (255, 200, 255), (cx+130, cy+98), 5)
        pygame.draw.circle(s, (180, 80, 255), (cx+130, cy+98), 10, 2)

    def _draw_zhyra(self, s, c, cx, cy):
        dark = (80, 20, 110)
        # Aura
        aura = pygame.Surface((120, 180), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (180, 50, 255, 25), (0, 0, 120, 180))
        s.blit(aura, (cx + 70, cy + 0))
        # Slender legs
        pygame.draw.rect(s, dark, (cx+94, cy+128, 14, 32))
        pygame.draw.rect(s, dark, (cx+152, cy+128, 14, 32))
        pygame.draw.ellipse(s, c, (cx+90, cy+152, 18, 10))
        pygame.draw.ellipse(s, c, (cx+150, cy+152, 18, 10))
        # Body
        pygame.draw.rect(s, c, (cx+82, cy+60, 96, 74), border_radius=6)
        pygame.draw.line(s, (255, 180, 255), (cx+130, cy+64), (cx+130, cy+130), 1)
        pygame.draw.line(s, (255, 180, 255), (cx+86, cy+98), (cx+174, cy+98), 1)
        # Alien head
        pygame.draw.ellipse(s, dark, (cx+90, cy+6, 80, 58))
        # Floating hair/antenna
        pygame.draw.line(s, c, (cx+130, cy+6), (cx+118, cy+0), 2)
        pygame.draw.line(s, c, (cx+130, cy+6), (cx+142, cy+0), 2)
        pygame.draw.circle(s, (255, 200, 255), (cx+116, cy+0), 4)
        pygame.draw.circle(s, (255, 200, 255), (cx+144, cy+0), 4)
        # Glowing eyes
        pygame.draw.ellipse(s, (255, 100, 255), (cx+100, cy+22, 16, 10))
        pygame.draw.ellipse(s, (255, 100, 255), (cx+144, cy+22, 16, 10))
        pygame.draw.circle(s, (255, 255, 255), (cx+108, cy+27), 4)
        pygame.draw.circle(s, (255, 255, 255), (cx+152, cy+27), 4)
        # Quantum orb
        pygame.draw.circle(s, (255, 120, 255), (cx+130, cy+98), 12)
        pygame.draw.circle(s, (255, 255, 255), (cx+130, cy+98), 5)
        pygame.draw.circle(s, (220, 80, 255), (cx+130, cy+98), 12, 2)

    def draw(self, surface: pygame.Surface) -> None:
        sw, sh = settings.SCREEN_SIZE

        # Animated starfield background
        surface.fill((5, 5, 18))
        import math, time as _time
        t = _time.time()
        rng_bg = __import__("random").Random(99)
        for _ in range(80):
            sx = rng_bg.randint(0, sw)
            sy = rng_bg.randint(0, sh)
            twinkle = int(120 + 80 * math.sin(t * rng_bg.uniform(0.5, 2.0) + sx))
            twinkle = max(60, min(255, twinkle))
            pygame.draw.circle(surface, (twinkle, twinkle, 255), (sx, sy), 1)

        if self._font_title:
            t_surf = self._font_title.render("SELECT YOUR HERO", True, settings.NEON_CYAN)
            # Subtle glow behind title
            glow = pygame.Surface((t_surf.get_width() + 20, t_surf.get_height() + 10), pygame.SRCALPHA)
            glow.fill((0, 200, 255, 20))
            surface.blit(glow, (sw // 2 - glow.get_width() // 2, 25))
            surface.blit(t_surf, (sw // 2 - t_surf.get_width() // 2, 30))

        card_w, card_h = 260, 340
        spacing = 40
        total = len(CHARACTERS) * card_w + (len(CHARACTERS) - 1) * spacing
        start_x = sw // 2 - total // 2

        for i, char in enumerate(CHARACTERS):
            cx = start_x + i * (card_w + spacing)
            cy = sh // 2 - card_h // 2
            selected = i == self._sel
            col = char["color"]

            # Card shadow
            shadow = pygame.Surface((card_w + 8, card_h + 8), pygame.SRCALPHA)
            shadow.fill((*col, 30))
            surface.blit(shadow, (cx - 4, cy - 4))

            # Card background gradient
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            for row in range(card_h):
                alpha = int(200 + 40 * row / card_h)
                rr = min(15 + col[0] // 12, 30)
                gg = min(10 + col[1] // 12, 20)
                bb = min(30 + col[2] // 12, 60)
                pygame.draw.line(card_surf, (rr, gg, bb, alpha), (0, row), (card_w, row))
            surface.blit(card_surf, (cx, cy))

            # Neon border — pulsing when selected
            import math, time as _time2
            if selected:
                pulse = int(180 + 75 * math.sin(_time2.time() * 4))
                border_col = (
                    min(255, int(col[0] * pulse / 255)),
                    min(255, int(col[1] * pulse / 255)),
                    min(255, int(col[2] * pulse / 255))
                )
                pygame.draw.rect(surface, border_col, (cx, cy, card_w, card_h), 3, border_radius=10)
                # Inner glow line
                pygame.draw.rect(surface, (*border_col, 60),
                                 (cx+2, cy+2, card_w-4, card_h-4), 1, border_radius=9)
            else:
                pygame.draw.rect(surface, (60, 60, 100), (cx, cy, card_w, card_h), 1, border_radius=10)

            # Character art (180×180 area)
            self._draw_character_art(surface, char["id"], col, cx + 30, cy - 10)

            # Divider line
            pygame.draw.line(surface, (*col, 120), (cx + 10, cy + 185), (cx + card_w - 10, cy + 185), 1)

            if self._font_name:
                name_lbl = self._font_name.render(char["name"], True, col)
                surface.blit(name_lbl, (cx + card_w // 2 - name_lbl.get_width() // 2, cy + 192))
            if self._font_info:
                cls_lbl = self._font_info.render(char["class"], True, settings.COLOR_GRAY)
                surface.blit(cls_lbl, (cx + card_w // 2 - cls_lbl.get_width() // 2, cy + 218))

                y_stat = cy + 248
                stat_max = {"HP": 150, "Speed": 120, "Power": 100}
                stat_colors = {"HP": (255, 80, 80), "Speed": (80, 200, 255), "Power": (255, 160, 0)}
                for stat, val in char["stats"].items():
                    max_val = stat_max.get(stat, 150)
                    bar_fill = int(min(val, max_val) / max_val * 155)
                    bar_col = stat_colors.get(stat, col)
                    lbl = self._font_info.render(stat, True, settings.COLOR_GRAY)
                    surface.blit(lbl, (cx + 12, y_stat))
                    # Bar bg
                    pygame.draw.rect(surface, (30, 30, 55), (cx + 78, y_stat + 2, 160, 9), border_radius=3)
                    # Bar fill
                    if bar_fill > 0:
                        pygame.draw.rect(surface, bar_col, (cx + 78, y_stat + 2, bar_fill, 9), border_radius=3)
                        # Shine
                        pygame.draw.line(surface, (255, 255, 255),
                                         (cx + 78, y_stat + 3), (cx + 78 + bar_fill - 1, y_stat + 3), 1)
                    y_stat += 22

        if self._font_info:
            hint = self._font_info.render("← → browse   ENTER / Click to select   ESC back",
                                          True, settings.COLOR_GRAY)
            surface.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 38))
