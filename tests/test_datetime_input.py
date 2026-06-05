from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_datetime_input_registered() -> None:
    definition = get_widget("datetime_input")
    assert definition is not None
    assert definition.label == "Datetime input"
    prop_names = [p.name for p in definition.props_schema]
    assert "label" in prop_names
    assert "value" in prop_names
    assert "min_value" in prop_names
    assert "max_value" in prop_names
    assert "format" in prop_names
    assert "step" in prop_names
    assert "disabled" in prop_names
    assert "help" in prop_names
    assert "label_visibility" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_datetime_input_format_options() -> None:
    definition = get_widget("datetime_input")
    fmt_prop = next(p for p in definition.props_schema if p.name == "format")
    assert "YYYY/MM/DD" in fmt_prop.options
    assert "DD/MM/YYYY" in fmt_prop.options
    assert "MM/DD/YYYY" in fmt_prop.options
    assert "YYYY-MM-DD" in fmt_prop.options


def test_datetime_input_width_options() -> None:
    definition = get_widget("datetime_input")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options
    assert "content" not in width_prop.options


def test_datetime_input_label_visibility_options() -> None:
    definition = get_widget("datetime_input")
    lv_prop = next(p for p in definition.props_schema if p.name == "label_visibility")
    assert "visible" in lv_prop.options
    assert "hidden" in lv_prop.options
    assert "collapsed" in lv_prop.options


def test_codegen_datetime_input_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt1",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.datetime_input(" in code
    assert "'Datetime input'" in code
    assert "value='now'" in code
    assert "min_value=None" in code
    assert "max_value=None" in code
    assert "key='dt1'" in code
    assert "format='YYYY/MM/DD'" in code
    assert "step=900" in code
    assert "disabled=False" in code
    assert "label_visibility='visible'" in code


def test_codegen_datetime_input_empty_value_generates_none() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt2",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
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


def test_codegen_datetime_input_iso_value() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt3",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "2025-11-19 16:45",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "value='2025-11-19 16:45'" in code


def test_codegen_datetime_input_min_max() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt4",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "2025-01-01 00:00",
                    "max_value": "2025-12-31 23:59",
                    "format": "YYYY/MM/DD",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "min_value='2025-01-01 00:00'" in code
    assert "max_value='2025-12-31 23:59'" in code


def test_codegen_datetime_input_disabled() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt5",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
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


def test_codegen_datetime_input_with_help() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt6",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
                    "step": 900,
                    "disabled": False,
                    "help": "Pick a date and time",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "help='Pick a date and time'" in code


def test_codegen_datetime_input_no_help_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt7",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
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


def test_codegen_datetime_input_label_visibility_hidden() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt8",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
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


def test_codegen_datetime_input_custom_format() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt9",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "DD/MM/YYYY",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "format='DD/MM/YYYY'" in code


def test_codegen_datetime_input_custom_step() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt10",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
                    "step": 1800,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "step=1800" in code


def test_codegen_datetime_input_width_custom() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt11",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
                    "step": 900,
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                    "width": "custom",
                    "custom_width": 450,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width=450" in code


def test_codegen_datetime_input_width_stretch() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dt12",
                type="datetime_input",
                props={
                    "label": "Datetime input",
                    "value": "now",
                    "min_value": "",
                    "max_value": "",
                    "format": "YYYY/MM/DD",
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

