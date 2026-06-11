"""Skill tree DAG loader and unlock logic."""
from __future__ import annotations
import json
import os
import settings


class SkillNode:
    def __init__(self, data: dict) -> None:
        self.id: str = data["id"]
        self.name: str = data.get("name", self.id)
        self.cost: int = int(data.get("cost", 1))
        self.requires: list[str] = data.get("requires", [])
        self.effect: dict = data.get("effect", {})
        self.unlocked = False


class SkillTree:
    def __init__(self, character_id: str) -> None:
        self._char = character_id
        self._nodes: dict[str, SkillNode] = {}
        self._load()

    def _load(self) -> None:
        path = os.path.join(settings.DATA_DIR, "skill_trees.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            char_data = data.get(self._char, {})
            for node_data in char_data.get("nodes", []):
                n = SkillNode(node_data)
                self._nodes[n.id] = n
        except Exception:
            pass

    def can_unlock(self, node_id: str, available_points: int) -> bool:
        node = self._nodes.get(node_id)
        if not node or node.unlocked:
            return False
        if available_points < node.cost:
            return False
        return all(self._nodes.get(r, SkillNode({"id": r})).unlocked
                   for r in node.requires)

    def unlock(self, node_id: str) -> dict:
        node = self._nodes.get(node_id)
        if node:
            node.unlocked = True
            return node.effect
        return {}

    def get_modifiers(self) -> dict:
        result: dict = {}
        for node in self._nodes.values():
            if node.unlocked:
                for k, v in node.effect.items():
                    result[k] = result.get(k, 1.0) * float(v)
        return result

    def unlocked_ids(self) -> list[str]:
        return [n.id for n in self._nodes.values() if n.unlocked]

    def restore(self, ids: list[str]) -> None:
        for nid in ids:
            if nid in self._nodes:
                self._nodes[nid].unlocked = True

    @property
    def all_nodes(self) -> list[SkillNode]:
        return list(self._nodes.values())
