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


def test_sidebar_registered():
    defn = get_widget("sidebar")
    assert defn is not None
    assert defn.label == "Sidebar"


def test_sidebar_codegen_no_children():
    d = _make_design(_wi("sidebar", {"label": "Sidebar"}))
    code = generate_code(d)
    assert "with st.sidebar:" in code
    assert "pass" in code
    # No parentheses!
    assert "st.sidebar()" not in code


def test_sidebar_codegen_label_comment():
    d = _make_design(_wi("sidebar", {"label": "Navigation"}))
    code = generate_code(d)
    assert "# Navigation" in code


def test_sidebar_codegen_with_child():
    sb = _wi("sidebar", {"label": "Sidebar"})
    child = _wi("text", {"body": "Hello"}, parent_id=sb.id)
    d = _make_design(sb, child)
    code = generate_code(d)
    assert "with st.sidebar:" in code
    assert "pass" not in code


def test_sidebar_codegen_no_pass_with_children():
    sb = _wi("sidebar", {"label": "Sidebar"})
    child = _wi("text", {"body": "Hello"}, parent_id=sb.id)
    d = _make_design(sb, child)
    code = generate_code(d)
    assert "pass" not in code


def test_sidebar_no_parentheses():
    d = _make_design(_wi("sidebar", {"label": "S"}))
    code = generate_code(d)
    assert "with st.sidebar:" in code
    assert "sidebar(" not in code


