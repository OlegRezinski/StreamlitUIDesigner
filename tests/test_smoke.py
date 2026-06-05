import json
from pathlib import Path

from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry
from designer.serialization import design_from_dict
from designer.widgets import register_default_widgets


def test_smoke_sample_design_codegen() -> None:
    clear_registry()
    register_default_widgets()

    sample_path = Path(__file__).resolve().parents[1] / "examples" / "sample_design.json"
    data = json.loads(sample_path.read_text(encoding="utf-8"))
    design = design_from_dict(data)

    code = generate_streamlit_code(design)
    assert "streamlit" in code
    assert "st.text_input" in code


def test_smoke_table_widget() -> None:
    clear_registry()
    register_default_widgets()

    sample_path = Path(__file__).resolve().parents[1] / "examples" / "sample_design.json"
    data = json.loads(sample_path.read_text(encoding="utf-8"))
    design = design_from_dict(data)

    code = generate_streamlit_code(design)
    assert "st.table" in code


def test_smoke_json_widget_codegen() -> None:
    clear_registry()
    register_default_widgets()

    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="json-smoke",
                type="json",
                props={
                    "expanded": "custom",
                    "custom_expanded": 2,
                    "width": "stretch",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.json(" in code
    assert "'foo': 'bar'" in code


def test_smoke_area_chart_widget_codegen() -> None:
    clear_registry()
    register_default_widgets()

    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="area-smoke",
                type="area_chart",
                props={
                    "x_label": "",
                    "y_label": "",
                    "stack": "none",
                    "width": "stretch",
                    "custom_width": 320,
                    "height": "content",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "import pandas as pd" in code
    assert "chart_data = pd.DataFrame(" in code
    assert "st.area_chart(" in code


def test_smoke_bar_chart_widget_codegen() -> None:
    clear_registry()
    register_default_widgets()

    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="bar-smoke",
                type="bar_chart",
                props={
                    "x_label": "",
                    "y_label": "",
                    "horizontal": False,
                    "sort": "true",
                    "custom_sort": "",
                    "stack": "none",
                    "width": "stretch",
                    "custom_width": 320,
                    "height": "content",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "import pandas as pd" in code
    assert "# Replace with your data" in code
    assert "chart_data = pd.DataFrame(" in code
    assert "st.bar_chart(" in code


def test_smoke_line_chart_widget_codegen() -> None:
    clear_registry()
    register_default_widgets()

    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="line-smoke",
                type="line_chart",
                props={
                    "x_label": "",
                    "y_label": "",
                    "width": "stretch",
                    "custom_width": 320,
                    "height": "content",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "import pandas as pd" in code
    assert "# Replace with your data" in code
    assert "chart_data = pd.DataFrame(" in code
    assert "st.line_chart(" in code


def test_smoke_scatter_chart_widget_codegen() -> None:
    clear_registry()
    register_default_widgets()

    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="scatter-smoke",
                type="scatter_chart",
                props={
                    "x_label": "",
                    "y_label": "",
                    "size": "",
                    "width": "stretch",
                    "custom_width": 320,
                    "height": "content",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "import pandas as pd" in code
    assert "# Replace with your data" in code
    assert "chart_data = pd.DataFrame(" in code
    assert "st.scatter_chart(" in code


def test_smoke_graphviz_chart_widget_codegen() -> None:
    clear_registry()
    register_default_widgets()

    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="graphviz-smoke",
                type="graphviz_chart",
                props={
                    "width": "stretch",
                    "custom_width": 320,
                    "height": "content",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "# Replace with your data" in code
    assert "graph_dot =" in code
    assert "digraph" in code
    assert "st.graphviz_chart(" in code


