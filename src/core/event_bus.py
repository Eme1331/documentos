"""Typed pub/sub event bus."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Type, Any


# --- Typed event dataclasses ---
@dataclass
class Event:
    """Base event."""


@dataclass
class PlayerDamagedEvent(Event):
    amount: int
    source: Any = None
    remaining_hp: int = 0


@dataclass
class EnemyDiedEvent(Event):
    enemy_id: int = 0
    xp_reward: int = 0
    position: tuple = (0.0, 0.0)
    enemy_type: str = ""


@dataclass
class XPGainedEvent(Event):
    amount: int = 0
    total_xp: int = 0


@dataclass
class BossPhaseChangedEvent(Event):
    boss_name: str = ""
    new_phase: int = 0
    total_phases: int = 1


@dataclass
class CheckpointReachedEvent(Event):
    checkpoint_id: str = ""
    position: tuple = (0.0, 0.0)


@dataclass
class LevelCompletedEvent(Event):
    level_id: str = ""
    time_seconds: float = 0.0


class EventBus:
    """Simple synchronous typed pub/sub dispatcher."""

    def __init__(self) -> None:
        self._subscribers: dict[Type[Event], list[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: Type[Event], handler: Callable[[Event], None]) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: Type[Event], handler: Callable[[Event], None]) -> None:
        handlers = self._subscribers.get(event_type)
        if handlers and handler in handlers:
            handlers.remove(handler)

    def emit(self, event: Event) -> None:
        for handler in list(self._subscribers.get(type(event), [])):
            handler(event)

    def clear(self) -> None:
        self._subscribers.clear()
