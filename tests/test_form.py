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


def test_form_registered():
    defn = get_widget("form")
    assert defn is not None
    assert defn.label == "Form"


def test_form_codegen_no_children():
    d = _make_design(_wi("form", {"label": "My Form", "key": "my_form", "width": "stretch", "height": "content"}))
    code = generate_code(d)
    assert "with st.form(" in code
    assert "My Form" in code
    assert "st.form_submit_button('Submit')" in code


def test_form_codegen_label_comment():
    d = _make_design(_wi("form", {"label": "Login", "key": "login_form", "width": "stretch", "height": "content"}))
    code = generate_code(d)
    assert "# Login" in code


def test_form_codegen_auto_key():
    wi = _wi("form", {"label": "F", "key": "", "width": "stretch", "height": "content"})
    d = _make_design(wi)
    code = generate_code(d)
    assert f"form_{wi.id[:8]}" in code


def test_form_codegen_clear_on_submit():
    d = _make_design(_wi("form", {"label": "F", "key": "f", "clear_on_submit": True, "width": "stretch", "height": "content"}))
    code = generate_code(d)
    assert "clear_on_submit=True" in code


def test_form_codegen_clear_on_submit_false_not_emitted():
    d = _make_design(_wi("form", {"label": "F", "key": "f", "clear_on_submit": False, "width": "stretch", "height": "content"}))
    code = generate_code(d)
    assert "clear_on_submit" not in code


def test_form_codegen_enter_to_submit_false():
    d = _make_design(_wi("form", {"label": "F", "key": "f", "enter_to_submit": False, "width": "stretch", "height": "content"}))
    code = generate_code(d)
    assert "enter_to_submit=False" in code


def test_form_codegen_border_false():
    d = _make_design(_wi("form", {"label": "F", "key": "f", "border": False, "width": "stretch", "height": "content"}))
    code = generate_code(d)
    assert "border=False" in code


def test_form_codegen_custom_width():
    d = _make_design(_wi("form", {"label": "F", "key": "f", "width": "custom", "custom_width": 500, "height": "content"}))
    code = generate_code(d)
    assert "width=500" in code


def test_form_codegen_custom_height():
    d = _make_design(_wi("form", {"label": "F", "key": "f", "width": "stretch", "height": "custom", "custom_height": 400}))
    code = generate_code(d)
    assert "height=400" in code


def test_form_codegen_with_child():
    form = _wi("form", {"label": "F", "key": "f", "width": "stretch", "height": "content"})
    child = _wi("text", {"body": "Hello"}, parent_id=form.id)
    d = _make_design(form, child)
    code = generate_code(d)
    assert "with st.form(" in code
    assert "st.form_submit_button('Submit')" in code


def test_form_codegen_submit_button_always_present():
    form = _wi("form", {"label": "F", "key": "f", "width": "stretch", "height": "content"})
    d = _make_design(form)
    code = generate_code(d)
    assert "st.form_submit_button('Submit')" in code

