"""Tile map: loads TMX or generates a fallback test level."""
from __future__ import annotations
import pygame
import settings

_HAS_PYTMX = False
try:
    import pytmx
    _HAS_PYTMX = True
except ImportError:
    pass


class TileMap:
    def __init__(self, tmx_path: str | None = None,
                 ambient_color: tuple = (8, 8, 20)) -> None:
        self.tile_size = settings.TILE_SIZE
        self.width_tiles = 80
        self.height_tiles = 30
        self.collision_rects: list[pygame.Rect] = []
        self.one_way_rects: list[pygame.Rect] = []
        self.hazard_rects: list[pygame.Rect] = []
        self.LAYER_FOREGROUND = "Foreground"
        self._surfaces: dict[str, pygame.Surface] = {}
        self._ambient = ambient_color
        self._tmx_data = None

        loaded = False
        if tmx_path and _HAS_PYTMX:
            try:
                self._tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
                self._parse_tmx()
                loaded = True
            except Exception:
                pass

        if not loaded:
            self._generate_test_level()

    def _parse_tmx(self) -> None:
        td = self._tmx_data
        self.width_tiles = td.width
        self.height_tiles = td.height
        ts = td.tilewidth

        for layer in td.visible_layers:
            if not hasattr(layer, "data"):
                continue
            surf = pygame.Surface(
                (td.width * ts, td.height * ts), pygame.SRCALPHA)
            for x, y, image in layer.tiles():
                if image:
                    surf.blit(image, (x * ts, y * ts))
                if layer.name == settings.LAYER_COLLISION:
                    self.collision_rects.append(pygame.Rect(x*ts, y*ts, ts, ts))
            self._surfaces[layer.name] = surf

    def _generate_test_level(self) -> None:
        import random
        W, H = self.width_tiles, self.height_tiles
        ts = self.tile_size
        floor_y = H - 3
        pw, ph = W * ts, H * ts

        # --- Rich sci-fi background ---
        bg = pygame.Surface((pw, ph))
        for y in range(ph):
            t = y / ph
            r = int(5 + t * 3)
            g = int(5 + t * 2)
            b = int(20 + t * 12)
            pygame.draw.line(bg, (r, g, b), (0, y), (pw, y))

        # Nebulae
        rng = random.Random(7)
        nebula_data = [
            (int(pw * 0.15), int(ph * 0.3), 220, 80,  (30, 0, 60, 40)),
            (int(pw * 0.50), int(ph * 0.2), 300, 100, (0, 20, 60, 35)),
            (int(pw * 0.78), int(ph * 0.45), 180, 90, (40, 0, 80, 30)),
            (int(pw * 0.35), int(ph * 0.6), 250, 70,  (0, 30, 50, 25)),
        ]
        for nx, ny, nw, nh, nc in nebula_data:
            neb = pygame.Surface((nw, nh), pygame.SRCALPHA)
            pygame.draw.ellipse(neb, nc, (0, 0, nw, nh))
            bg.blit(neb, (nx - nw // 2, ny - nh // 2), special_flags=pygame.BLEND_RGBA_ADD)

        # Stars
        star_colors = [(200, 200, 255), (255, 255, 255), (180, 220, 255), (255, 200, 180)]
        for _ in range(350):
            sx = rng.randint(0, pw - 1)
            sy = rng.randint(0, ph - 1)
            alpha = rng.randint(120, 255)
            size = rng.choice([1, 1, 1, 2, 2, 3])
            col = rng.choice(star_colors)
            if size == 1:
                bg.set_at((sx, sy), col)
            else:
                s = pygame.Surface((size, size), pygame.SRCALPHA)
                s.fill((*col, alpha))
                bg.blit(s, (sx, sy))

        # Distant city silhouette at horizon
        city_y = floor_y * ts - 50
        bx = 0
        while bx < pw:
            bh = rng.randint(20, 70)
            bw2 = rng.randint(12, 28)
            pygame.draw.rect(bg, (12, 12, 30), (bx, city_y - bh, bw2, bh))
            for wy in range(city_y - bh + 5, city_y - 4, 8):
                for wx in range(bx + 3, bx + bw2 - 2, 5):
                    if rng.random() > 0.45:
                        wc = rng.choice([(0, 160, 255, 160), (255, 220, 80, 120)])
                        ws = pygame.Surface((3, 3), pygame.SRCALPHA)
                        ws.fill(wc)
                        bg.blit(ws, (wx, wy))
            bx += bw2 + rng.randint(2, 8)

        self._surfaces[settings.LAYER_BACKGROUND] = bg

        # --- Sci-fi metal tiles ---
        col_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)

        def draw_tile(tx, ty, top_glow=True):
            r = pygame.Rect(tx * ts, ty * ts, ts, ts)
            pygame.draw.rect(col_surf, (22, 22, 45), r)
            pygame.draw.rect(col_surf, (30, 30, 58), pygame.Rect(r.x, r.y, r.w, r.h // 2))
            pygame.draw.line(col_surf, (15, 15, 30), r.bottomleft, r.bottomright)
            pygame.draw.line(col_surf, (35, 35, 60), r.topleft, r.bottomleft)
            pygame.draw.line(col_surf, (15, 15, 30), r.topright, r.bottomright)
            if top_glow:
                pygame.draw.line(col_surf, (60, 100, 255), r.topleft, r.topright, 2)
                glow = pygame.Surface((r.w, 4), pygame.SRCALPHA)
                glow.fill((60, 100, 255, 50))
                col_surf.blit(glow, (r.x, r.y + 2))
            pygame.draw.circle(col_surf, (50, 50, 80), (r.x + 4, r.y + 4), 2)
            pygame.draw.circle(col_surf, (50, 50, 80), (r.right - 4, r.y + 4), 2)

        def place_tile(tx, ty, top_glow=True):
            draw_tile(tx, ty, top_glow)
            self.collision_rects.append(pygame.Rect(tx * ts, ty * ts, ts, ts))

        for x in range(W):
            place_tile(x, floor_y, top_glow=True)
            place_tile(x, floor_y + 1, top_glow=False)
            place_tile(x, floor_y + 2, top_glow=False)

        for y in range(H):
            place_tile(0, y, top_glow=False)
            place_tile(W - 1, y, top_glow=False)

        platforms = [
            (5,  floor_y - 5,  6),
            (14, floor_y - 8,  5),
            (22, floor_y - 5,  7),
            (31, floor_y - 10, 4),
            (38, floor_y - 6,  6),
            (47, floor_y - 4,  5),
            (55, floor_y - 8,  6),
            (64, floor_y - 5,  5),
        ]
        for px, py, pw2 in platforms:
            for x in range(px, px + pw2):
                place_tile(x, py)
            # Neon glow strip under platform
            strip = pygame.Surface((pw2 * ts, 3), pygame.SRCALPHA)
            strip.fill((0, 180, 255, 70))
            col_surf.blit(strip, (px * ts, py * ts + ts))

        # Midground: structural pillars + panels
        mid = pygame.Surface((pw, ph), pygame.SRCALPHA)
        for px2, py2, pw3 in [(8, floor_y - 14, 3), (30, floor_y - 18, 2), (52, floor_y - 12, 3)]:
            for iy in range(py2, floor_y - 2):
                r2 = pygame.Rect(px2 * ts + ts // 3, iy * ts, ts // 3, ts)
                pygame.draw.rect(mid, (25, 25, 50, 200), r2)
                pygame.draw.rect(mid, (50, 50, 100, 100), r2, 1)

        panel_positions = [(10, 8), (25, 5), (42, 7), (60, 10), (70, 6)]
        for ppx, ppy in panel_positions:
            panel = pygame.Surface((ts * 2, ts // 2), pygame.SRCALPHA)
            panel.fill((0, 40, 80, 100))
            pygame.draw.rect(panel, (0, 150, 255, 160), (0, 0, ts * 2, ts // 2), 1)
            mid.blit(panel, (ppx * ts, ppy * ts))

        self._surfaces[settings.LAYER_COLLISION] = col_surf
        self._surfaces[settings.LAYER_MIDGROUND] = mid

    @property
    def pixel_width(self) -> int:
        return self.width_tiles * self.tile_size

    @property
    def pixel_height(self) -> int:
        return self.height_tiles * self.tile_size

    def render_layer(self, surface: pygame.Surface, layer_name: str, camera) -> None:
        surf = self._surfaces.get(layer_name)
        if not surf:
            return
        offset = camera.offset if camera else pygame.math.Vector2(0, 0)
        surface.blit(surf, (-offset.x, -offset.y))
