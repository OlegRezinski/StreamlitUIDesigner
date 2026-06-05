from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_video_registered() -> None:
    definition = get_widget("video")
    assert definition is not None
    assert definition.label == "Video"
    prop_names = [p.name for p in definition.props_schema]
    assert "data" not in prop_names  # data is hidden from properties pane
    assert "format" not in prop_names  # format is hidden from properties pane
    assert "loop" in prop_names
    assert "autoplay" in prop_names
    assert "muted" in prop_names
    assert "width" in prop_names
    assert "key" in prop_names


def test_video_width_options() -> None:
    definition = get_widget("video")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


def test_codegen_video_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="vid1", type="video", props={})],
    )
    code = generate_streamlit_code(design)
    assert "st.video(" in code
    assert "# Replace with your video data" in code
    assert "format='video/mp4'" in code
    assert "width='stretch'" in code
    assert "key='vid1'" in code


def test_codegen_video_no_start_time_if_zero() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="vid2", type="video", props={"start_time": 0})],
    )
    code = generate_streamlit_code(design)
    assert "start_time" not in code


def test_codegen_video_start_time_nonzero() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="vid3", type="video", props={"start_time": 30})],
    )
    code = generate_streamlit_code(design)
    assert "start_time=30" in code


def test_codegen_video_loop_true() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="vid4", type="video", props={"loop": True})],
    )
    code = generate_streamlit_code(design)
    assert "loop=True" in code


def test_codegen_video_loop_false_omitted() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="vid5", type="video", props={"loop": False})],
    )
    code = generate_streamlit_code(design)
    assert "loop" not in code


def test_codegen_video_autoplay_muted() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="vid6", type="video", props={"autoplay": True, "muted": True})],
    )
    code = generate_streamlit_code(design)
    assert "autoplay=True" in code
    assert "muted=True" in code


def test_codegen_video_custom_width() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="vid7", type="video", props={"width": "custom", "custom_width": 600})],
    )
    code = generate_streamlit_code(design)
    assert "width=600" in code


def test_codegen_video_comment_present() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="vid8", type="video", props={})],
    )
    code = generate_streamlit_code(design)
    assert "# Replace with your video data" in code

