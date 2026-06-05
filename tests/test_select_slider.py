from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_select_slider_registered() -> None:
    definition = get_widget("select_slider")
    assert definition is not None
    assert definition.label == "Select slider"
    prop_names = [p.name for p in definition.props_schema]
    assert "label" in prop_names
    assert "options" in prop_names
    assert "disabled" in prop_names
    assert "help" in prop_names
    assert "label_visibility" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_select_slider_width_options() -> None:
    definition = get_widget("select_slider")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options
    assert "content" not in width_prop.options


def test_select_slider_label_visibility_options() -> None:
    definition = get_widget("select_slider")
    lv_prop = next(p for p in definition.props_schema if p.name == "label_visibility")
    assert "visible" in lv_prop.options
    assert "hidden" in lv_prop.options
    assert "collapsed" in lv_prop.options


def test_select_slider_value_not_in_schema() -> None:
    """value should be generated in code as None, not exposed as a property pane field."""
    definition = get_widget("select_slider")
    prop_names = [p.name for p in definition.props_schema]
    assert "value" not in prop_names
    assert "value" not in definition.defaults


def test_codegen_select_slider_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ss1",
                type="select_slider",
                props={
                    "label": "Select slider",
                    "options": "Option 1, Option 2, Option 3",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.select_slider(" in code
    assert "'Select slider'" in code
    assert "options=['Option 1', 'Option 2', 'Option 3']" in code
    assert "value=None" in code
    assert "key='ss1'" in code
    assert "disabled=False" in code
    assert "label_visibility='visible'" in code


def test_codegen_select_slider_disabled() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ss2",
                type="select_slider",
                props={
                    "label": "Select slider",
                    "options": "A, B, C",
                    "disabled": True,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "disabled=True" in code


def test_codegen_select_slider_with_help() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ss3",
                type="select_slider",
                props={
                    "label": "Select slider",
                    "options": "A, B",
                    "disabled": False,
                    "help": "Pick an option",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "help='Pick an option'" in code


def test_codegen_select_slider_no_help_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ss4",
                type="select_slider",
                props={
                    "label": "Select slider",
                    "options": "A, B",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "help=" not in code


def test_codegen_select_slider_label_visibility_hidden() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ss5",
                type="select_slider",
                props={
                    "label": "Select slider",
                    "options": "A, B",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "hidden",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "label_visibility='hidden'" in code


def test_codegen_select_slider_width_stretch() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ss6",
                type="select_slider",
                props={
                    "label": "Select slider",
                    "options": "A, B",
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


def test_codegen_select_slider_width_custom() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ss7",
                type="select_slider",
                props={
                    "label": "Select slider",
                    "options": "A, B",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                    "width": "custom",
                    "custom_width": 500,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width=500" in code


def test_codegen_select_slider_options_parsed() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ss8",
                type="select_slider",
                props={
                    "label": "Colors",
                    "options": "red, green, blue",
                    "disabled": False,
                    "help": "",
                    "label_visibility": "visible",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "['red', 'green', 'blue']" in code

