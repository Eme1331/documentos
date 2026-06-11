"""Instantiate correct character class from data."""
from __future__ import annotations
import json
import os
import settings


def create_character(char_id: str):
    path = os.path.join(settings.DATA_DIR, "characters.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        chars = data.get("characters", data)
        if isinstance(chars, list):
            stats = next((c for c in chars if c.get("id") == char_id), {})
        else:
            stats = chars.get(char_id, {})
    except Exception:
        stats = {}

    if char_id == "ethan":
        from src.characters.ethan import Ethan
        return Ethan(stats)
    elif char_id == "cy_x7":
        from src.characters.cy_x7 import CYX7
        return CYX7(stats)
    elif char_id == "zhyra":
        from src.characters.zhyra import Zhyra
        return Zhyra(stats)
    else:
        from src.characters.ethan import Ethan
        return Ethan(stats)
