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


def test_camera_input_registered():
    defn = get_widget("camera_input")
    assert defn is not None
    assert defn.label == "Camera input"


def test_camera_input_codegen_basic():
    wi = _wi("camera_input", {"label": "Take a photo", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "st.camera_input(" in code
    assert "'Take a photo'" in code
    assert f"camera_input_{wi.id[:8]}" in code


def test_camera_input_codegen_key_always_generated():
    wi = _wi("camera_input", {"label": "Snap", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "key=" in code


def test_camera_input_codegen_custom_key():
    wi = _wi("camera_input", {"label": "Snap", "key": "my_cam", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "key='my_cam'" in code


def test_camera_input_codegen_help():
    wi = _wi("camera_input", {"label": "Snap", "help": "Smile!", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "help='Smile!'" in code


def test_camera_input_codegen_no_help_when_empty():
    wi = _wi("camera_input", {"label": "Snap", "help": "", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "help=" not in code


def test_camera_input_codegen_disabled():
    wi = _wi("camera_input", {"label": "Snap", "disabled": True, "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "disabled=True" in code


def test_camera_input_codegen_label_visibility():
    wi = _wi("camera_input", {"label": "Snap", "label_visibility": "hidden", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "label_visibility='hidden'" in code


def test_camera_input_codegen_custom_width():
    wi = _wi("camera_input", {"label": "Snap", "width": "custom", "custom_width": 500})
    d = _make_design(wi)
    code = generate_code(d)
    assert "width=500" in code


def test_camera_input_codegen_stretch_width():
    wi = _wi("camera_input", {"label": "Snap", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "width='stretch'" in code

