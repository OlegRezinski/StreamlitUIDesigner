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


def test_spinner_registered():
    defn = get_widget("spinner")
    assert defn is not None
    assert defn.label == "Spinner"
    assert any(p.name == "text" for p in defn.props_schema)
    assert any(p.name == "show_time" for p in defn.props_schema)
    assert any(p.name == "width" for p in defn.props_schema)
    assert any(p.name == "custom_width" for p in defn.props_schema)


def test_spinner_defaults():
    defn = get_widget("spinner")
    assert defn.defaults == {
        "text": "In progress...",
        "show_time": False,
        "width": "content",
        "custom_width": 320,
    }


def test_spinner_width_options():
    defn = get_widget("spinner")
    width_prop = next(p for p in defn.props_schema if p.name == "width")
    assert "content" in width_prop.options
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


def test_codegen_spinner_no_children():
    d = _make_design(_wi("spinner", {"text": "Loading", "width": "content"}))
    code = generate_code(d)
    assert "with st.spinner(" in code
    assert "pass" in code


def test_codegen_spinner_comment():
    d = _make_design(_wi("spinner", {"text": "Loading", "width": "content"}))
    code = generate_code(d)
    assert "# Spinner" in code


def test_codegen_spinner_text():
    d = _make_design(_wi("spinner", {"text": "Please wait...", "width": "content"}))
    code = generate_code(d)
    assert "'Please wait...'" in code


def test_codegen_spinner_default_text():
    d = _make_design(_wi("spinner", {"text": "In progress...", "width": "content"}))
    code = generate_code(d)
    assert "'In progress...'" in code


def test_codegen_spinner_show_time_true():
    d = _make_design(_wi("spinner", {"text": "Loading", "show_time": True, "width": "content"}))
    code = generate_code(d)
    assert "show_time=True" in code


def test_codegen_spinner_show_time_false_not_emitted():
    d = _make_design(_wi("spinner", {"text": "Loading", "show_time": False, "width": "content"}))
    code = generate_code(d)
    assert "show_time" not in code


def test_codegen_spinner_width_content_not_emitted():
    d = _make_design(_wi("spinner", {"text": "Loading", "width": "content"}))
    code = generate_code(d)
    assert "width=" not in code


def test_codegen_spinner_width_stretch():
    d = _make_design(_wi("spinner", {"text": "Loading", "width": "stretch"}))
    code = generate_code(d)
    assert "width='stretch'" in code


def test_codegen_spinner_custom_width():
    d = _make_design(_wi("spinner", {"text": "Loading", "width": "custom", "custom_width": 500}))
    code = generate_code(d)
    assert "width=500" in code


def test_codegen_spinner_with_child():
    parent = _wi("spinner", {"text": "Loading", "width": "content"})
    child = _wi("text", {"text": "Hello"}, parent_id=parent.id)
    d = _make_design(parent, child)
    code = generate_code(d)
    assert "with st.spinner(" in code
    assert "Hello" in code


def test_codegen_spinner_no_pass_with_children():
    parent = _wi("spinner", {"text": "Loading", "width": "content"})
    child = _wi("text", {"text": "Hello"}, parent_id=parent.id)
    d = _make_design(parent, child)
    code = generate_code(d)
    # pass should NOT appear when children are present
    lines = code.split("\n")
    spinner_block = False
    for line in lines:
        if "with st.spinner(" in line:
            spinner_block = True
            continue
        if spinner_block:
            assert "pass" not in line.strip()
            break


def test_codegen_spinner_all_options():
    d = _make_design(_wi("spinner", {
        "text": "Wait...",
        "show_time": True,
        "width": "custom",
        "custom_width": 400,
    }))
    code = generate_code(d)
    assert "'Wait...'" in code
    assert "show_time=True" in code
    assert "width=400" in code

