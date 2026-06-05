import pytest
from designer.models import Design, WidgetInstance
from designer.codegen import generate_streamlit_code as generate_code
from designer.registry import get_widget, clear_registry
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def _make_design(*widgets):
    return Design(name="test", widgets=list(widgets))


import uuid


def _wi(type_, props=None, parent_id=None):
    return WidgetInstance(id=str(uuid.uuid4()), type=type_, props=props or {}, parent_id=parent_id)


def test_expander_registered():
    defn = get_widget("expander")
    assert defn is not None


def test_expander_default_codegen():
    d = _make_design(_wi("expander", {"label": "My Expander", "width": "stretch"}))
    code = generate_code(d)
    assert "with st.expander(" in code
    assert "My Expander" in code


def test_expander_expanded_true():
    d = _make_design(_wi("expander", {"label": "E", "expanded": True, "width": "stretch"}))
    code = generate_code(d)
    assert "expanded=True" in code


def test_expander_expanded_false_not_emitted():
    d = _make_design(_wi("expander", {"label": "E", "expanded": False, "width": "stretch"}))
    code = generate_code(d)
    assert "expanded=True" not in code


def test_expander_icon():
    d = _make_design(_wi("expander", {"label": "E", "icon": ":material/star:", "width": "stretch"}))
    code = generate_code(d)
    assert "icon=':material/star:'" in code


def test_expander_no_icon_when_empty():
    d = _make_design(_wi("expander", {"label": "E", "icon": "", "width": "stretch"}))
    code = generate_code(d)
    assert "icon=" not in code


def test_expander_custom_width():
    d = _make_design(_wi("expander", {"label": "E", "width": "custom", "custom_width": 500}))
    code = generate_code(d)
    assert "width=500" in code


def test_expander_stretch_width():
    d = _make_design(_wi("expander", {"label": "E", "width": "stretch"}))
    code = generate_code(d)
    assert "width='stretch'" in code


def test_expander_with_child():
    exp = _wi("expander", {"label": "E", "width": "stretch"})
    child = _wi("text", {"body": "Hello"}, parent_id=exp.id)
    d = _make_design(exp, child)
    code = generate_code(d)
    assert "with st.expander(" in code
    assert "st.markdown" in code or "st.text" in code or "Hello" in code


def test_expander_empty_body():
    d = _make_design(_wi("expander", {"label": "E", "width": "stretch"}))
    code = generate_code(d)
    assert "pass" in code




