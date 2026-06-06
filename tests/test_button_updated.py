from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_button_registered():
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


def test_button_defaults():
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


def test_button_type_options():
    defn = get_widget("button")
    type_prop = next(p for p in defn.props_schema if p.name == "type")
    assert "primary" in type_prop.options
    assert "secondary" in type_prop.options
    assert "tertiary" in type_prop.options


def test_button_width_options():
    defn = get_widget("button")
    width_prop = next(p for p in defn.props_schema if p.name == "width")
    assert "content" in width_prop.options
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


def test_codegen_button_defaults():
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn1",
                type="button",
                props={
                    "label": "Click me",
                    "key": "",
                    "help": "",
                    "type": "secondary",
                    "icon": "",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 200,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.button(" in code
    assert "'Click me'" in code
    assert "key='btn1'" in code
    assert "type='secondary'" in code
    assert "width='content'" in code
    # help not emitted when empty
    assert "help=" not in code
    # icon not emitted when empty
    assert "icon=" not in code
    # disabled not emitted when False
    assert "disabled=" not in code


def test_codegen_button_with_help():
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn2",
                type="button",
                props={
                    "label": "Help Button",
                    "key": "",
                    "help": "Click for help",
                    "type": "primary",
                    "icon": ":material/thumb_up:",
                    "disabled": True,
                    "width": "stretch",
                    "custom_width": 200,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.button(" in code
    assert "'Help Button'" in code
    assert "help='Click for help'" in code
    assert "type='primary'" in code
    assert "icon=':material/thumb_up:'" in code
    assert "disabled=True" in code
    assert "width='stretch'" in code


def test_codegen_button_custom_width():
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn3",
                type="button",
                props={
                    "label": "Wide Button",
                    "key": "",
                    "help": "",
                    "type": "secondary",
                    "icon": "",
                    "disabled": False,
                    "width": "custom",
                    "custom_width": 300,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width=300," in code


def test_codegen_button_custom_key():
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn4",
                type="button",
                props={
                    "label": "Custom Key",
                    "key": "my_button",
                    "help": "",
                    "type": "secondary",
                    "icon": "",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 200,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "key='my_button'" in code


def test_codegen_button_no_old_css():
    """The updated button should NOT generate custom CSS when colors are empty."""
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn5",
                type="button",
                props={
                    "label": "Modern",
                    "key": "",
                    "help": "",
                    "type": "secondary",
                    "icon": "",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 200,
                    "background_color": "",
                    "text_color": "",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    # No button-specific CSS should appear when colors are empty
    assert ".st-key-btn5 button" not in code
    assert "border-radius" not in code


def test_button_schema_no_old_props():
    """Old props like height, expand should be gone. background_color and text_color are now present."""
    defn = get_widget("button")
    prop_names = [p.name for p in defn.props_schema]
    assert "height" not in prop_names
    assert "expand" not in prop_names
    # New color props should be present
    assert "background_color" in prop_names
    assert "text_color" in prop_names


def test_codegen_button_background_color():
    """When background_color is set, CSS should be injected."""
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn_bg",
                type="button",
                props={
                    "label": "Colored",
                    "key": "",
                    "help": "",
                    "type": "secondary",
                    "icon": "",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 200,
                    "background_color": "#FF5733",
                    "text_color": "",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.button(" in code
    assert "background-color: #FF5733 !important" in code
    assert "unsafe_allow_html=True" in code
    assert ".st-key-btn_bg button" in code
    # Only background-color rule in the button CSS, no separate text color
    btn_css = code[code.index(".st-key-btn_bg button"):]
    btn_css_block = btn_css[: btn_css.index("}") + 1]
    assert "background-color:" in btn_css_block
    # No standalone "color:" rule (only "background-color:" should be present)
    stripped_block = btn_css_block.replace("background-color", "")
    assert "color:" not in stripped_block


def test_codegen_button_text_color():
    """When text_color is set, CSS should be injected."""
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn_tc",
                type="button",
                props={
                    "label": "Text Color",
                    "key": "",
                    "help": "",
                    "type": "secondary",
                    "icon": "",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 200,
                    "background_color": "",
                    "text_color": "#FFFFFF",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.button(" in code
    assert "color: #FFFFFF !important" in code
    assert "unsafe_allow_html=True" in code


def test_codegen_button_both_colors():
    """When both colors are set, both CSS rules should be injected."""
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn_both",
                type="button",
                props={
                    "label": "Both Colors",
                    "key": "",
                    "help": "",
                    "type": "primary",
                    "icon": "",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 200,
                    "background_color": "#123456",
                    "text_color": "#ABCDEF",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "background-color: #123456 !important" in code
    assert "color: #ABCDEF !important" in code
    assert ".st-key-btn_both button" in code


def test_codegen_button_no_css_when_no_colors():
    """When neither color is set, no CSS block should be generated."""
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="btn_noc",
                type="button",
                props={
                    "label": "No Color",
                    "key": "",
                    "help": "",
                    "type": "secondary",
                    "icon": "",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 200,
                    "background_color": "",
                    "text_color": "",
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.button(" in code
    # No button-specific CSS injection
    assert ".st-key-btn_noc button" not in code


def test_button_defaults_include_colors():
    """The defaults dict should include the new color properties."""
    defn = get_widget("button")
    assert defn.defaults["background_color"] == "#FFFFFF"
    assert defn.defaults["text_color"] == ""

