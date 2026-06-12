from __future__ import annotations

import uuid

from designer.backgrounds import parse_background_style
from designer.code_import import import_design_from_code
from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _w(widget_id: str, widget_type: str, **props) -> WidgetInstance:
    base = dict(get_widget(widget_type).defaults)
    base.update(props)
    return WidgetInstance(id=widget_id, type=widget_type, props=base)


def _types_tree(design: Design) -> list[tuple[str, str | None]]:
    """List of (type, parent_type) for structural comparison (order-preserving)."""
    by_id = {w.id: w for w in design.widgets}
    result = []
    for w in design.widgets:
        parent_type = by_id[w.parent_id].type if w.parent_id in by_id else None
        result.append((w.type, parent_type))
    return result


# --------------------------------------------------------------------------
# parse_background_style unit tests
# --------------------------------------------------------------------------
def test_parse_background_style_color_and_image() -> None:
    css = '<style>.stApp { background-color: #123456; background-image: url("http://x/y.png"); }</style>'
    color, image = parse_background_style(css)
    assert color == "#123456"
    assert image == "http://x/y.png"


def test_parse_background_style_color_only() -> None:
    color, image = parse_background_style("<style>.stApp { background-color: red; }</style>")
    assert color == "red"
    assert image == ""


def test_parse_background_style_empty() -> None:
    assert parse_background_style("") == ("", "")


# --------------------------------------------------------------------------
# basic / structural reconstruction
# --------------------------------------------------------------------------
def test_import_flat_widgets_structure() -> None:
    design = Design(name="D", widgets=[
        _w("a", "button", label="Click"),
        _w("b", "checkbox", label="Agree", checked=True),
        _w("c", "text_input", label="Name", value="x"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    types = [w.type for w in result.design.widgets]
    assert types == ["button", "checkbox", "text_input"]


def test_import_reuses_key_uuid_as_id() -> None:
    design = Design(name="D", widgets=[_w("11111111-2222-3333-4444-555555555555", "checkbox", label="X")])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert result.design.widgets[0].id == "11111111-2222-3333-4444-555555555555"


def test_import_recovers_common_props() -> None:
    design = Design(name="D", widgets=[
        _w("a", "checkbox", label="Agree", checked=True, disabled=True),
        _w("b", "slider", label="S", min=2.0, max=8.0, value=5.0, step=0.5),
        _w("c", "selectbox", label="Pick", options="One, Two, Three", index=1),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    cb, sl, sb = result.design.widgets
    assert cb.props["label"] == "Agree"
    assert cb.props["checked"] is True
    assert cb.props["disabled"] is True
    assert sl.props["min"] == 2.0 and sl.props["max"] == 8.0
    assert sl.props["value"] == 5.0 and sl.props["step"] == 0.5
    assert sb.props["index"] == 1
    # options list is joined back to a comma string
    assert sb.props["options"] == "One, Two, Three"


# --------------------------------------------------------------------------
# containers / structure
# --------------------------------------------------------------------------
def test_import_container_nesting() -> None:
    design = Design(name="D", widgets=[
        _w("ctr", "container"),
        WidgetInstance(id="child", type="button",
                       props=dict(get_widget("button").defaults), parent_id="ctr"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert _types_tree(result.design) == [("container", None), ("button", "container")]


def test_import_columns_with_ratios() -> None:
    design = Design(name="D", widgets=[
        WidgetInstance(id="cc", type="columns_container",
                       props={"label": "Columns", "background_color": "#FFFFFF", "columns": 2}),
        WidgetInstance(id="c0", type="column",
                       props={"label": "Column", "background_color": "#FFFFFF", "ratio": 2},
                       parent_id="cc", column_index=0),
        WidgetInstance(id="c1", type="column",
                       props={"label": "Column", "background_color": "#FFFFFF", "ratio": 3},
                       parent_id="cc", column_index=1),
        WidgetInstance(id="b0", type="button", props=dict(get_widget("button").defaults),
                       parent_id="c0", column_index=0),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    cc = next(w for w in result.design.widgets if w.type == "columns_container")
    cols = [w for w in result.design.widgets if w.type == "column"]
    assert cc.props["columns"] == 2
    assert [c.props["ratio"] for c in cols] == [2, 3]
    # the button lands inside the first column
    btn = next(w for w in result.design.widgets if w.type == "button")
    assert btn.parent_id == cols[0].id
    assert btn.column_index == 0


def test_import_tabs_with_labels() -> None:
    design = Design(name="D", widgets=[
        WidgetInstance(id="t", type="tabs",
                       props={"label": "Tabs", "tabs": 2, "width": "stretch",
                              "custom_width": 320, "default": ""}),
        WidgetInstance(id="t0", type="tab", props={"label": "Alpha"}, parent_id="t"),
        WidgetInstance(id="t1", type="tab", props={"label": "Beta"}, parent_id="t"),
        WidgetInstance(id="b", type="button", props=dict(get_widget("button").defaults),
                       parent_id="t0"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    tabs = next(w for w in result.design.widgets if w.type == "tabs")
    tab_ws = [w for w in result.design.widgets if w.type == "tab"]
    assert tabs.props["tabs"] == 2
    assert [t.props["label"] for t in tab_ws] == ["Alpha", "Beta"]
    btn = next(w for w in result.design.widgets if w.type == "button")
    assert btn.parent_id == tab_ws[0].id


def test_import_sidebar() -> None:
    design = Design(name="D", widgets=[
        _w("s", "sidebar"),
        WidgetInstance(id="b", type="button", props=dict(get_widget("button").defaults),
                       parent_id="s"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert _types_tree(result.design) == [("sidebar", None), ("button", "sidebar")]


def test_import_form_drops_submit_button() -> None:
    design = Design(name="D", widgets=[
        _w("f", "form"),
        WidgetInstance(id="b", type="button", props=dict(get_widget("button").defaults),
                       parent_id="f"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    # exactly one form + one button; the auto-emitted form_submit_button is dropped
    assert [w.type for w in result.design.widgets] == ["form", "button"]


def test_import_expander() -> None:
    design = Design(name="D", widgets=[_w("e", "expander", label="More", expanded=True)])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert result.design.widgets[0].type == "expander"


# --------------------------------------------------------------------------
# page-level settings
# --------------------------------------------------------------------------
def test_import_wide_layout() -> None:
    design = Design(name="D", screen_width="wide", widgets=[_w("a", "button")])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert result.design.screen_width == "wide"


def test_import_background_color_and_image() -> None:
    design = Design(name="D", background_color="#abcdef",
                    background_image="https://example.com/bg.png",
                    widgets=[_w("a", "button")])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert result.design.background_color == "#abcdef"
    assert result.design.background_image == "https://example.com/bg.png"


# --------------------------------------------------------------------------
# edge cases
# --------------------------------------------------------------------------
def test_import_non_streamlit_code_rejected() -> None:
    result = import_design_from_code("x = 1\nprint('hello world')\n")
    assert result.design is None
    assert result.errors


def test_import_syntax_error_reported() -> None:
    result = import_design_from_code("import streamlit as st\nst.button('x'\n")
    assert result.design is None
    assert result.errors
    assert result.errors[0].lineno is not None


def test_import_unknown_widget_warns_and_continues() -> None:
    code = (
        "import streamlit as st\n"
        "st.totally_made_up_widget('x')\n"
        "st.button('Real', key='k1')\n"
    )
    result = import_design_from_code(code)
    assert result.ok
    assert any("totally_made_up_widget" in w.message for w in result.warnings)
    assert [w.type for w in result.design.widgets] == ["button"]


def test_import_non_literal_arg_uses_default_and_warns() -> None:
    code = (
        "import streamlit as st\n"
        "some_var = 'hello'\n"
        "st.text_input('Name', value=some_var, key='k')\n"
    )
    result = import_design_from_code(code)
    assert result.ok
    ti = result.design.widgets[0]
    assert ti.type == "text_input"
    # value falls back to default because it was non-literal
    assert ti.props["value"] == get_widget("text_input").defaults["value"]
    assert result.warnings


def test_import_custom_column_var_name() -> None:
    code = (
        "import streamlit as st\n"
        "grid = st.columns([1, 1])\n"
        "with grid[0]:\n"
        "    st.button('A', key='a')\n"
        "with grid[1]:\n"
        "    st.button('B', key='b')\n"
    )
    result = import_design_from_code(code)
    assert result.ok
    cols = [w for w in result.design.widgets if w.type == "column"]
    buttons = [w for w in result.design.widgets if w.type == "button"]
    assert len(cols) == 2 and len(buttons) == 2
    assert buttons[0].parent_id == cols[0].id
    assert buttons[1].parent_id == cols[1].id


def test_import_multiple_columns_blocks() -> None:
    code = (
        "import streamlit as st\n"
        "cols = st.columns([1, 1])\n"
        "with cols[0]:\n"
        "    st.button('A', key='a')\n"
        "cols_2 = st.columns([1, 1, 1])\n"
        "with cols_2[2]:\n"
        "    st.button('B', key='b')\n"
    )
    result = import_design_from_code(code)
    assert result.ok
    containers = [w for w in result.design.widgets if w.type == "columns_container"]
    assert len(containers) == 2
    assert containers[0].props["columns"] == 2
    assert containers[1].props["columns"] == 3


def test_import_for_loop_skipped_with_warning() -> None:
    code = (
        "import streamlit as st\n"
        "for i in range(3):\n"
        "    st.button(str(i))\n"
        "st.button('After', key='k')\n"
    )
    result = import_design_from_code(code)
    assert result.ok
    assert any("Dynamic construct" in w.message for w in result.warnings)
    assert [w.type for w in result.design.widgets] == ["button"]


def test_import_oversized_input_rejected() -> None:
    big = "import streamlit as st\n" + ("st.button('x')\n" * 200000)
    result = import_design_from_code(big)
    assert result.design is None
    assert result.errors


def test_import_does_not_execute_code(monkeypatch) -> None:
    """Security: importing must never exec/eval the uploaded source."""
    import builtins

    called = {"exec": False, "eval": False}
    real_exec, real_eval = builtins.exec, builtins.eval

    def fake_exec(*a, **k):  # pragma: no cover - must not be called
        called["exec"] = True
        return real_exec(*a, **k)

    def fake_eval(*a, **k):  # pragma: no cover - must not be called
        called["eval"] = True
        return real_eval(*a, **k)

    monkeypatch.setattr(builtins, "exec", fake_exec)
    monkeypatch.setattr(builtins, "eval", fake_eval)

    dangerous = (
        "import streamlit as st\n"
        "import os\n"
        "os.system('echo pwned')\n"
        "__import__('os').system('echo pwned')\n"
        "st.button('safe', key='k')\n"
    )
    result = import_design_from_code(dangerous)
    assert called["exec"] is False
    assert called["eval"] is False
    # the os.system calls are unknown st? no -> they are not st.* so skipped;
    # the real button is imported.
    assert any(w.type == "button" for w in result.design.widgets)


def test_import_fresh_uuid_when_no_key() -> None:
    # container emits no key -> fresh uuid id is generated
    design = Design(name="D", widgets=[_w("ctr", "container")])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    new_id = result.design.widgets[0].id
    # valid uuid4 string and different from original
    uuid.UUID(new_id)
    assert new_id != "ctr"


# --------------------------------------------------------------------------
# styled-text widgets (wrapped in keyed st.container by codegen)
# --------------------------------------------------------------------------
def test_import_styled_text_widgets_collapse_to_inner_type() -> None:
    for wtype, text_prop in [
        ("markdown", "text"),
        ("title", "text"),
        ("header", "text"),
        ("subheader", "text"),
        ("caption", "text"),
        ("text", "text"),
        ("divider", None),
    ]:
        design = Design(name="D", widgets=[_w("x", wtype)])
        code = generate_streamlit_code(design)
        result = import_design_from_code(code)
        assert result.ok, f"{wtype} failed: {[d.message for d in result.errors]}"
        types = [w.type for w in result.design.widgets]
        # collapsed: exactly the inner widget, no wrapping container
        assert types == [wtype], f"{wtype} -> {types}"


def test_import_user_container_with_text_child_not_collapsed() -> None:
    # A genuine user container (no key) wrapping a styled-text child keeps both.
    design = Design(name="D", widgets=[
        _w("ctr", "container"),
        WidgetInstance(id="m", type="markdown",
                       props=dict(get_widget("markdown").defaults), parent_id="ctr"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert _types_tree(result.design) == [("container", None), ("markdown", "container")]


# --------------------------------------------------------------------------
# colored container background (anchor <div> must not become a widget)
# --------------------------------------------------------------------------
def test_import_colored_container_no_spurious_markdown() -> None:
    design = Design(name="D", widgets=[
        WidgetInstance(id="ctr", type="container",
                       props={**get_widget("container").defaults,
                              "background_color": "#FF0000"}),
        WidgetInstance(id="b", type="button",
                       props=dict(get_widget("button").defaults), parent_id="ctr"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    types = [w.type for w in result.design.widgets]
    # no spurious 'markdown' widget from the anchor <div>
    assert "markdown" not in types
    assert types == ["container", "button"]


# --------------------------------------------------------------------------
# nested structure
# --------------------------------------------------------------------------
def test_import_columns_inside_container() -> None:
    design = Design(name="D", widgets=[
        _w("ctr", "container"),
        WidgetInstance(id="cc", type="columns_container",
                       props={"label": "Columns", "background_color": "#FFFFFF", "columns": 2},
                       parent_id="ctr"),
        WidgetInstance(id="c0", type="column",
                       props={"label": "Column", "background_color": "#FFFFFF", "ratio": 1},
                       parent_id="cc", column_index=0),
        WidgetInstance(id="c1", type="column",
                       props={"label": "Column", "background_color": "#FFFFFF", "ratio": 1},
                       parent_id="cc", column_index=1),
        WidgetInstance(id="b", type="button", props=dict(get_widget("button").defaults),
                       parent_id="c0", column_index=0),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    by_id = {w.id: w for w in result.design.widgets}
    cc = next(w for w in result.design.widgets if w.type == "columns_container")
    assert by_id[cc.parent_id].type == "container"
    btn = next(w for w in result.design.widgets if w.type == "button")
    assert by_id[btn.parent_id].type == "column"


def test_import_deeply_nested_does_not_crash() -> None:
    src = "import streamlit as st\n" + "(" * 200 + "1" + ")" * 200 + "\n"
    result = import_design_from_code(src)
    # Either parses (no widgets) or returns an error - must not raise.
    assert result is not None


# --------------------------------------------------------------------------
# ignored-statement reporting (mixed Streamlit / non-Streamlit files)
# --------------------------------------------------------------------------
def test_import_mixed_file_reports_ignored_statements() -> None:
    code = (
        "import streamlit as st\n"
        "import os\n"
        "x = 1 + 2\n"
        "print('hello')\n"
        "os.system('echo hi')\n"
        "st.button('Real', key='k1')\n"
    )
    result = import_design_from_code(code)
    assert result.ok
    # the real widget is imported
    assert [w.type for w in result.design.widgets] == ["button"]
    # the non-streamlit assignment + two non-st calls are reported as ignored
    messages = " ".join(d.message for d in result.ignored)
    assert len(result.ignored) == 3
    assert "assignment" in messages.lower()
    assert "call" in messages.lower()


def test_import_styling_infos_not_counted_as_ignored() -> None:
    # A styled-text widget emits a <style> markdown -> info, NOT ignored.
    design = Design(name="D", widgets=[_w("m", "markdown")])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert result.ignored == []  # styling info must not count as ignored
    assert [w.type for w in result.design.widgets] == ["markdown"]


def test_import_widget_count_property() -> None:
    design = Design(name="D", widgets=[
        _w("a", "button"),
        _w("b", "checkbox"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert result.widget_count == 2


def test_import_clean_generated_file_has_no_ignored() -> None:
    # A normal generated file should produce zero ignored statements.
    design = Design(name="D", widgets=[
        _w("a", "button"),
        _w("b", "text_input"),
        _w("c", "slider"),
    ])
    code = generate_streamlit_code(design)
    result = import_design_from_code(code)
    assert result.ok
    assert result.ignored == []





