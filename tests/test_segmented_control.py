from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_segmented_control_registered() -> None:
    definition = get_widget("segmented_control")
    assert definition is not None
    assert definition.label == "Segmented control"
    prop_names = [p.name for p in definition.props_schema]
    assert "label" in prop_names
    assert "options" in prop_names
    assert "selection_mode" in prop_names
    assert "disabled" in prop_names
    assert "label_visibility" in prop_names


def test_segmented_control_selection_mode_options() -> None:
    definition = get_widget("segmented_control")
    sm_prop = next(p for p in definition.props_schema if p.name == "selection_mode")
    assert "single" in sm_prop.options
    assert "multi" in sm_prop.options


def test_segmented_control_label_visibility_options() -> None:
    definition = get_widget("segmented_control")
    lv_prop = next(p for p in definition.props_schema if p.name == "label_visibility")
    assert "visible" in lv_prop.options
    assert "hidden" in lv_prop.options
    assert "collapsed" in lv_prop.options


def test_segmented_control_width_options() -> None:
    definition = get_widget("segmented_control")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "content" in width_prop.options
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


def test_segmented_control_default_not_in_schema() -> None:
    """default should be generated in code, not exposed as a property pane field."""
    definition = get_widget("segmented_control")
    prop_names = [p.name for p in definition.props_schema]
    assert "default" not in prop_names
    assert "default" not in definition.defaults


def test_codegen_segmented_control_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="sc1",
                type="segmented_control",
                props={
                    "label": "Segmented control",
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
    assert "st.segmented_control(" in code
    assert "'Segmented control'" in code
    assert "selection_mode='single'" in code
    assert "key='sc1'" in code
    assert "default=None" in code
    assert "disabled=False" in code
    assert "label_visibility='visible'" in code


def test_codegen_segmented_control_multi_selection() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="sc2",
                type="segmented_control",
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


def test_codegen_segmented_control_disabled() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="sc3",
                type="segmented_control",
                props={
                    "label": "Segmented control",
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


def test_codegen_segmented_control_with_help() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="sc4",
                type="segmented_control",
                props={
                    "label": "Segmented control",
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


def test_codegen_segmented_control_no_help_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="sc5",
                type="segmented_control",
                props={
                    "label": "Segmented control",
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


def test_codegen_segmented_control_label_visibility_hidden() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="sc6",
                type="segmented_control",
                props={
                    "label": "Segmented control",
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


def test_codegen_segmented_control_width_stretch() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="sc7",
                type="segmented_control",
                props={
                    "label": "Segmented control",
                    "options": "A, B",
                    "selection_mode": "single",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width='stretch'" in code


def test_codegen_segmented_control_width_custom() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="sc8",
                type="segmented_control",
                props={
                    "label": "Segmented control",
                    "options": "A, B",
                    "selection_mode": "single",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                    "width": "custom",
                    "custom_width": 400,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width=400" in code

