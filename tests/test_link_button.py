from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_link_button_registered() -> None:
    definition = get_widget("link_button")
    assert definition is not None
    assert definition.label == "Link button"
    prop_names = [p.name for p in definition.props_schema]
    assert "label" in prop_names
    assert "url" in prop_names
    assert "type" in prop_names
    assert "disabled" in prop_names
    assert "help" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_codegen_link_button_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="lb1",
                type="link_button",
                props={
                    "label": "Link",
                    "url": "https://www.streamlit.io",
                    "type": "secondary",
                    "disabled": False,
                    "help": "",
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.link_button(" in code
    assert "'Link'" in code
    assert "url='https://www.streamlit.io'" in code
    assert "type='secondary'" in code
    assert "icon=':material/link:'" in code
    assert "disabled=False" in code
    assert "width='stretch'" in code
    # No container wrapping or CSS for width anymore
    assert "width: 100%" not in code
    assert "st.container" not in code


def test_codegen_link_button_primary_disabled_with_help() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="lb2",
                type="link_button",
                props={
                    "label": "Visit Docs",
                    "url": "https://docs.streamlit.io",
                    "type": "primary",
                    "disabled": True,
                    "help": "Opens documentation",
                    "width": "custom",
                    "custom_width": 250,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.link_button(" in code
    assert "'Visit Docs'" in code
    assert "url='https://docs.streamlit.io'" in code
    assert "type='primary'" in code
    assert "disabled=True" in code
    assert "help='Opens documentation'" in code
    assert "width=250," in code


def test_codegen_link_button_no_help_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="lb3",
                type="link_button",
                props={
                    "label": "Link",
                    "url": "https://www.streamlit.io",
                    "type": "secondary",
                    "disabled": False,
                    "help": "",
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "help=" not in code


def test_codegen_link_button_content_width() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="lb4",
                type="link_button",
                props={
                    "label": "Link",
                    "url": "https://www.streamlit.io",
                    "type": "secondary",
                    "disabled": False,
                    "help": "",
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "width='content'" in code


def test_link_button_schema_does_not_include_icon() -> None:
    """icon should be auto-generated, not in properties pane."""
    definition = get_widget("link_button")
    prop_names = [p.name for p in definition.props_schema]
    assert "icon" not in prop_names
    assert "icon" not in definition.defaults


def test_link_button_tertiary_type() -> None:
    definition = get_widget("link_button")
    type_prop = next(p for p in definition.props_schema if p.name == "type")
    assert "tertiary" in type_prop.options

