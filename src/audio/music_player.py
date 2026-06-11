"""Crossfade music player."""
from __future__ import annotations
import pygame
from enum import Enum


class MusicState(Enum):
    EXPLORATION = "exploration"
    COMBAT = "combat"
    BOSS = "boss"
    CUTSCENE = "cutscene"
    MENU = "menu"


class MusicPlayer:
    def __init__(self, audio_manager=None) -> None:
        self._am = audio_manager
        self.current_state = MusicState.MENU
        self._current_file: str = ""

    def play_for_state(self, state: MusicState, file_path: str) -> None:
        if file_path == self._current_file:
            return
        self._current_file = file_path
        self.current_state = state
        try:
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.load(file_path)
            vol = (self._am.music_vol * self._am.master) if self._am else 0.7
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1, fade_ms=800)
        except Exception:
            pass

    def stop(self) -> None:
        try:
            pygame.mixer.music.fadeout(500)
        except Exception:
            pass
        self._current_file = ""
