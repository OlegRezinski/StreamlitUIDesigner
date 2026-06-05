from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_time_input_registered() -> None:
    definition = get_widget("time_input")
    assert definition is not None
    assert definition.label == "Time input"
    prop_names = [p.name for p in definition.props_schema]
    assert "label" in prop_names
    assert "value" in prop_names
    assert "step" in prop_names
    assert "disabled" in prop_names
    assert "help" in prop_names
    assert "label_visibility" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_time_input_width_options() -> None:
    definition = get_widget("time_input")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options
    assert "content" not in width_prop.options


def test_time_input_label_visibility_options() -> None:
    definition = get_widget("time_input")
    lv_prop = next(p for p in definition.props_schema if p.name == "label_visibility")
    assert "visible" in lv_prop.options
    assert "hidden" in lv_prop.options
    assert "collapsed" in lv_prop.options


def test_codegen_time_input_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti1",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "now",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.time_input(" in code
    assert "'Time input'" in code
    assert "value='now'" in code
    assert "key='ti1'" in code
    assert "step=900" in code
    assert "disabled=False" in code
    assert "label_visibility='visible'" in code


def test_codegen_time_input_empty_value_generates_none() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti2",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "value=None" in code


def test_codegen_time_input_iso_value() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti3",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "08:45",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "value='08:45'" in code


def test_codegen_time_input_disabled() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti4",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "now",
                    "step": 900,
                    "disabled": True,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "disabled=True" in code


def test_codegen_time_input_with_help() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti5",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "now",
                    "step": 900,
                    "disabled": False,
                    "help": "Set an alarm",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "help='Set an alarm'" in code


def test_codegen_time_input_no_help_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti6",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "now",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "help=" not in code


def test_codegen_time_input_label_visibility_hidden() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti7",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "now",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "hidden",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "label_visibility='hidden'" in code


def test_codegen_time_input_custom_step() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti8",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "now",
                    "step": 3600,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "step=3600" in code


def test_codegen_time_input_width_stretch() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti9",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "now",
                    "step": 900,
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


def test_codegen_time_input_width_custom() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ti10",
                type="time_input",
                props={
                    "label": "Time input",
                    "value": "now",
                    "step": 900,
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

