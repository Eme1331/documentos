"""Damage formula."""
from __future__ import annotations
import random

RESISTANCES: dict[str, dict[str, float]] = {
    "grunt":        {"PHYSICAL": 0.0,  "ENERGY": 0.1,  "EXPLOSIVE": 0.0},
    "heavy":        {"PHYSICAL": 0.3,  "ENERGY": 0.0,  "EXPLOSIVE": 0.1},
    "flying_drone": {"PHYSICAL": 0.0,  "ENERGY": 0.2,  "EXPLOSIVE": 0.1},
    "boss":         {"PHYSICAL": 0.1,  "ENERGY": 0.1,  "EXPLOSIVE": 0.1},
}


def calculate(base: int, attack_type: str = "PHYSICAL",
              atk_modifier: float = 1.0,
              combo_multiplier: float = 1.0,
              enemy_type: str = "grunt",
              is_crit: bool = False) -> int:
    resistance = RESISTANCES.get(enemy_type, {}).get(attack_type, 0.0)
    crit = 1.5 if is_crit else 1.0
    variance = random.uniform(0.9, 1.1)
    result = base * atk_modifier * (1 - resistance) * combo_multiplier * variance * crit
    return max(1, int(result))
