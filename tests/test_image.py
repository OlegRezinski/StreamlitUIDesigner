from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_image_registered() -> None:
    definition = get_widget("image")
    assert definition is not None
    assert definition.label == "Image"
    prop_names = [p.name for p in definition.props_schema]
    assert "image" in prop_names
    assert "caption" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names
    assert "output_format" in prop_names
    assert "link" not in prop_names


def test_image_width_options() -> None:
    definition = get_widget("image")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "content" in width_prop.options
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


def test_image_output_format_options() -> None:
    definition = get_widget("image")
    fmt_prop = next(p for p in definition.props_schema if p.name == "output_format")
    assert "auto" in fmt_prop.options
    assert "JPEG" in fmt_prop.options
    assert "PNG" in fmt_prop.options


def test_codegen_image_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img1",
                type="image",
                props={},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.image(" in code
    assert "img_placeholder.jpg" in code
    assert "caption=None" in code
    assert "width='content'" in code
    assert "output_format='auto'" in code
    assert "link=" not in code


def test_codegen_image_with_caption() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img2",
                type="image",
                props={"caption": "A beautiful sunset"},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "caption='A beautiful sunset'" in code


def test_codegen_image_no_caption_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img3",
                type="image",
                props={"caption": ""},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "caption=None" in code


def test_codegen_image_width_stretch() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img4",
                type="image",
                props={"width": "stretch"},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width='stretch'" in code


def test_codegen_image_width_custom() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img5",
                type="image",
                props={"width": "custom", "custom_width": 500},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width=500" in code


def test_codegen_image_output_format_jpeg() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img6",
                type="image",
                props={"output_format": "JPEG"},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "output_format='JPEG'" in code


def test_codegen_image_link_prop_ignored() -> None:
    """link prop is not generated (not supported in current Streamlit version)."""
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img7",
                type="image",
                props={"link": "https://streamlit.io"},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "link=" not in code


def test_codegen_image_no_link_in_output() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img8",
                type="image",
                props={"link": ""},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "link=" not in code


def test_codegen_image_custom_url() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="img9",
                type="image",
                props={"image": "https://example.com/photo.jpg"},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "https://example.com/photo.jpg" in code

