"""Weapon upgrade tiers."""
from __future__ import annotations

UPGRADE_COSTS = [0, 3, 6, 10, 15]  # material cost for tier 1-5

class WeaponUpgrade:
    def __init__(self) -> None:
        self._tiers: dict[str, int] = {}
        self._materials: int = 0

    def add_materials(self, amount: int) -> None:
        self._materials += amount

    def upgrade(self, weapon_id: str) -> bool:
        tier = self._tiers.get(weapon_id, 0)
        if tier >= 5:
            return False
        cost = UPGRADE_COSTS[tier]
        if self._materials < cost:
            return False
        self._materials -= cost
        self._tiers[weapon_id] = tier + 1
        return True

    def get_tier(self, weapon_id: str) -> int:
        return self._tiers.get(weapon_id, 0)

    def damage_multiplier(self, weapon_id: str) -> float:
        tier = self.get_tier(weapon_id)
        return 1.0 + tier * 0.15

    def to_dict(self) -> dict:
        return {"tiers": self._tiers, "materials": self._materials}

    def from_dict(self, data: dict) -> None:
        self._tiers = data.get("tiers", {})
        self._materials = data.get("materials", 0)
