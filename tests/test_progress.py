from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets, _progress_width_value


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_progress_registered() -> None:
    definition = get_widget("progress")
    assert definition is not None
    assert definition.label == "Progress"
    prop_names = [p.name for p in definition.props_schema]
    assert "value" in prop_names
    assert "text" in prop_names
    assert "width" in prop_names
    assert "custom_width" in prop_names


def test_progress_width_options() -> None:
    definition = get_widget("progress")
    width_prop = next(p for p in definition.props_schema if p.name == "width")
    assert "stretch" in width_prop.options
    assert "custom" in width_prop.options


def test_progress_defaults() -> None:
    definition = get_widget("progress")
    assert definition.defaults == {
        "value": 50,
        "text": "",
        "width": "stretch",
        "custom_width": 320,
    }


def test_codegen_progress_defaults() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pg1",
                type="progress",
                props={
                    "value": 50,
                    "text": "",
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.progress(" in code
    assert "50," in code
    assert "text=None," in code
    assert "width='stretch'" in code


def test_codegen_progress_with_text() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pg2",
                type="progress",
                props={
                    "value": 75,
                    "text": "Loading...",
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "text='Loading...'" in code


def test_codegen_progress_custom_width() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pg3",
                type="progress",
                props={
                    "value": 50,
                    "text": "",
                    "width": "custom",
                    "custom_width": 400,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "width=400," in code


def test_codegen_progress_value_clamped_high() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pg4",
                type="progress",
                props={
                    "value": 150,
                    "text": "",
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "100," in code
    assert "150" not in code


def test_codegen_progress_value_clamped_low() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="pg5",
                type="progress",
                props={
                    "value": -10,
                    "text": "",
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "\n    0,\n" in code


def test_progress_width_helper_stretch() -> None:
    assert _progress_width_value("stretch", 320) == "stretch"


def test_progress_width_helper_custom() -> None:
    assert _progress_width_value("custom", 400) == 400


def test_progress_width_helper_custom_negative() -> None:
    assert _progress_width_value("custom", -5) == "stretch"


def test_progress_width_helper_invalid() -> None:
    assert _progress_width_value("invalid", 320) == "stretch"

