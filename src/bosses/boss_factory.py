"""Create bosses by ID."""
from __future__ import annotations
import json
import os
import settings


_BOSS_MAP: dict = {}


def _load_data() -> dict:
    global _BOSS_MAP
    if _BOSS_MAP:
        return _BOSS_MAP
    path = os.path.join(settings.DATA_DIR, "bosses.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            bosses = raw.get("bosses", raw)
            if isinstance(bosses, list):
                _BOSS_MAP = {b["id"]: b for b in bosses if isinstance(b, dict)}
            elif isinstance(bosses, dict):
                _BOSS_MAP = bosses
    except Exception:
        pass
    return _BOSS_MAP


def create_boss(boss_id: str, x: float, y: float, event_bus=None):
    data = _load_data()
    stats = data.get(boss_id, {})

    _map = {
        "titan_x_drone":     "TitanXDrone",
        "scorpion_mecha":     "ScorpionMecha",
        "cryo_sentinel":      "CryoSentinel",
        "mutant_bio_core":    "MutantBioCore",
        "storm_valkyrie":     "StormValkyrie",
        "magma_colossus":     "MagmaColossus",
        "neuro_beast":        "NeuroBeast",
        "moon_reaper":        "MoonReaper",
        "void_harbinger":     "VoidHarbinger",
        "nexus_prime":        "NexusPrime",
    }
    class_name = _map.get(boss_id, "")
    if class_name:
        try:
            mod_name = boss_id  # e.g. "titan_x_drone"
            module = __import__(
                f"src.bosses.implementations.{mod_name}",
                fromlist=[class_name])
            cls = getattr(module, class_name)
            return cls(x, y, stats or {"name": boss_id, "hp": 500}, event_bus)
        except Exception:
            pass

    from src.bosses.base_boss import BaseBoss
    return BaseBoss(x, y, stats or {"name": boss_id, "hp": 500}, event_bus)
