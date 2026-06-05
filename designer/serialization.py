from __future__ import annotations

from typing import Any, Dict

from .models import Design, WidgetInstance


def widget_to_dict(widget: WidgetInstance) -> Dict[str, Any]:
    return {
        "id": widget.id,
        "type": widget.type,
        "props": dict(widget.props),
        "parent_id": widget.parent_id,
        "column_index": widget.column_index,
    }


def widget_from_dict(data: Dict[str, Any]) -> WidgetInstance:
    return WidgetInstance(
        id=data["id"],
        type=data["type"],
        props=dict(data.get("props", {})),
        parent_id=data.get("parent_id"),
        column_index=data.get("column_index"),
    )


def design_to_dict(design: Design) -> Dict[str, Any]:
    return {
        "name": design.name,
        "widgets": [widget_to_dict(w) for w in design.widgets],
        "screen_width": design.screen_width,
        "background_color": design.background_color,
        "background_image": design.background_image,
    }


def design_from_dict(data: Dict[str, Any]) -> Design:
    widgets = [widget_from_dict(w) for w in data.get("widgets", [])]
    return Design(
        name=data.get("name", "Untitled"),
        widgets=widgets,
        screen_width=data.get("screen_width", "regular"),
        background_color=data.get("background_color", "#FFFFFF"),
        background_image=data.get("background_image", ""),
    )
