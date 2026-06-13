"""Level transition door — sci-fi portal gate."""
from __future__ import annotations
import pygame
import math
from src.entities.entity import Entity


class LevelDoor(Entity):
    W = 56
    H = 88

    def __init__(self, x: float, y: float, next_level_id: str,
                 event_bus=None) -> None:
        super().__init__()
        self.layer = "default"
        self.next_level_id = next_level_id
        self.rect = pygame.Rect(int(x), int(y), self.W, self.H)
        self._event_bus = event_bus
        self._activated = False
        self._anim_time = 0.0
        self._player_inside = False

    def update(self, dt: float) -> None:
        self._anim_time += dt

    def check_player(self, player_rect: pygame.Rect) -> bool:
        """Returns True the frame the player enters the door."""
        inside = self.rect.colliderect(player_rect)
        triggered = inside and not self._player_inside and not self._activated
        self._player_inside = inside
        if triggered:
            self._activated = True
        return triggered

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        t = self._anim_time
        pos = self.rect.topleft
        if camera:
            pos = camera.apply_point(pos)
        x, y = pos
        W, H = self.W, self.H

        pulse = 0.5 + 0.5 * math.sin(t * 3.0)
        fast_pulse = 0.5 + 0.5 * math.sin(t * 8.0)

        # --- Frame / arch structure ---
        frame_col = (30, 30, 60)
        edge_col  = (60, 100, 255)
        pygame.draw.rect(surface, frame_col, (x, y, W, H), border_radius=4)

        # Outer frame border (thick neon)
        pygame.draw.rect(surface, edge_col, (x, y, W, H), 3, border_radius=4)

        # Inner glow border
        glow_alpha = int(80 + 100 * pulse)
        glow_surf = pygame.Surface((W - 8, H - 8), pygame.SRCALPHA)
        glow_surf.fill((80, 140, 255, glow_alpha))
        surface.blit(glow_surf, (x + 4, y + 4))

        # --- Portal interior (animated swirl) ---
        inner_w, inner_h = W - 14, H - 20
        inner_x, inner_y = x + 7, y + 10
        portal_surf = pygame.Surface((inner_w, inner_h), pygame.SRCALPHA)

        # Deep background
        portal_surf.fill((5, 5, 30, 220))

        # Animated horizontal energy lines
        for i in range(8):
            ly = int(inner_h * (i + 0.5) / 8 + math.sin(t * 2.0 + i * 0.8) * 3)
            ly = max(0, min(inner_h - 1, ly))
            alpha = int(120 + 80 * math.sin(t * 3.0 + i))
            line_col = (
                int(40 + 100 * abs(math.sin(t + i * 0.5))),
                int(80 + 100 * abs(math.sin(t * 1.3 + i))),
                255,
                max(0, min(255, alpha)),
            )
            line_surf = pygame.Surface((inner_w, 2), pygame.SRCALPHA)
            line_surf.fill(line_col)
            portal_surf.blit(line_surf, (0, ly))

        # Central orb
        cx, cy = inner_w // 2, inner_h // 2
        orb_r = int(10 + 4 * pulse)
        # Outer glow
        for r in range(orb_r + 8, orb_r - 1, -2):
            a = int(40 * (1 - (r - orb_r) / 9))
            pygame.draw.circle(portal_surf, (100, 180, 255, a), (cx, cy), r)
        # Core
        pygame.draw.circle(portal_surf, (180, 220, 255), (cx, cy), orb_r)
        pygame.draw.circle(portal_surf, (255, 255, 255), (cx, cy), max(1, orb_r - 4))

        # Orbiting particles
        for i in range(3):
            angle = t * 2.5 + i * (2 * math.pi / 3)
            orbit_r = 16 + 4 * pulse
            px2 = cx + int(orbit_r * math.cos(angle))
            py2 = cy + int(orbit_r * math.sin(angle) * 0.5)
            pygame.draw.circle(portal_surf, (0, 200, 255), (px2, py2), 3)

        surface.blit(portal_surf, (inner_x, inner_y))

        # --- Frame details: corner brackets ---
        bracket = 10
        for bx, by, dx, dy in [
            (x, y, 1, 1), (x + W, y, -1, 1),
            (x, y + H, 1, -1), (x + W, y + H, -1, -1)
        ]:
            pygame.draw.line(surface, (200, 220, 255),
                             (bx, by), (bx + dx * bracket, by), 2)
            pygame.draw.line(surface, (200, 220, 255),
                             (bx, by), (bx, by + dy * bracket), 2)

        # --- Top panel: "EXIT" label with blinking arrow ---
        try:
            font = pygame.font.SysFont("consolas", 10, bold=True)
            label = font.render("EXIT", True, (0, 220, 255))
            surface.blit(label, (x + W // 2 - label.get_width() // 2, y - 14))
        except Exception:
            pass

        # Blinking down-arrow above door
        arrow_alpha = int(200 * fast_pulse)
        arrow_col = (0, 200, 255, arrow_alpha)
        arr = pygame.Surface((10, 6), pygame.SRCALPHA)
        pygame.draw.polygon(arr, arrow_col, [(5, 6), (0, 0), (10, 0)])
        surface.blit(arr, (x + W // 2 - 5, y - 22))

        # --- Side neon strips ---
        strip_alpha = int(100 + 100 * pulse)
        for sx2 in [x, x + W - 3]:
            strip = pygame.Surface((3, H - 10), pygame.SRCALPHA)
            strip.fill((60, 120, 255, strip_alpha))
            surface.blit(strip, (sx2, y + 5))

        # --- Floor light beam ---
        beam = pygame.Surface((W, 8), pygame.SRCALPHA)
        beam.fill((60, 120, 255, int(60 * pulse)))
        surface.blit(beam, (x, y + H - 4))
