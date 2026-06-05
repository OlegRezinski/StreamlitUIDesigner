from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_logo_registered() -> None:
    definition = get_widget("logo")
    assert definition is not None
    assert definition.label == "Logo"
    prop_names = [p.name for p in definition.props_schema]
    assert "image" in prop_names
    assert "size" in prop_names
    assert "icon_image" in prop_names


def test_logo_size_options() -> None:
    definition = get_widget("logo")
    size_prop = next(p for p in definition.props_schema if p.name == "size")
    assert "small" in size_prop.options
    assert "medium" in size_prop.options
    assert "large" in size_prop.options


def test_codegen_logo_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="logo1", type="logo", props={})],
    )
    code = generate_streamlit_code(design)
    assert "st.logo(" in code
    assert "img_placeholder.jpg" in code
    assert "size='medium'" in code
    assert "icon_image=None" in code


def test_codegen_logo_custom_image() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="logo2", type="logo", props={"image": "https://example.com/logo.png"})],
    )
    code = generate_streamlit_code(design)
    assert "https://example.com/logo.png" in code


def test_codegen_logo_size_small() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="logo3", type="logo", props={"size": "small"})],
    )
    code = generate_streamlit_code(design)
    assert "size='small'" in code


def test_codegen_logo_size_large() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="logo4", type="logo", props={"size": "large"})],
    )
    code = generate_streamlit_code(design)
    assert "size='large'" in code


def test_codegen_logo_with_icon_image() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="logo5", type="logo", props={"icon_image": "https://example.com/icon.png"})],
    )
    code = generate_streamlit_code(design)
    assert "icon_image='https://example.com/icon.png'" in code


def test_codegen_logo_empty_icon_image() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="logo6", type="logo", props={"icon_image": ""})],
    )
    code = generate_streamlit_code(design)
    assert "icon_image=None" in code


def test_codegen_logo_material_icon() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="logo7", type="logo", props={"image": ":material/home:"})],
    )
    code = generate_streamlit_code(design)
    assert ":material/home:" in code


def test_codegen_logo_emoji() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="logo8", type="logo", props={"image": "\U0001f3e0"})],
    )
    code = generate_streamlit_code(design)
    assert "\U0001f3e0" in code

