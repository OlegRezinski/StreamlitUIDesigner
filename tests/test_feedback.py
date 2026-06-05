from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_feedback_registered() -> None:
    definition = get_widget("feedback")
    assert definition is not None
    assert definition.label == "Feedback"
    prop_names = [p.name for p in definition.props_schema]
    assert "options" in prop_names
    assert "disabled" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_feedback_options_values() -> None:
    definition = get_widget("feedback")
    options_prop = next(p for p in definition.props_schema if p.name == "options")
    assert "thumbs" in options_prop.options
    assert "faces" in options_prop.options
    assert "stars" in options_prop.options


def test_feedback_width_options() -> None:
    definition = get_widget("feedback")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "content" in width_prop.options
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


def test_codegen_feedback_defaults_thumbs() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="fb1",
                type="feedback",
                props={
                    "options": "thumbs",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.feedback(" in code
    assert "'thumbs'" in code
    assert "key='fb1'" in code
    assert "default=None" in code
    assert "disabled=False" in code
    assert "width='content'" in code


def test_codegen_feedback_faces() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="fb2",
                type="feedback",
                props={
                    "options": "faces",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "'faces'" in code


def test_codegen_feedback_stars() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="fb3",
                type="feedback",
                props={
                    "options": "stars",
                    "disabled": False,
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "'stars'" in code


def test_codegen_feedback_disabled() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="fb4",
                type="feedback",
                props={
                    "options": "thumbs",
                    "disabled": True,
                    "width": "content",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "disabled=True" in code


def test_codegen_feedback_stretch_width() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="fb5",
                type="feedback",
                props={
                    "options": "thumbs",
                    "disabled": False,
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "width='stretch'" in code


def test_codegen_feedback_custom_width() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="fb6",
                type="feedback",
                props={
                    "options": "thumbs",
                    "disabled": False,
                    "width": "custom",
                    "custom_width": 150,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "width=150," in code


def test_feedback_default_not_in_schema() -> None:
    """default should be generated in code, not a property pane field."""
    definition = get_widget("feedback")
    prop_names = [p.name for p in definition.props_schema]
    assert "default" not in prop_names
    assert "default" not in definition.defaults

