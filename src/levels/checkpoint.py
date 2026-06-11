"""Checkpoint entity."""
from __future__ import annotations
import pygame
from src.entities.entity import Entity


class Checkpoint(Entity):
    def __init__(self, checkpoint_id: str, x: float, y: float,
                 event_bus=None) -> None:
        super().__init__()
        self.checkpoint_id = checkpoint_id
        self.rect = pygame.Rect(int(x), int(y), 32, 64)
        self.activated = False
        self._event_bus = event_bus
        self._surf = pygame.Surface((32, 64), pygame.SRCALPHA)
        pygame.draw.rect(self._surf, (0, 200, 150, 180), (0, 0, 32, 64), 3)
        self.layer = "default"

    def update(self, dt: float) -> None:
        pass

    def check_player(self, player_rect: pygame.Rect) -> bool:
        if not self.activated and self.rect.colliderect(player_rect):
            self.activated = True
            if self._event_bus:
                from src.core.event_bus import CheckpointReachedEvent
                self._event_bus.emit(CheckpointReachedEvent(
                    checkpoint_id=self.checkpoint_id,
                    position=(self.rect.centerx, self.rect.centery)))
            return True
        return False

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        pos = self.rect.topleft
        if camera:
            pos = camera.apply_point(pos)
        col = (0, 255, 200) if self.activated else (0, 150, 100)
        pygame.draw.rect(surface, col, (*pos, 32, 64), 2)
