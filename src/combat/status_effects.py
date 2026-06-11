"""Status effect system."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class StatusEffect:
    name: str
    duration: float
    _elapsed: float = 0.0

    @property
    def active(self) -> bool:
        return self._elapsed < self.duration

    def update(self, entity, dt: float) -> None:
        self._elapsed += dt
        self._tick(entity, dt)

    def _tick(self, entity, dt: float) -> None:
        pass


class Burn(StatusEffect):
    def __init__(self, duration: float = 3.0, dps: float = 5.0) -> None:
        super().__init__("burn", duration)
        self.dps = dps

    def _tick(self, entity, dt: float) -> None:
        from src.entities.components.health import Health
        hp = entity.get(Health)
        if hp:
            hp.take_damage(int(self.dps * dt), source="burn")


class Freeze(StatusEffect):
    def __init__(self, duration: float = 2.0) -> None:
        super().__init__("freeze", duration)

    def _tick(self, entity, dt: float) -> None:
        from src.entities.components.transform import Transform
        tr = entity.get(Transform)
        if tr:
            tr.velocity.x *= 0.3


class Stun(StatusEffect):
    def __init__(self, frames: int = 30) -> None:
        super().__init__("stun", frames / 60.0)


class OverclockBuff(StatusEffect):
    def __init__(self, duration: float = 8.0) -> None:
        super().__init__("overclock", duration)
        self.speed_bonus = 1.3
        self.attack_bonus = 1.2


class GravityInversion(StatusEffect):
    def __init__(self, duration: float = 4.0) -> None:
        super().__init__("gravity_inversion", duration)

    def _tick(self, entity, dt: float) -> None:
        from src.entities.components.transform import Transform
        tr = entity.get(Transform)
        if tr:
            tr.velocity.y -= 980.0 * 2 * dt


class StatusEffectManager:
    def __init__(self) -> None:
        self._effects: list[StatusEffect] = []

    def add(self, effect: StatusEffect) -> None:
        self._effects = [e for e in self._effects if e.name != effect.name]
        self._effects.append(effect)

    def update(self, entity, dt: float) -> None:
        for effect in list(self._effects):
            effect.update(entity, dt)
        self._effects = [e for e in self._effects if e.active]

    def has(self, name: str) -> bool:
        return any(e.name == name for e in self._effects)

    def get(self, name: str) -> StatusEffect | None:
        return next((e for e in self._effects if e.name == name), None)

    def clear(self) -> None:
        self._effects.clear()
