from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_pills_registered() -> None:
    definition = get_widget("pills")
    assert definition is not None
    assert definition.label == "Pills"
    prop_names = [p.name for p in definition.props_schema]
    assert "label" in prop_names
    assert "options" in prop_names
    assert "selection_mode" in prop_names
    assert "disabled" in prop_names
    assert "label_visibility" in prop_names


def test_pills_selection_mode_options() -> None:
    definition = get_widget("pills")
    sm_prop = next(p for p in definition.props_schema if p.name == "selection_mode")
    assert "single" in sm_prop.options
    assert "multi" in sm_prop.options


def test_pills_label_visibility_options() -> None:
    definition = get_widget("pills")
    lv_prop = next(p for p in definition.props_schema if p.name == "label_visibility")
    assert "visible" in lv_prop.options
    assert "hidden" in lv_prop.options
    assert "collapsed" in lv_prop.options


def test_codegen_pills_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="p1",
                type="pills",
                props={
                    "label": "Pills",
                    "options": "Option 1, Option 2, Option 3",
                    "selection_mode": "single",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.pills(" in code
    assert "'Pills'" in code
    assert "selection_mode='single'" in code
    assert "key='p1'" in code
    assert "default=None" in code
    assert "disabled=False" in code
    assert "label_visibility='visible'" in code


def test_codegen_pills_multi_selection() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="p2",
                type="pills",
                props={
                    "label": "Choose",
                    "options": "A, B, C",
                    "selection_mode": "multi",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "selection_mode='multi'" in code
    assert "['A', 'B', 'C']" in code


def test_codegen_pills_disabled() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="p3",
                type="pills",
                props={
                    "label": "Pills",
                    "options": "X, Y",
                    "selection_mode": "single",
                    "disabled": True,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "disabled=True" in code


def test_codegen_pills_with_help() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="p4",
                type="pills",
                props={
                    "label": "Pills",
                    "options": "A, B",
                    "selection_mode": "single",
                    "disabled": False,
                    "help": "Pick one",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "help='Pick one'" in code


def test_codegen_pills_no_help_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="p5",
                type="pills",
                props={
                    "label": "Pills",
                    "options": "A, B",
                    "selection_mode": "single",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "help=" not in code


def test_codegen_pills_label_visibility_hidden() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="p6",
                type="pills",
                props={
                    "label": "Pills",
                    "options": "A, B",
                    "selection_mode": "single",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "hidden",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "label_visibility='hidden'" in code


def test_pills_default_not_in_schema() -> None:
    """default should be generated in code, not exposed as a property pane field."""
    definition = get_widget("pills")
    prop_names = [p.name for p in definition.props_schema]
    assert "default" not in prop_names
    assert "default" not in definition.defaults

