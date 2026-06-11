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

    # --- TMX loading ---
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

    # --- Procedural test level ---
    def _generate_test_level(self) -> None:
        W, H = self.width_tiles, self.height_tiles
        ts = self.tile_size
        floor_y = H - 3

        # Background
        bg = pygame.Surface((W * ts, H * ts))
        bg.fill(self._ambient)
        # Stars
        import random, math
        rng = random.Random(42)
        for _ in range(200):
            sx = rng.randint(0, W * ts)
            sy = rng.randint(0, H * ts)
            alpha = rng.randint(80, 255)
            s = pygame.Surface((2, 2), pygame.SRCALPHA)
            s.fill((200, 200, 255, alpha))
            bg.blit(s, (sx, sy))
        self._surfaces[settings.LAYER_BACKGROUND] = bg

        # Collision tiles
        col = pygame.Surface((W * ts, H * ts), pygame.SRCALPHA)
        tile_col = (50, 50, 80)

        def place_tile(tx, ty):
            r = pygame.Rect(tx * ts, ty * ts, ts, ts)
            pygame.draw.rect(col, tile_col, r)
            pygame.draw.rect(col, (80, 80, 120), r, 1)
            self.collision_rects.append(r)

        # Floor
        for x in range(W):
            place_tile(x, floor_y)
            place_tile(x, floor_y + 1)
            place_tile(x, floor_y + 2)

        # Left/right walls
        for y in range(H):
            place_tile(0, y)
            place_tile(W - 1, y)

        # Platforms
        platforms = [
            (5, floor_y - 5, 6), (14, floor_y - 8, 5),
            (22, floor_y - 5, 7), (31, floor_y - 10, 4),
            (38, floor_y - 6, 6), (47, floor_y - 4, 5),
            (55, floor_y - 8, 6), (64, floor_y - 5, 5),
        ]
        for px, py, pw in platforms:
            for x in range(px, px + pw):
                place_tile(x, py)

        self._surfaces[settings.LAYER_COLLISION] = col
        self._surfaces[settings.LAYER_MIDGROUND] = pygame.Surface(
            (W * ts, H * ts), pygame.SRCALPHA)

    # --- Public accessors ---
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
