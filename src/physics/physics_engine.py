"""Gravity and velocity integration."""
from __future__ import annotations
import settings


class PhysicsEngine:
    GRAVITY = settings.GRAVITY
    TERMINAL_VELOCITY = settings.TERMINAL_VELOCITY

    def __init__(self) -> None:
        self.time_scale: float = 1.0

    def apply(self, transform, grounded: bool, dt: float) -> None:
        effective_dt = dt * self.time_scale
        if not grounded:
            transform.velocity.y += self.GRAVITY * effective_dt
            if transform.velocity.y > self.TERMINAL_VELOCITY:
                transform.velocity.y = self.TERMINAL_VELOCITY

        transform.position += transform.velocity * effective_dt
