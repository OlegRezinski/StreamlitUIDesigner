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


def test_audio_input_registered():
    defn = get_widget("audio_input")
    assert defn is not None
    assert defn.label == "Audio input"


def test_audio_input_codegen_basic():
    wi = _wi("audio_input", {"label": "Record voice", "sample_rate": "16000", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "st.audio_input(" in code
    assert "'Record voice'" in code
    assert f"audio_input_{wi.id[:8]}" in code


def test_audio_input_codegen_sample_rate_default_not_emitted():
    wi = _wi("audio_input", {"label": "R", "sample_rate": "16000", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "sample_rate" not in code


def test_audio_input_codegen_sample_rate_custom():
    wi = _wi("audio_input", {"label": "R", "sample_rate": "48000", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "sample_rate=48000" in code


def test_audio_input_codegen_sample_rate_none():
    wi = _wi("audio_input", {"label": "R", "sample_rate": "None", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "sample_rate=None" in code


def test_audio_input_codegen_help():
    wi = _wi("audio_input", {"label": "R", "help": "Speak now", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "help='Speak now'" in code


def test_audio_input_codegen_disabled():
    wi = _wi("audio_input", {"label": "R", "disabled": True, "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "disabled=True" in code


def test_audio_input_codegen_label_visibility():
    wi = _wi("audio_input", {"label": "R", "label_visibility": "collapsed", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "label_visibility='collapsed'" in code


def test_audio_input_codegen_custom_width():
    wi = _wi("audio_input", {"label": "R", "width": "custom", "custom_width": 400})
    d = _make_design(wi)
    code = generate_code(d)
    assert "width=400" in code


def test_audio_input_codegen_stretch_width():
    wi = _wi("audio_input", {"label": "R", "width": "stretch"})
    d = _make_design(wi)
    code = generate_code(d)
    assert "width='stretch'" in code

