from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_chat_input_registered() -> None:
    definition = get_widget("chat_input")
    assert definition is not None
    assert definition.label == "Chat input"
    prop_names = [p.name for p in definition.props_schema]
    assert "placeholder" in prop_names
    assert "key" in prop_names
    assert "disabled" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_chat_input_default_props() -> None:
    definition = get_widget("chat_input")
    assert definition.defaults["placeholder"] == "Your message"
    assert definition.defaults["key"] == ""
    assert definition.defaults["disabled"] is False
    assert definition.defaults["width"] == "stretch"
    assert definition.defaults["custom_width"] == 320


def test_codegen_chat_input_custom_key() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ci_auto",
                type="chat_input",
                props={"placeholder": "Your message", "key": "my_chat_key"},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "key='my_chat_key'" in code
    assert "ci_auto" not in code


def test_chat_input_key_not_in_codegen_defaults() -> None:
    """When key prop is empty, widget.id is used as key."""
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ci_auto2",
                type="chat_input",
                props={"placeholder": "Your message", "key": ""},
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "key='ci_auto2'" in code


def test_chat_input_width_options() -> None:
    definition = get_widget("chat_input")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options
    assert "content" not in width_prop.options


def test_chat_input_not_in_schema() -> None:
    """max_chars, accept_file, accept_audio should not be in the pane schema."""
    definition = get_widget("chat_input")
    prop_names = [p.name for p in definition.props_schema]
    assert "max_chars" not in prop_names
    assert "accept_file" not in prop_names
    assert "accept_audio" not in prop_names


def test_codegen_chat_input_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ci1",
                type="chat_input",
                props={
                    "placeholder": "Your message",
                    "disabled": False,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "st.chat_input(" in code
    assert "'Your message'" in code
    assert "key='ci1'" in code
    assert "max_chars=None" in code
    assert "accept_file=False" in code
    assert "accept_audio=False" in code
    assert "disabled=False" in code
    assert "width='stretch'" in code


def test_codegen_chat_input_custom_placeholder() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ci2",
                type="chat_input",
                props={
                    "placeholder": "Ask me anything...",
                    "disabled": False,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "'Ask me anything...'" in code


def test_codegen_chat_input_disabled() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ci3",
                type="chat_input",
                props={
                    "placeholder": "Your message",
                    "disabled": True,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "disabled=True" in code


def test_codegen_chat_input_width_stretch() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ci4",
                type="chat_input",
                props={
                    "placeholder": "Your message",
                    "disabled": False,
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width='stretch'" in code


def test_codegen_chat_input_width_custom() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="ci5",
                type="chat_input",
                props={
                    "placeholder": "Your message",
                    "disabled": False,
                    "width": "custom",
                    "custom_width": 600,
                },
            )
        ],
    )
    code = generate_streamlit_code(design)
    assert "width=600" in code

