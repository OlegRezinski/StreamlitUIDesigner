from __future__ import annotations

from typing import Dict, List

from .models import WidgetDefinition

_REGISTRY: Dict[str, WidgetDefinition] = {}


def register_widget(definition: WidgetDefinition) -> None:
    if definition.type in _REGISTRY:
        raise ValueError(f"Widget type already registered: {definition.type}")
    _REGISTRY[definition.type] = definition


def get_widget(widget_type: str) -> WidgetDefinition:
    if widget_type not in _REGISTRY:
        raise KeyError(f"Unknown widget type: {widget_type}")
    return _REGISTRY[widget_type]


def list_widgets() -> List[WidgetDefinition]:
    return list(_REGISTRY.values())


def clear_registry() -> None:
    _REGISTRY.clear()


def has_widget(widget_type: str) -> bool:
    return widget_type in _REGISTRY
