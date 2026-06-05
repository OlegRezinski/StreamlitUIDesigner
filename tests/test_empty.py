from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_empty_registered() -> None:
    definition = get_widget("empty")
    assert definition is not None
    assert definition.label == "Empty"


def test_codegen_empty_no_children() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="e1", type="empty", props={})],
    )
    code = generate_streamlit_code(design)
    assert "with st.empty():" in code
    assert "# Add elements here; each will replace the previous one" in code


def test_codegen_empty_label_comment() -> None:
    design = Design(
        name="Test",
        widgets=[WidgetInstance(id="e2", type="empty", props={"label": "My Empty"})],
    )
    code = generate_streamlit_code(design)
    assert "# My Empty" in code
    assert "with st.empty():" in code


def test_codegen_empty_with_child() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(id="e3", type="empty", props={}),
            WidgetInstance(id="t1", type="title", props={"text": "Hello"}, parent_id="e3"),
        ],
    )
    code = generate_streamlit_code(design)
    assert "with st.empty():" in code
    assert "st.title" in code
    # child should be indented inside the empty block
    lines = code.splitlines()
    empty_idx = next(i for i, l in enumerate(lines) if "with st.empty():" in l)
    child_line = next((l for l in lines[empty_idx + 1:] if "st.title" in l), None)
    assert child_line is not None
    assert child_line.startswith("    ")


def test_codegen_empty_no_pass_with_children() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(id="e4", type="empty", props={}),
            WidgetInstance(id="t2", type="title", props={"text": "Hi"}, parent_id="e4"),
        ],
    )
    code = generate_streamlit_code(design)
    assert "pass" not in code

