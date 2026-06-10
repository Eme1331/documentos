"""Base ECS entity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type, TypeVar, Any

T = TypeVar("T")

_next_id = [1]


def next_entity_id() -> int:
    eid = _next_id[0]
    _next_id[0] += 1
    return eid


@dataclass
class Entity:
    id: int = field(default_factory=next_entity_id)
    components: dict = field(default_factory=dict)
    active: bool = True
    tags: set = field(default_factory=set)
    layer: str = "default"

    def add(self, component: Any) -> "Entity":
        self.components[type(component)] = component
        # allow base-class lookup for subclassed components
        for base in type(component).__mro__:
            if base is object:
                break
            self.components.setdefault(base, component)
        return self

    def get(self, ctype: Type[T]) -> T | None:
        return self.components.get(ctype)

    def has(self, ctype: Type) -> bool:
        return ctype in self.components

    def remove(self, ctype: Type) -> None:
        self.components.pop(ctype, None)

    def add_tag(self, tag: str) -> None:
        self.tags.add(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags
