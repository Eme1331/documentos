"""Attack data model."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Attack:
    name: str = ""
    damage: int = 10
    knockback: tuple = (200, -100)
    hitstun_frames: int = 8
    attack_type: str = "PHYSICAL"   # PHYSICAL | ENERGY | EXPLOSIVE
    hitbox_size: tuple = (40, 30)
    hitbox_offset: tuple = (20, 0)
    active_frames: range = field(default_factory=lambda: range(4, 8))
    can_pierce: bool = False
    status: str | None = None
    energy_cost: int = 0
    cooldown: float = 0.0
