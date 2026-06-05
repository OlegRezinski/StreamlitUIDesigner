from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_download_button_registered() -> None:
    definition = get_widget("download_button")
    assert definition is not None
    assert definition.label == "Download button"
    prop_names = [p.name for p in definition.props_schema]
    assert "label" in prop_names
    assert "data" in prop_names
    assert "file_name" in prop_names
    assert "type" in prop_names
    assert "disabled" in prop_names
    assert "help" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_codegen_download_button_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dl1",
                type="download_button",
                props={
                    "label": "Download",
                    "data": "Your data goes here",
                    "file_name": "Your_file_name.txt",
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
    assert "st.download_button(" in code
    assert "'Download'" in code
    assert "data='Your data goes here'" in code
    assert "file_name='Your_file_name.txt'" in code
    assert "mime=None" in code
    assert "key='dl1'" in code
    assert "type='secondary'" in code
    assert "icon=':material/download:'" in code
    assert "disabled=False" in code
    # stretch width emits width='stretch'
    assert "width='stretch'" in code


def test_codegen_download_button_primary_disabled_with_help() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dl2",
                type="download_button",
                props={
                    "label": "Get Report",
                    "data": "report content",
                    "file_name": "report.csv",
                    "type": "primary",
                    "disabled": True,
                    "help": "Click to download",
                    "width": "custom",
                    "custom_width": 250,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.download_button(" in code
    assert "'Get Report'" in code
    assert "data='report content'" in code
    assert "file_name='report.csv'" in code
    assert "type='primary'" in code
    assert "disabled=True" in code
    assert "help='Click to download'" in code
    assert "width=250" in code


def test_codegen_download_button_no_help_when_empty() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="dl3",
                type="download_button",
                props={
                    "label": "Download",
                    "data": "data",
                    "file_name": "file.txt",
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


def test_download_button_schema_does_not_include_icon() -> None:
    """icon should be auto-generated, not in properties pane."""
    definition = get_widget("download_button")
    prop_names = [p.name for p in definition.props_schema]
    assert "icon" not in prop_names
    assert "icon" not in definition.defaults

