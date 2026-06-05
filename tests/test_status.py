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


def test_status_registered():
    defn = get_widget("status")
    assert defn is not None
    assert defn.label == "Status"
    assert any(p.name == "label" for p in defn.props_schema)
    assert any(p.name == "state" for p in defn.props_schema)
    assert any(p.name == "expanded" for p in defn.props_schema)


def test_codegen_status_no_children():
    d = _make_design(_wi("status", {"label": "Loading", "width": "stretch"}))
    code = generate_code(d)
    assert "with st.status(" in code
    assert "pass" in code


def test_codegen_status_label_comment():
    d = _make_design(_wi("status", {"label": "My Status", "width": "stretch"}))
    code = generate_code(d)
    assert "# My Status" in code


def test_codegen_status_with_child():
    parent = _wi("status", {"label": "S", "width": "stretch"})
    child = _wi("text", {"text": "Hello"}, parent_id=parent.id)
    d = _make_design(parent, child)
    code = generate_code(d)
    assert "with st.status(" in code
    assert "Hello" in code


def test_codegen_status_no_pass_with_children():
    parent = _wi("status", {"label": "S", "width": "stretch"})
    child = _wi("text", {"text": "Hello"}, parent_id=parent.id)
    d = _make_design(parent, child)
    code = generate_code(d)
    # pass should NOT appear when children are present
    lines = code.split("\n")
    status_block = False
    for line in lines:
        if "with st.status(" in line:
            status_block = True
            continue
        if status_block:
            assert "pass" not in line or "pass" not in line.strip()
            break


def test_codegen_status_expanded():
    d = _make_design(_wi("status", {"label": "S", "expanded": True, "width": "stretch"}))
    code = generate_code(d)
    assert "expanded=True" in code


def test_codegen_status_state_complete():
    d = _make_design(_wi("status", {"label": "S", "state": "complete", "width": "stretch"}))
    code = generate_code(d)
    assert "state='complete'" in code


def test_codegen_status_state_error():
    d = _make_design(_wi("status", {"label": "S", "state": "error", "width": "stretch"}))
    code = generate_code(d)
    assert "state='error'" in code


def test_codegen_status_state_running_not_emitted():
    d = _make_design(_wi("status", {"label": "S", "state": "running", "width": "stretch"}))
    code = generate_code(d)
    assert "state=" not in code


def test_codegen_status_custom_width():
    d = _make_design(_wi("status", {"label": "S", "width": "custom", "custom_width": 500}))
    code = generate_code(d)
    assert "width=500" in code

