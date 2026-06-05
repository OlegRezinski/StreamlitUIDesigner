import pytest
import uuid
from designer.models import Design, WidgetInstance
from designer.codegen import generate_streamlit_code as generate_code
from designer.registry import get_widget, clear_registry
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def _make_design(*widgets):
    return Design(name="test", widgets=list(widgets))


def _wi(type_, props=None, parent_id=None):
    return WidgetInstance(id=str(uuid.uuid4()), type=type_, props=props or {}, parent_id=parent_id)


def test_popover_registered():
    defn = get_widget("popover")
    assert defn is not None
    assert defn.label == "Popover"


def test_popover_codegen_basic():
    d = _make_design(_wi("popover", {"label": "Open", "width": "content"}))
    code = generate_code(d)
    assert "with st.popover(" in code
    assert "'Open'" in code


def test_popover_codegen_label_comment():
    d = _make_design(_wi("popover", {"label": "My Menu", "width": "content"}))
    code = generate_code(d)
    assert "# My Menu" in code


def test_popover_codegen_type_primary():
    d = _make_design(_wi("popover", {"label": "P", "type": "primary", "width": "content"}))
    code = generate_code(d)
    assert "type='primary'" in code


def test_popover_codegen_type_secondary_not_emitted():
    d = _make_design(_wi("popover", {"label": "P", "type": "secondary", "width": "content"}))
    code = generate_code(d)
    assert "type=" not in code


def test_popover_codegen_help():
    d = _make_design(_wi("popover", {"label": "P", "help": "Click me", "width": "content"}))
    code = generate_code(d)
    assert "help='Click me'" in code


def test_popover_codegen_icon():
    d = _make_design(_wi("popover", {"label": "P", "icon": ":material/star:", "width": "content"}))
    code = generate_code(d)
    assert "icon=':material/star:'" in code


def test_popover_codegen_disabled():
    d = _make_design(_wi("popover", {"label": "P", "disabled": True, "width": "content"}))
    code = generate_code(d)
    assert "disabled=True" in code


def test_popover_codegen_custom_width():
    d = _make_design(_wi("popover", {"label": "P", "width": "custom", "custom_width": 450}))
    code = generate_code(d)
    assert "width=450" in code


def test_popover_codegen_stretch_width():
    d = _make_design(_wi("popover", {"label": "P", "width": "stretch"}))
    code = generate_code(d)
    assert "width='stretch'" in code


def test_popover_codegen_on_change_rerun():
    wi = _wi("popover", {"label": "P", "width": "content", "on_change": "rerun", "key": ""})
    d = _make_design(wi)
    code = generate_code(d)
    assert "on_change=st.rerun" in code
    assert f"popover_{wi.id[:8]}" in code


def test_popover_codegen_no_children():
    d = _make_design(_wi("popover", {"label": "P", "width": "content"}))
    code = generate_code(d)
    assert "pass" in code


def test_popover_codegen_with_child():
    pop = _wi("popover", {"label": "P", "width": "content"})
    child = _wi("text", {"body": "Hello"}, parent_id=pop.id)
    d = _make_design(pop, child)
    code = generate_code(d)
    assert "with st.popover(" in code
    assert "pass" not in code

