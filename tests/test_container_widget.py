from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_container_registered() -> None:
    defn = get_widget("container")
    assert defn is not None
    assert defn.label == "Container"
    names = [p.name for p in defn.props_schema]
    assert "border" in names
    assert "width" in names
    assert "height" in names
    assert "horizontal" in names
    assert "gap" in names
    assert "background_color" in names


def test_codegen_container_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c1", type="container", props={})],
    )
    code = generate_streamlit_code(design)
    assert "with st.container(" in code
    assert "width='stretch'" in code
    assert "height='content'" in code
    assert "pass" in code


def test_codegen_container_label_comment() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c2", type="container", props={"label": "My Box"})],
    )
    code = generate_streamlit_code(design)
    assert "# My Box" in code


def test_codegen_container_border_true() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c3", type="container", props={"border": "True"})],
    )
    code = generate_streamlit_code(design)
    assert "border=True" in code


def test_codegen_container_border_none_not_generated() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c4", type="container", props={"border": "None"})],
    )
    code = generate_streamlit_code(design)
    assert "border=" not in code


def test_codegen_container_custom_width() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c5", type="container", props={"width": "custom", "custom_width": 400})],
    )
    code = generate_streamlit_code(design)
    assert "width=400" in code


def test_codegen_container_custom_height() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c6", type="container", props={"height": "custom", "custom_height": 250})],
    )
    code = generate_streamlit_code(design)
    assert "height=250" in code


def test_codegen_container_horizontal_true() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c7", type="container", props={"horizontal": True})],
    )
    code = generate_streamlit_code(design)
    assert "horizontal=True" in code


def test_codegen_container_horizontal_false_omitted() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c8", type="container", props={"horizontal": False})],
    )
    code = generate_streamlit_code(design)
    assert "horizontal" not in code


def test_codegen_container_gap_not_default_generated() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c9", type="container", props={"gap": "large"})],
    )
    code = generate_streamlit_code(design)
    assert "gap='large'" in code


def test_codegen_container_gap_none() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c10", type="container", props={"gap": "None"})],
    )
    code = generate_streamlit_code(design)
    assert "gap=None" in code


def test_codegen_container_gap_small_omitted() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="c11", type="container", props={"gap": "small"})],
    )
    code = generate_streamlit_code(design)
    assert "gap=" not in code


def test_codegen_container_with_child() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(id="c12", type="container", props={}),
            WidgetInstance(id="t1", type="title", props={"text": "Hello"}, parent_id="c12"),
        ],
    )
    code = generate_streamlit_code(design)
    assert "with st.container(" in code
    assert "st.title" in code
    assert "pass" not in code


def test_codegen_container_no_pass_with_children() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(id="c13", type="container", props={}),
            WidgetInstance(id="t2", type="title", props={"text": "Hi"}, parent_id="c13"),
        ],
    )
    code = generate_streamlit_code(design)
    assert "pass" not in code

