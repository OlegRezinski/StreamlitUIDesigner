from __future__ import annotations

import uuid
import pytest

from designer.models import Design, WidgetInstance
from designer.codegen import generate_streamlit_code as generate_code
from designer.registry import get_widget, clear_registry
from designer.widgets import register_default_widgets
from streamlit.testing.v1 import AppTest


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def _make_design(*widgets):
    return Design(name="test", widgets=list(widgets))


def _wi(type_, props=None, parent_id=None):
    return WidgetInstance(id=str(uuid.uuid4()), type=type_, props=props or {}, parent_id=parent_id)


def _run_ui2(design, extra_state: dict | None = None):
    at = AppTest.from_file("UI_2.py")
    at.session_state["design"] = design
    if extra_state:
        for k, v in extra_state.items():
            at.session_state[k] = v
    return at.run(timeout=20)


def test_tabs_registered():
    defn = get_widget("tabs")
    assert defn is not None
    assert defn.label == "Tabs"
    prop_names = [p.name for p in defn.props_schema]
    assert "label" in prop_names
    assert "tabs" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names
    assert "default" in prop_names


def test_tab_registered():
    defn = get_widget("tab")
    assert defn is not None
    assert defn.label == "Tab"


def test_tabs_not_in_tab_props_schema():
    defn = get_widget("tabs")
    key_filter = {"key", "on_change", "args", "kwargs"}
    prop_names = {p.name for p in defn.props_schema}
    assert not prop_names.intersection(key_filter)


def test_codegen_tabs_empty():
    tabs = _wi("tabs", {"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = _wi("tab", {"label": "Tab 1"}, parent_id=tabs.id)
    tab2 = _wi("tab", {"label": "Tab 2"}, parent_id=tabs.id)
    d = _make_design(tabs, tab1, tab2)
    code = generate_code(d)
    assert "pass" in code
    assert "with tabs_1[0]:" in code
    assert "with tabs_1[1]:" in code


def test_codegen_tabs_label_comment():
    tabs = _wi("tabs", {"label": "My Tabs", "tabs": 1, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = _wi("tab", {"label": "First"}, parent_id=tabs.id)
    d = _make_design(tabs, tab1)
    code = generate_code(d)
    assert "# My Tabs" in code


def test_codegen_tabs_custom_width():
    tabs = _wi("tabs", {"label": "Tabs", "tabs": 2, "width": "custom", "custom_width": 480, "default": ""})
    tab1 = _wi("tab", {"label": "Tab 1"}, parent_id=tabs.id)
    tab2 = _wi("tab", {"label": "Tab 2"}, parent_id=tabs.id)
    d = _make_design(tabs, tab1, tab2)
    code = generate_code(d)
    assert "width=480" in code


def test_codegen_tabs_default_valid():
    tabs = _wi("tabs", {"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": "Second"})
    tab1 = _wi("tab", {"label": "First"}, parent_id=tabs.id)
    tab2 = _wi("tab", {"label": "Second"}, parent_id=tabs.id)
    d = _make_design(tabs, tab1, tab2)
    code = generate_code(d)
    assert "default='Second'" in code


def test_codegen_tabs_default_invalid():
    tabs = _wi("tabs", {"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": "NonExistent"})
    tab1 = _wi("tab", {"label": "First"}, parent_id=tabs.id)
    tab2 = _wi("tab", {"label": "Second"}, parent_id=tabs.id)
    d = _make_design(tabs, tab1, tab2)
    code = generate_code(d)
    assert "default='NonExistent'" not in code


def test_codegen_tabs_with_children():
    tabs = _wi("tabs", {"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = _wi("tab", {"label": "Tab 1"}, parent_id=tabs.id)
    tab2 = _wi("tab", {"label": "Tab 2"}, parent_id=tabs.id)
    child = _wi("text", {"text": "Hello"}, parent_id=tab1.id)
    d = _make_design(tabs, tab1, tab2, child)
    code = generate_code(d)
    assert "with tabs_1[0]:" in code
    assert "with tabs_1[1]:" in code
    lines = code.splitlines()
    tab0_idx = next(i for i, l in enumerate(lines) if "with tabs_1[0]:" in l)
    tab1_idx = next(i for i, l in enumerate(lines) if "with tabs_1[1]:" in l)
    between = lines[tab0_idx + 1:tab1_idx]
    assert not all("pass" in l for l in between)


def test_adding_widget_to_tabs_lands_in_first_tab_by_default():
    """When tabs container is selected and no target_tab_id is set, new widget lands in first tab."""
    tabs = WidgetInstance(id="tabs1", type="tabs", props={"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = WidgetInstance(id="tab1", type="tab", props={"label": "Tab 1"}, parent_id="tabs1")
    tab2 = WidgetInstance(id="tab2", type="tab", props={"label": "Tab 2"}, parent_id="tabs1")
    design = Design(name="Test", widgets=[tabs, tab1, tab2])

    at = _run_ui2(design, {
        "hierarchy_checked_id": "tab1",
        "hierarchy_checked_prev": ["tab1"],
        "target_container_id": "tabs1",
        "add_to_container": "tabs1",
        "target_tab_id": "tab1",
    })
    btn = at.button(key="ui2_add_Text elements_caption")
    assert btn is not None
    btn.click()
    at = at.run(timeout=20)

    result_design = at.session_state["design"]
    captions = [w for w in result_design.widgets if w.type == "caption"]
    assert len(captions) == 1
    assert captions[0].parent_id == "tab1", f"Expected parent_id='tab1', got {captions[0].parent_id!r}"


def test_adding_widget_to_tabs_lands_in_second_tab_when_targeted():
    """When target_tab_id is set to second tab, new widget lands there."""
    tabs = WidgetInstance(id="tabs1", type="tabs", props={"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = WidgetInstance(id="tab1", type="tab", props={"label": "Tab 1"}, parent_id="tabs1")
    tab2 = WidgetInstance(id="tab2", type="tab", props={"label": "Tab 2"}, parent_id="tabs1")
    design = Design(name="Test", widgets=[tabs, tab1, tab2])

    at = _run_ui2(design, {
        "hierarchy_checked_id": "tab2",
        "hierarchy_checked_prev": ["tab2"],
        "target_container_id": "tabs1",
        "add_to_container": "tabs1",
        "target_tab_id": "tab2",
    })
    btn = at.button(key="ui2_add_Text elements_caption")
    assert btn is not None
    btn.click()
    at = at.run(timeout=20)

    result_design = at.session_state["design"]
    captions = [w for w in result_design.widgets if w.type == "caption"]
    assert len(captions) == 1
    assert captions[0].parent_id == "tab2", f"Expected parent_id='tab2', got {captions[0].parent_id!r}"


def test_hierarchy_selecting_tab_sets_target_tab_id():
    """Selecting a tab in the hierarchy sets target_container_id to the parent tabs and target_tab_id to that tab."""
    tabs = WidgetInstance(id="tabs1", type="tabs", props={"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = WidgetInstance(id="tab1", type="tab", props={"label": "Tab 1"}, parent_id="tabs1")
    tab2 = WidgetInstance(id="tab2", type="tab", props={"label": "Tab 2"}, parent_id="tabs1")
    design = Design(name="Test", widgets=[tabs, tab1, tab2])

    at = _run_ui2(design, {
        "hierarchy_checked_id": "tab2",
        "hierarchy_checked_prev": ["tab2"],
    })

    assert at.session_state["target_container_id"] == "tabs1"
    assert at.session_state["target_tab_id"] == "tab2"


def test_hierarchy_selecting_child_inside_tab_sets_target_tab_id():
    """Selecting a widget inside a tab sets target_container_id to the tabs widget and target_tab_id to the containing tab."""
    tabs = WidgetInstance(id="tabs1", type="tabs", props={"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = WidgetInstance(id="tab1", type="tab", props={"label": "Tab 1"}, parent_id="tabs1")
    tab2 = WidgetInstance(id="tab2", type="tab", props={"label": "Tab 2"}, parent_id="tabs1")
    child = WidgetInstance(id="child1", type="text", props={"text": "Hi"}, parent_id="tab2")
    design = Design(name="Test", widgets=[tabs, tab1, tab2, child])

    at = _run_ui2(design, {
        "hierarchy_checked_id": "child1",
        "hierarchy_checked_prev": ["child1"],
    })

    assert at.session_state["target_container_id"] == "tabs1"
    assert at.session_state["target_tab_id"] == "tab2"


def test_hierarchy_selecting_tabs_container_sets_first_tab_as_target():
    """Selecting the tabs container itself sets target_container_id=tabs and target_tab_id=first tab."""
    tabs = WidgetInstance(id="tabs1", type="tabs", props={"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""})
    tab1 = WidgetInstance(id="tab1", type="tab", props={"label": "Tab 1"}, parent_id="tabs1")
    tab2 = WidgetInstance(id="tab2", type="tab", props={"label": "Tab 2"}, parent_id="tabs1")
    design = Design(name="Test", widgets=[tabs, tab1, tab2])

    at = _run_ui2(design, {
        "hierarchy_checked_id": "tabs1",
        "hierarchy_checked_prev": ["tabs1"],
    })

    assert at.session_state["target_container_id"] == "tabs1"
    assert at.session_state["target_tab_id"] == "tab1"
