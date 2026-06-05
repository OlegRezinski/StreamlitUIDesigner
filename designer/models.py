from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PropDefinition:
    name: str
    label: str
    input_type: str
    default: Any
    options: Optional[List[str]] = None


@dataclass
class WidgetDefinition:
    type: str
    label: str
    props_schema: List[PropDefinition]
    defaults: Dict[str, Any]
    codegen: Callable[["WidgetInstance"], List[str]]
    render: Callable[["WidgetInstance"], None]


@dataclass
class WidgetInstance:
    id: str
    type: str
    props: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    column_index: Optional[int] = None


@dataclass
class Design:
    name: str
    widgets: List[WidgetInstance] = field(default_factory=list)
    screen_width: str = "regular"
    background_color: str = "#FFFFFF"
    background_image: str = ""
