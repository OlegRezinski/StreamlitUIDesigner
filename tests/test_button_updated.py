import inspect

import streamlit as st

from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


_HAS_ICON_POSITION = "icon_position" in inspect.signature(st.button).parameters


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def _button_design(widget_id: str, **props: object) -> Design:
    base = {
        "label": "Button",
        "key": "",
        "help": "",
        "type": "secondary",
        "icon": "",
        "disabled": False,
        "width": "content",
        "custom_width": 200,
        "background_color": "#FFFFFF",
        "text_color": "",
    }
    base.update(props)
    return Design(name="Test", widgets=[WidgetInstance(id=widget_id, type="button", props=base)])


def test_button_registered() -> None:
    defn = get_widget("button")
    assert defn is not None
    assert defn.label == "Button"

    prop_names = [p.name for p in defn.props_schema]
    assert "label" in prop_names
    assert "key" in prop_names
    assert "help" in prop_names
    assert "type" in prop_names
    assert "icon" in prop_names
    assert "disabled" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names
    assert "background_color" in prop_names
    assert "text_color" in prop_names
    assert "icon_position" not in prop_names


def test_button_defaults() -> None:
    defn = get_widget("button")
    assert defn.defaults == {
        "label": "Button",
        "key": "",
        "help": "",
        "type": "secondary",
        "icon": "",
        "disabled": False,
        "width": "content",
        "custom_width": 200,
        "background_color": "#FFFFFF",
        "text_color": "",
    }


def test_button_type_options() -> None:
    defn = get_widget("button")
    type_prop = next(p for p in defn.props_schema if p.name == "type")
    assert type_prop.options == ["primary", "secondary", "tertiary"]


def test_button_width_options() -> None:
    defn = get_widget("button")
    width_prop = next(p for p in defn.props_schema if p.name == "width")
    assert width_prop.options == ["content", "stretch", "custom"]


def test_codegen_button_defaults() -> None:
    code = generate_streamlit_code(_button_design("btn1", label="Click me"))
    assert "st.button(" in code
    assert "'Click me'" in code
    assert "key='btn1'" in code
    assert "type='secondary'" in code
    assert "width='content'" in code
    assert "help=" not in code
    assert "icon=" not in code
    assert "disabled=" not in code
    assert "icon_position=" not in code
    assert ".st-key-btn1 button" in code
    assert "background-color: #FFFFFF !important" in code


def test_codegen_button_with_help_icon_disabled() -> None:
    code = generate_streamlit_code(
        _button_design(
            "btn2",
            label="Help Button",
            help="Click for help",
            type="primary",
            icon=":material/thumb_up:",
            disabled=True,
            width="stretch",
        )
    )
    assert "st.button(" in code
    assert "help='Click for help'" in code
    assert "type='primary'" in code
    assert "icon=':material/thumb_up:'" in code
    assert "disabled=True" in code
    assert "width='stretch'" in code
    if _HAS_ICON_POSITION:
        assert "icon_position='left'" in code


def test_codegen_button_custom_width() -> None:
    code = generate_streamlit_code(_button_design("btn3", width="custom", custom_width=300))
    assert "width=300," in code


def test_codegen_button_custom_key() -> None:
    code = generate_streamlit_code(_button_design("btn4", key="my_button"))
    assert "key='my_button'" in code


def test_codegen_button_background_color_only() -> None:
    code = generate_streamlit_code(_button_design("btn_bg", background_color="#FF5733"))
    assert ".st-key-btn_bg button" in code
    assert "background-color: #FF5733 !important" in code
    css_block = code.split(".st-key-btn_bg button", 1)[1].split("}", 1)[0]
    assert " color: #" not in css_block


def test_codegen_button_text_color_only() -> None:
    code = generate_streamlit_code(_button_design("btn_tc", background_color="", text_color="#FFFFFF"))
    assert ".st-key-btn_tc button" in code
    assert "color: #FFFFFF !important" in code
    css_block = code.split(".st-key-btn_tc button", 1)[1].split("}", 1)[0]
    assert "background-color:" not in css_block


def test_codegen_button_both_colors() -> None:
    code = generate_streamlit_code(
        _button_design("btn_both", key="my_button_key", background_color="#123456", text_color="#ABCDEF")
    )
    assert ".st-key-my_button_key button" in code
    assert "background-color: #123456 !important" in code
    assert "color: #ABCDEF !important" in code


def test_codegen_button_no_css_when_no_colors() -> None:
    code = generate_streamlit_code(_button_design("btn_noc", background_color=""))
    assert ".st-key-btn_noc button" not in code

