from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_page_link_registered() -> None:
    definition = get_widget("page_link")
    assert definition is not None
    assert definition.label == "Page link"
    prop_names = [p.name for p in definition.props_schema]
    assert "page" in prop_names
    assert "label" in prop_names
    assert "disabled" in prop_names
    assert "help" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_page_link_schema_does_not_include_icon() -> None:
    """icon should be auto-generated, not in properties pane."""
    definition = get_widget("page_link")
    prop_names = [p.name for p in definition.props_schema]
    assert "icon" not in prop_names
    assert "icon" not in definition.defaults


def test_codegen_page_link_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pl1",
                type="page_link",
                props={
                    "page": "https://www.streamlit.io",
                    "label": "Page link",
                    "disabled": False,
                    "help": "",
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.page_link(" in code
    assert "'https://www.streamlit.io'" in code
    assert "label='Page link'" in code
    assert "icon=':material/thumb_up:'" in code
    assert "disabled=False" in code
    assert "width='content'" in code
    # No CSS injection for width (only app background markdown is expected, not width CSS)
    assert "width: 100%" not in code
    assert "fit-content" not in code


def test_codegen_page_link_no_help_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pl2",
                type="page_link",
                props={
                    "page": "https://www.streamlit.io",
                    "label": "Page link",
                    "disabled": False,
                    "help": "",
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "help=" not in code


def test_codegen_page_link_with_help() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pl3",
                type="page_link",
                props={
                    "page": "https://www.streamlit.io",
                    "label": "Go here",
                    "disabled": False,
                    "help": "Navigate to the page",
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "help='Navigate to the page'" in code


def test_codegen_page_link_stretch_width() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pl4",
                type="page_link",
                props={
                    "page": "https://www.streamlit.io",
                    "label": "Page link",
                    "disabled": False,
                    "help": "",
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "width='stretch'" in code


def test_codegen_page_link_custom_width() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pl5",
                type="page_link",
                props={
                    "page": "https://www.streamlit.io",
                    "label": "Page link",
                    "disabled": False,
                    "help": "",
                    "width": "custom",
                    "custom_width": 200,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "width=200," in code


def test_codegen_page_link_disabled() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pl6",
                type="page_link",
                props={
                    "page": "https://www.streamlit.io",
                    "label": "Page link",
                    "disabled": True,
                    "help": "",
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "disabled=True" in code


def test_page_link_width_options() -> None:
    definition = get_widget("page_link")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "content" in width_prop.options
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


