from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

from designer.models import Design, WidgetInstance


def _button_widget(widget_id: str, label: str, parent_id: str | None = None) -> WidgetInstance:
    return WidgetInstance(
        id=widget_id,
        type="button",
        props={
            "label": label,
            "background_color": "#2E6CF6",
            "text_color": "#FFFFFF",
            "width": "",
            "height": "",
            "expand": False,
        },
        parent_id=parent_id,
    )


def test_ui2_sidebar_preview_uses_30_70_layout_when_expanded() -> None:
    sidebar = WidgetInstance(id="sidebar-root", type="sidebar", props={"label": "Navigation"})
    sidebar_child = _button_widget("sidebar-child", "Sidebar action", parent_id=sidebar.id)
    main_child = _button_widget("main-child", "Main action")
    design = Design(name="Preview", widgets=[sidebar, sidebar_child, main_child])

    at = AppTest.from_file("UI_2.py")
    at.session_state["design"] = design
    at = at.run(timeout=20)

    assert at.button(key="ui2_preview_sidebar_toggle").label == "◀"
    assert any(caption.value == "st.sidebar — Navigation" for caption in at.caption)
    assert any(button.label == "Sidebar action" for button in at.button)
    assert any(button.label == "Main action" for button in at.button)
    assert any(col.weight == pytest.approx(0.3, abs=1e-6) for col in at.columns)
    assert any(col.weight == pytest.approx(0.7, abs=1e-6) for col in at.columns)


def test_ui2_sidebar_preview_collapses_horizontally() -> None:
    sidebar = WidgetInstance(id="sidebar-root", type="sidebar", props={"label": "Navigation"})
    sidebar_child = _button_widget("sidebar-child", "Sidebar action", parent_id=sidebar.id)
    main_child = _button_widget("main-child", "Main action")
    design = Design(name="Preview", widgets=[sidebar, sidebar_child, main_child])

    at = AppTest.from_file("UI_2.py")
    at.session_state["design"] = design
    at = at.run(timeout=20)

    at.button(key="ui2_preview_sidebar_toggle").click()
    at = at.run(timeout=20)

    assert at.button(key="ui2_preview_sidebar_toggle").label == "▶"
    assert not any(caption.value == "st.sidebar — Navigation" for caption in at.caption)
    assert all(button.label != "Sidebar action" for button in at.button)
    assert any(button.label == "Main action" for button in at.button)
    assert any(col.weight == pytest.approx(0.06, abs=1e-6) for col in at.columns)
    assert any(col.weight == pytest.approx(0.94, abs=1e-6) for col in at.columns)

