"""Core Game class: window, main loop with fixed-timestep accumulator."""
from __future__ import annotations

import os
import json
import pygame

import settings
from src.core.state_machine import StateMachine
from src.core.event_bus import EventBus
from src.core.asset_manager import AssetManager
from src.core.input_handler import InputHandler


class Game:
    TARGET_FPS = 60
    FIXED_TIMESTEP = 1.0 / 60.0
    MAX_FRAME_TIME = 0.25

    def __init__(self) -> None:
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass

        self.config = self._load_config()
        res = self.config.get("resolution", list(settings.SCREEN_SIZE))
        self.screen = pygame.display.set_mode((int(res[0]), int(res[1])))
        pygame.display.set_caption(settings.TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.event_bus = EventBus()
        self.assets = AssetManager(settings.ASSETS_DIR)
        bindings = self._load_bindings()
        self.input = InputHandler(bindings)
        self.state_machine = StateMachine()

        # Shared session data (selected character, save slot, etc.)
        self.session: dict = {"character": "ethan", "level_id": "level_01"}

        # Audio manager (optional, graceful)
        try:
            from src.audio.audio_manager import AudioManager
            self.audio = AudioManager(self.assets, self.config.get("volume", {}))
        except Exception:
            self.audio = None

        self._accumulator = 0.0
        self._boot_initial_state()

    # ------------------------------------------------------------------
    def _load_config(self) -> dict:
        path = os.path.join(settings.DATA_DIR, "config.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"resolution": list(settings.SCREEN_SIZE), "volume": {}}

    def _load_bindings(self) -> dict:
        keybinds = self.config.get("keybinds", {})
        out: dict[str, int] = {}
        for action, keyname in keybinds.items():
            if isinstance(keyname, int):
                out[action] = keyname
            elif isinstance(keyname, str):
                try:
                    out[action] = pygame.key.key_code(keyname)
                except Exception:
                    pass
        return out

    def _boot_initial_state(self) -> None:
        from src.states.splash_state import SplashState
        self.state_machine.push(SplashState(self))

    # ------------------------------------------------------------------
    def quit(self) -> None:
        self.running = False

    def run(self) -> None:
        while self.running and not self.state_machine.is_empty:
            frame_time = min(self.clock.tick(self.TARGET_FPS) / 1000.0,
                             self.MAX_FRAME_TIME)
            self._handle_events()

            self._accumulator += frame_time
            while self._accumulator >= self.FIXED_TIMESTEP:
                self.state_machine.fixed_update(self.FIXED_TIMESTEP)
                self._accumulator -= self.FIXED_TIMESTEP

            self.state_machine.update(frame_time)

            self.screen.fill(settings.BLACK)
            self.state_machine.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

    def _handle_events(self) -> None:
        self.input.begin_frame()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.input.process_event(event)
            self.state_machine.handle_event(event)
