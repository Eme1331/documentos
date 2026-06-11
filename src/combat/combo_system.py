"""Input buffer and combo chain detection."""
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Callable


@dataclass
class ComboEntry:
    action: str
    timestamp: float


@dataclass
class ComboDefinition:
    name: str
    sequence: list[str]
    max_gap_ms: float
    multiplier: float = 1.5
    callback: Callable | None = None


class ComboSystem:
    BUFFER_SIZE = 8
    DEFAULT_MAX_GAP = 400.0  # ms

    def __init__(self) -> None:
        self._buffer: list[ComboEntry] = []
        self._combos: list[ComboDefinition] = []

    def add_combo(self, combo: ComboDefinition) -> None:
        self._combos.append(combo)

    def push_action(self, action: str) -> ComboDefinition | None:
        now = time.time() * 1000
        self._buffer.append(ComboEntry(action, now))
        if len(self._buffer) > self.BUFFER_SIZE:
            self._buffer.pop(0)
        return self._check_combos()

    def _check_combos(self) -> ComboDefinition | None:
        for combo in sorted(self._combos, key=lambda c: -len(c.sequence)):
            seq = combo.sequence
            if len(self._buffer) < len(seq):
                continue
            tail = self._buffer[-len(seq):]
            if [e.action for e in tail] != seq:
                continue
            for i in range(1, len(tail)):
                if tail[i].timestamp - tail[i-1].timestamp > combo.max_gap_ms:
                    break
            else:
                self._buffer.clear()
                if combo.callback:
                    combo.callback()
                return combo
        return None

    def clear(self) -> None:
        self._buffer.clear()
