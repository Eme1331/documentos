"""Skill tree DAG UI."""
from __future__ import annotations
import pygame
import settings


class SkillTreeUI:
    NODE_R = 24
    SPACING = (110, 90)

    def __init__(self) -> None:
        self._skill_tree = None
        self._selected = 0
        try:
            self._font = pygame.font.SysFont("consolas", 12)
            self._font_title = pygame.font.SysFont("consolas", 22, bold=True)
        except Exception:
            self._font = self._font_title = None

    def set_tree(self, skill_tree) -> None:
        self._skill_tree = skill_tree

    def handle_event(self, event: pygame.event.Event, available_points: int) -> str | None:
        if not self._skill_tree:
            return None
        nodes = self._skill_tree.all_nodes
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "CLOSE"
            if event.key in (pygame.K_LEFT, pygame.K_a) and nodes:
                self._selected = (self._selected - 1) % len(nodes)
            if event.key in (pygame.K_RIGHT, pygame.K_d) and nodes:
                self._selected = (self._selected + 1) % len(nodes)
            if event.key == pygame.K_RETURN and nodes:
                node = nodes[self._selected]
                if self._skill_tree.can_unlock(node.id, available_points):
                    self._skill_tree.unlock(node.id)
                    return f"UNLOCKED:{node.id}"
        return None

    def draw(self, surface: pygame.Surface, available_points: int = 0) -> None:
        sw, sh = settings.SCREEN_SIZE
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 15, 220))
        surface.blit(overlay, (0, 0))

        if self._font_title:
            t = self._font_title.render("SKILL TREE", True, settings.NEON_CYAN)
            surface.blit(t, (sw // 2 - t.get_width() // 2, 20))
            pts = self._font_title.render(f"Points: {available_points}", True, settings.NEON_YELLOW)
            surface.blit(pts, (sw - pts.get_width() - 20, 20))

        if not self._skill_tree:
            return

        nodes = self._skill_tree.all_nodes
        ox, oy = 100, 100
        positions: dict[str, tuple] = {}

        for i, node in enumerate(nodes):
            col_i = i % 6
            row_i = i // 6
            x = ox + col_i * self.SPACING[0]
            y = oy + row_i * self.SPACING[1]
            positions[node.id] = (x, y)

        # Draw connections
        for node in nodes:
            nx, ny = positions.get(node.id, (0, 0))
            for req in node.requires:
                if req in positions:
                    rx, ry = positions[req]
                    col = (0, 180, 140) if node.unlocked else (60, 60, 100)
                    pygame.draw.line(surface, col, (rx, ry), (nx, ny), 2)

        # Draw nodes
        for i, node in enumerate(nodes):
            x, y = positions.get(node.id, (0, 0))
            if node.unlocked:
                col = settings.NEON_CYAN
            elif self._skill_tree.can_unlock(node.id, available_points):
                col = (0, 180, 120)
            else:
                col = (60, 60, 100)

            border = settings.NEON_YELLOW if i == self._selected else col
            pygame.draw.circle(surface, (10, 10, 30), (x, y), self.NODE_R)
            pygame.draw.circle(surface, col, (x, y), self.NODE_R - 4)
            pygame.draw.circle(surface, border, (x, y), self.NODE_R, 2)

            if self._font:
                name = node.id.replace("_", " ")[:8]
                lbl = self._font.render(name, True, (200, 200, 220))
                surface.blit(lbl, (x - lbl.get_width() // 2, y + self.NODE_R + 3))

        if self._font and nodes and 0 <= self._selected < len(nodes):
            sel = nodes[self._selected]
            desc = f"{sel.name} — Cost: {sel.cost}pt"
            dlbl = self._font.render(desc, True, settings.NEON_CYAN)
            surface.blit(dlbl, (sw // 2 - dlbl.get_width() // 2, sh - 50))
