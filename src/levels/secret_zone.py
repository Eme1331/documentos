"""Hidden passage trigger volume."""
from __future__ import annotations
import pygame
from src.entities.entity import Entity


class SecretZone(Entity):
    REVEAL_DISTANCE = 80.0

    def __init__(self, secret_id: str, rect: pygame.Rect,
                 reward: str = "") -> None:
        super().__init__()
        self.secret_id = secret_id
        self.rect = rect
        self.reward = reward
        self.revealed = False
        self.triggered = False

    def update_visibility(self, player_pos: tuple) -> None:
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = (dx*dx + dy*dy) ** 0.5
        self.revealed = dist < self.REVEAL_DISTANCE

    def check_trigger(self, player_rect: pygame.Rect) -> bool:
        if not self.triggered and self.rect.colliderect(player_rect):
            self.triggered = True
            return True
        return False

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        if self.revealed:
            pos = self.rect.topleft
            if camera:
                pos = camera.apply_point(pos)
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            s.fill((255, 200, 0, 60))
            surface.blit(s, pos)
