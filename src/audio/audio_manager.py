"""pygame.mixer wrapper."""
from __future__ import annotations
import pygame


class AudioManager:
    def __init__(self, assets, volume_config: dict = None) -> None:
        self._assets = assets
        cfg = volume_config or {}
        self.master = float(cfg.get("master", 1.0))
        self.music_vol = float(cfg.get("music", 0.7))
        self.sfx_vol = float(cfg.get("sfx", 0.8))
        try:
            pygame.mixer.set_num_channels(32)
        except Exception:
            pass

    def set_master(self, vol: float) -> None:
        self.master = max(0.0, min(1.0, vol))

    def set_music_volume(self, vol: float) -> None:
        self.music_vol = max(0.0, min(1.0, vol))
        try:
            pygame.mixer.music.set_volume(self.music_vol * self.master)
        except Exception:
            pass
