"""Dialogue box with typewriter effect."""
from __future__ import annotations
import pygame


class DialogueBox:
    CHARS_PER_SEC = 40
    BOX_H = 100

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self._sw, self._sh = screen_w, screen_h
        self._text = ""
        self._speaker = ""
        self._displayed = 0.0
        self._done = False
        self.visible = False

    def show(self, text: str, speaker: str = "") -> None:
        self._text = text
        self._speaker = speaker
        self._displayed = 0.0
        self._done = False
        self.visible = True

    def advance(self) -> bool:
        if not self._done:
            self._displayed = len(self._text)
            self._done = True
            return False
        self.visible = False
        return True  # dialogue complete

    def update(self, dt: float) -> None:
        if not self.visible or self._done:
            return
        self._displayed = min(len(self._text),
                               self._displayed + self.CHARS_PER_SEC * dt)
        if self._displayed >= len(self._text):
            self._done = True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        y = self._sh - self.BOX_H - 10
        box = pygame.Rect(20, y, self._sw - 40, self.BOX_H)
        bg = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
        bg.fill((0, 10, 30, 210))
        surface.blit(bg, box.topleft)
        pygame.draw.rect(surface, (0, 180, 200), box, 2)

        try:
            font = pygame.font.SysFont("consolas", 15)
            if self._speaker:
                spk = font.render(self._speaker, True, (0, 220, 200))
                surface.blit(spk, (box.x + 10, box.y + 8))
            text_y = box.y + (28 if self._speaker else 12)
            shown = self._text[:int(self._displayed)]
            wrapped = self._wrap(shown, font, box.width - 20)
            for line in wrapped:
                lbl = font.render(line, True, (220, 220, 230))
                surface.blit(lbl, (box.x + 10, text_y))
                text_y += 20
            if self._done:
                arrow = font.render("▼", True, (0, 220, 200))
                surface.blit(arrow, (box.right - 24, box.bottom - 22))
        except Exception:
            pass

    def _wrap(self, text: str, font, max_w: int) -> list[str]:
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= max_w:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
