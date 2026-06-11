"""Inventory and equip slots."""
from __future__ import annotations
import settings


class Inventory:
    EQUIP_SLOTS = ("weapon", "armor", "chip1", "chip2", "chip3")

    def __init__(self) -> None:
        self._items: list[dict] = []
        self._equipped: dict[str, dict | None] = {s: None for s in self.EQUIP_SLOTS}

    def add(self, item: dict) -> bool:
        if len(self._items) >= settings.MAX_INVENTORY_SLOTS:
            return False
        self._items.append(item)
        return True

    def remove(self, item_id: str) -> bool:
        for i, item in enumerate(self._items):
            if item.get("id") == item_id:
                self._items.pop(i)
                return True
        return False

    def equip(self, item_id: str, slot: str) -> bool:
        item = next((i for i in self._items if i.get("id") == item_id), None)
        if item and slot in self._equipped:
            self._equipped[slot] = item
            return True
        return False

    def unequip(self, slot: str) -> None:
        self._equipped[slot] = None

    def get_equipped(self, slot: str) -> dict | None:
        return self._equipped.get(slot)

    @property
    def items(self) -> list[dict]:
        return list(self._items)

    def to_dict(self) -> dict:
        return {"items": self._items, "equipped": self._equipped}

    def from_dict(self, data: dict) -> None:
        self._items = data.get("items", [])
        self._equipped = data.get("equipped", {s: None for s in self.EQUIP_SLOTS})
