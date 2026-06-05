from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_audio_registered() -> None:
    definition = get_widget("audio")
    assert definition is not None
    assert definition.label == "Audio"
    prop_names = [p.name for p in definition.props_schema]
    assert "format" in prop_names
    assert "start_time" in prop_names
    assert "loop" in prop_names
    assert "autoplay" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_audio_format_options() -> None:
    definition = get_widget("audio")
    fmt_prop = next(p for p in definition.props_schema if p.name == "format")
    assert "audio/wav" in fmt_prop.options
    assert "audio/mp3" in fmt_prop.options
    assert "audio/ogg" in fmt_prop.options


def test_audio_width_options() -> None:
    definition = get_widget("audio")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


def test_codegen_audio_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="a1",
                type="audio",
                props={},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.audio(" in code
    assert "format='audio/wav'" in code
    assert "start_time=0" in code
    assert "loop=False" in code
    assert "autoplay=False" in code
    assert "width='stretch'" in code
    assert "end_time=None" in code


def test_codegen_audio_loop_autoplay() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="a2",
                type="audio",
                props={"loop": True, "autoplay": True},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "loop=True" in code
    assert "autoplay=True" in code


def test_codegen_audio_custom_format() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="a3",
                type="audio",
                props={"format": "audio/mp3"},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "format='audio/mp3'" in code


def test_codegen_audio_start_time() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="a4",
                type="audio",
                props={"start_time": 30},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "start_time=30" in code


def test_codegen_audio_width_custom() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="a5",
                type="audio",
                props={"width": "custom", "custom_width": 400},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width=400" in code


def test_codegen_audio_width_stretch() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="a6",
                type="audio",
                props={"width": "stretch"},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width='stretch'" in code


def test_codegen_audio_sample_url() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="a7",
                type="audio",
                props={},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "soundhelix" in code

