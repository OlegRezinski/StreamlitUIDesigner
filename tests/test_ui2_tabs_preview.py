from __future__ import annotations

import uuid

from streamlit.testing.v1 import AppTest

from designer.models import Design, WidgetInstance


def _wi(type_, props=None, parent_id=None):
    return WidgetInstance(id=str(uuid.uuid4()), type=type_, props=props or {}, parent_id=parent_id)


def test_ui2_tabs_preview_renders_tabs_and_children() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    # Set up a design with a tabs widget + children
    tabs_widget = _wi("tabs", {"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = _wi("tab", {"label": "Tab 1"}, parent_id=tabs_widget.id)
    tab2 = _wi("tab", {"label": "Tab 2"}, parent_id=tabs_widget.id)
    child = _wi("button", {"label": "Hello"}, parent_id=tab1.id)

    design = at.session_state["design"]
    design.widgets.extend([tabs_widget, tab1, tab2, child])

    at = at.run(timeout=20)

    # Verify that the tabs caption appears
    caption_values = [c.value for c in at.caption]
    assert any("st.tabs" in v for v in caption_values)

