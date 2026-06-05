from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_pdf_registered() -> None:
    definition = get_widget("pdf")
    assert definition is not None
    assert definition.label == "PDF"
    prop_names = [p.name for p in definition.props_schema]
    assert "height" in prop_names
    assert "custom_height" in prop_names
    assert "key" in prop_names


def test_pdf_height_options() -> None:
    definition = get_widget("pdf")
    height_prop = next(p for p in definition.props_schema if p.name == "height")
    assert "custom" in height_prop.options
    assert "stretch" in height_prop.options


def test_codegen_pdf_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="pdf1", type="pdf", props={})],
    )
    code = generate_streamlit_code(design)
    assert "st.pdf(" in code
    assert "# Replace with your data" in code
    assert "height=500" in code
    assert "key='pdf1'" in code


def test_codegen_pdf_stretch_height() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="pdf2", type="pdf", props={"height": "stretch"})],
    )
    code = generate_streamlit_code(design)
    assert "height='stretch'" in code


def test_codegen_pdf_custom_height() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="pdf3", type="pdf", props={"height": "custom", "custom_height": 800})],
    )
    code = generate_streamlit_code(design)
    assert "height=800" in code


def test_codegen_pdf_invalid_custom_height_defaults_to_500() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="pdf4", type="pdf", props={"height": "custom", "custom_height": -1})],
    )
    code = generate_streamlit_code(design)
    assert "height=500" in code


def test_codegen_pdf_comment_present() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="pdf5", type="pdf", props={})],
    )
    code = generate_streamlit_code(design)
    assert "# Replace with your data" in code

