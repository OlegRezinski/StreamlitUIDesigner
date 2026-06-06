from pathlib import Path

from designer.codegen import generate_streamlit_code
from designer.models import Design, WidgetInstance
from designer.registry import clear_registry, get_widget
from designer.widgets import register_default_widgets


def _sample_code_text() -> str:
    sample_path = Path(__file__).resolve().parents[1] / "samples" / "Code_sample.py"
    return sample_path.read_text(encoding="utf-8").rstrip()


def setup_function() -> None:
    clear_registry()
    register_default_widgets()


def test_codegen_includes_date_import() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w1",
                type="date_input",
                props={"label": "Pick a date", "value": "2024-01-02"},
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "from datetime import date" in code
    assert "st.date_input" in code


def test_codegen_selectbox_options() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w2",
                type="selectbox",
                props={"label": "Pick", "options": ["A", "B"], "index": 1},
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.selectbox" in code
    assert "['A', 'B']" in code


def test_codegen_multiselect() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w3",
                type="multiselect",
                props={"label": "Pick", "options": ["A", "B"], "default": ["B"]},
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.multiselect" in code
    assert "default=['B']" in code


def test_codegen_columns() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w4",
                type="columns_container",
                props={
                    "label": "Layout",
                    "columns": 2,
                    "background_color": "#ABCDEF",
                },
            ),
            WidgetInstance(
                id="w4c1",
                type="column",
                props={"label": "Col 1", "ratio": 2, "background_color": "#111111"},
                parent_id="w4",
            ),
            WidgetInstance(
                id="w4c2",
                type="column",
                props={"label": "Col 2", "ratio": 1, "background_color": "#222222"},
                parent_id="w4",
            ),
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.columns([2, 1])" in code
    assert "background-color: #ABCDEF" in code
    assert "background-color: #111111" in code
    assert "background-color: #222222" in code


def test_codegen_columns_with_child() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w5",
                type="columns_container",
                props={"label": "Layout", "columns": 2},
            ),
            WidgetInstance(
                id="w5c1",
                type="column",
                props={"label": "Col 1", "ratio": 1},
                parent_id="w5",
            ),
            WidgetInstance(
                id="w5c2",
                type="column",
                props={"label": "Col 2", "ratio": 1},
                parent_id="w5",
            ),
            WidgetInstance(
                id="w6",
                type="text_input",
                props={"label": "Inside"},
                parent_id="w5c1",
            ),
        ],
    )

    code = generate_streamlit_code(design)
    assert "with cols[0]:" in code
    assert "st.text_input('Inside'" in code


def test_codegen_button_native() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w7",
                type="button",
                props={
                    "label": "Click",
                    "key": "",
                    "help": "",
                    "type": "primary",
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
    assert "'Click'" in code
    assert "key='w7'" in code
    assert "type='primary'" in code
    assert "width='content'" in code
    # No button-specific CSS container wrapping
    assert ".st-key-button_" not in code
    assert "border-radius" not in code


def test_codegen_button_stretch_width() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w8",
                type="button",
                props={
                    "label": "Wide",
                    "key": "",
                    "help": "",
                    "type": "secondary",
                    "icon": "",
                    "disabled": False,
                    "width": "stretch",
                    "custom_width": 200,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "width='stretch'" in code


def test_codegen_checkbox_toggle_color_picker() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w9",
                type="checkbox",
                props={"label": "Agree", "checked": True, "disabled": True, "label_visibility": False},
            ),
            WidgetInstance(
                id="w10",
                type="toggle",
                props={"label": "On", "value": False},
            ),
            WidgetInstance(
                id="w11",
                type="color_picker",
                props={"label": "Pick", "value": "#FF00FF"},
            ),
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.checkbox" in code
    assert "value=True" in code
    assert "disabled=True" in code
    assert "label_visibility='hidden'" in code
    assert "st.toggle" in code
    assert "st.color_picker" in code
    assert "#FF00FF" in code


def test_codegen_radio_slider_number_file_uploader() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w12",
                type="radio",
                props={"label": "Choice", "options": ["A", "B"], "index": 1},
            ),
            WidgetInstance(
                id="w13",
                type="slider",
                props={"label": "Level", "min": 0, "max": 10, "value": 3, "step": 1},
            ),
            WidgetInstance(
                id="w14",
                type="number_input",
                props={"label": "Count", "min": 0, "max": 5, "value": 2, "step": 1},
            ),
            WidgetInstance(
                id="w15",
                type="file_uploader",
                props={"label": "Upload", "types": ["csv", "txt"]},
            ),
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.radio" in code
    assert "st.slider" in code
    assert "st.number_input" in code
    assert "st.file_uploader" in code
    assert "['csv', 'txt']" in code


def test_codegen_text_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w16",
                type="text",
                props={
                    "text": "Hello",
                    "size": 18,
                    "color": "#112233",
                    "horizontal_alignment": "center",
                    "vertical_alignment": "bottom",
                    "style": "serif",
                    "bold": True,
                    "italic": True,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.text('Hello')" in code
    assert "with st.container(key='text_w16'):" in code
    assert ".st-key-text_w16 [data-testid=\"stText\"]" in code
    assert "st.markdown" in code
    assert "font-size: 18px" in code
    assert "color: #112233" in code
    assert "justify-content: center" in code
    assert "align-items: flex-end" in code
    assert "font-family: serif" in code
    assert "font-weight: 700" in code
    assert "font-style: italic" in code


def test_codegen_title_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w17",
                type="title",
                props={
                    "text": "Dashboard",
                    "size": 44,
                    "color": "#224466",
                    "horizontal_alignment": "center",
                    "vertical_alignment": "bottom",
                    "style": "serif",
                    "bold": False,
                    "italic": True,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.title('Dashboard')" in code
    assert "with st.container(key='title_w17'):" in code
    assert ".st-key-title_w17 [data-testid=\"stHeading\"] h1" in code
    assert "font-size: 44px" in code
    assert "color: #224466" in code
    assert "justify-content: center" in code
    assert "align-items: flex-end" in code
    assert "font-family: serif" in code
    assert "font-weight: 400" in code
    assert "font-style: italic" in code


def test_codegen_header_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w18",
                type="header",
                props={
                    "text": "Section Header",
                    "size": 34,
                    "color": "#556677",
                    "horizontal_alignment": "right",
                    "vertical_alignment": "top",
                    "style": "monospace",
                    "bold": True,
                    "italic": False,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.header('Section Header')" in code
    assert "with st.container(key='header_w18'):" in code
    assert ".st-key-header_w18 [data-testid=\"stHeading\"] h2" in code
    assert "font-size: 34px" in code
    assert "color: #556677" in code
    assert "justify-content: flex-end" in code
    assert "align-items: flex-start" in code
    assert "font-family: monospace" in code
    assert "font-weight: 700" in code
    assert "font-style: normal" in code


def test_codegen_subheader_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w19",
                type="subheader",
                props={
                    "text": "Section Subheader",
                    "size": 30,
                    "color": "#667788",
                    "horizontal_alignment": "center",
                    "vertical_alignment": "bottom",
                    "style": "serif",
                    "bold": False,
                    "italic": True,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.subheader('Section Subheader')" in code
    assert "with st.container(key='subheader_w19'):" in code
    assert ".st-key-subheader_w19 [data-testid=\"stHeading\"] h3" in code
    assert "font-size: 30px" in code
    assert "color: #667788" in code
    assert "justify-content: center" in code
    assert "align-items: flex-end" in code
    assert "font-family: serif" in code
    assert "font-weight: 400" in code
    assert "font-style: italic" in code


def test_codegen_markdown_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w20",
                type="markdown",
                props={
                    "text": "Preview **Markdown**",
                    "size": 18,
                    "color": "#778899",
                    "horizontal_alignment": "right",
                    "vertical_alignment": "top",
                    "style": "monospace",
                    "bold": True,
                    "italic": False,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.markdown('Preview **Markdown**')" in code
    assert "with st.container(key='markdown_w20'):" in code
    assert ".st-key-markdown_w20 [data-testid=\"stMarkdown\"]" in code
    assert "font-size: 18px" in code
    assert "color: #778899" in code
    assert "justify-content: flex-start" in code
    assert "align-items: flex-end" in code
    assert "font-family: monospace" in code
    assert "font-weight: 700" in code
    assert "font-style: normal" in code


def test_codegen_badge_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w21",
                type="badge",
                props={
                    "text": "Status Badge",
                    "size": 15,
                    "text_color": "#F1F2F3",
                    "background_color": "#345678",
                    "horizontal_alignment": "center",
                    "vertical_alignment": "bottom",
                    "style": "serif",
                    "bold": True,
                    "italic": True,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.badge('Status Badge', color='blue', width='content')" in code
    assert "with st.container(key='badge_w21'):" in code
    assert ".st-key-badge_w21 [data-testid=\"stMarkdown\"]" in code
    assert "background-color: #345678" in code
    assert "color: #F1F2F3" in code
    assert "font-size: 15px" in code
    assert "align-items: center" in code
    assert "justify-content: flex-end" in code
    assert "font-family: serif" in code
    assert "font-weight: 700" in code
    assert "font-style: italic" in code


def test_codegen_caption_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w22",
                type="caption",
                props={
                    "text": "Small helper text",
                    "size": 13,
                    "color": "#445566",
                    "horizontal_alignment": "center",
                    "vertical_alignment": "top",
                    "style": "monospace",
                    "bold": True,
                    "italic": True,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.caption('Small helper text')" in code
    assert "with st.container(key='caption_w22'):" in code
    assert ".st-key-caption_w22 [data-testid=\"stCaptionContainer\"]" in code
    assert "font-size: 13px" in code
    assert "color: #445566" in code
    assert "justify-content: flex-start" in code
    assert "align-items: center" in code
    assert "font-family: monospace" in code
    assert "font-weight: 700" in code
    assert "font-style: italic" in code


def test_codegen_code_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w23",
                type="code",
                props={
                    "width": "content",
                    "height": "stretch",
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    sample_code = _sample_code_text()
    assert "st.code(" in code
    assert repr(sample_code) in code
    assert "language='python'" in code
    assert "width='content'" in code
    assert "height='stretch'" in code


def test_codegen_divider_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w24",
                type="divider",
                props={
                    "line_width": 3,
                    "color": "#AABBCC",
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "with st.container(key='divider_w24'):" in code
    assert "st.divider()" in code
    assert ".st-key-divider_w24 hr" in code
    assert "border-top: 3px solid #AABBCC" in code


def test_codegen_echo_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w25",
                type="echo",
                props={
                    "code_location": "below",
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "with st.echo(code_location='below'):" in code
    assert "st.write('Echo output')" in code


def test_codegen_latex_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w26",
                type="latex",
                props={
                    "text": r"\\frac{a}{b}",
                    "help": "Tooltip **markdown**",
                    "width": "custom",
                    "custom_width": 320,
                    "font_size": 24,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "with st.container(key='latex_w26'):" in code
    assert "st.latex(" in code
    assert repr(r"\\frac{a}{b}") in code
    assert "help='Tooltip **markdown**'" in code
    assert "width=320" in code
    assert ".st-key-latex_w26 .katex" in code
    assert "font-size: 24px" in code


def test_codegen_help_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w27",
                type="help",
                props={
                    "text": "help text",
                    "width": "custom",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.help('help text', width=320)" in code


def test_codegen_dataframe_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w28",
                type="dataframe",
                props={
                    "width": "custom",
                    "custom_width": 360,
                    "height": "custom",
                    "custom_height": 240,
                    "selection_mode": "single-row",
                    "hide_index": True,
                    "row_height": "30",
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "with st.container(key='dataframe_w28'):" in code
    assert "st.dataframe(" in code
    assert "'Name': ['Bob', 'Alice', 'James']" in code
    assert "width=360" in code
    assert "height=240" in code
    assert "selection_mode='single-row'" in code
    assert "hide_index=True" in code
    assert "row_height=30" in code


def test_codegen_data_editor_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w29",
                type="data_editor",
                props={
                    "width": "custom",
                    "custom_width": 360,
                    "height": "custom",
                    "custom_height": 240,
                    "hide_index": True,
                    "num_rows": "delete",
                    "row_height": "30",
                    "disabled": ["Name", 0, "_index"],
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "with st.container(key='data_editor_w29'):" in code
    assert "st.data_editor(" in code
    assert "'Name': ['Bob', 'Alice', 'James']" in code
    assert "width=360" in code
    assert "height=240" in code
    assert "hide_index=True" in code
    assert "num_rows='delete'" in code
    assert "disabled=['Name', 0, '_index']" in code
    assert "key='w29'" in code
    assert "row_height=30" in code


def test_badge_widget_schema_does_not_include_icon() -> None:
    definition = get_widget("badge")
    prop_names = [prop.name for prop in definition.props_schema]

    assert "icon" not in prop_names
    assert "icon" not in definition.defaults


def test_all_implemented_text_elements_include_text_property() -> None:
    text_widget_types = ["text", "title", "header", "subheader", "markdown", "badge", "caption"]

    for widget_type in text_widget_types:
        definition = get_widget(widget_type)
        prop_names = [prop.name for prop in definition.props_schema]

        assert "text" in prop_names, f"{widget_type} is missing the text property"
        assert "text" in definition.defaults, f"{widget_type} is missing the text default"


def test_text_widget_schema_does_not_include_expand() -> None:
    definition = get_widget("text")
    prop_names = [prop.name for prop in definition.props_schema]

    assert "expand" not in prop_names
    assert "expand" not in definition.defaults


def test_codegen_table_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="w1",
                type="table",
                props={
                    "width": "stretch",
                    "custom_width": 0,
                    "height": "auto",
                    "custom_height": 0,
                    "border": True,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "from samples.DataFrame_sample import df_sample" in code
    assert "st.table(df_sample" in code


def test_codegen_metric_widget() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="metric1",
                type="metric",
                props={
                    "label": "Revenue",
                    "value": "1234",
                    "delta": "-15",
                    "delta_color": "inverse",
                    "help": "Monthly revenue",
                    "label_visibility": "visible",
                    "border": True,
                    "background_color": "#112233",
                    "height": "custom",
                    "custom_height": 180,
                    "width": "custom",
                    "custom_width": 420,
                    "chart_data": ["1", "2", "3.5"],
                    "chart_type": "bar",
                    "delta_arrow": "down",
                    "format": "dollar",
                    "delta_description": "vs last month",
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.metric(" in code
    assert "'Revenue'" in code
    assert "value=1234" in code
    assert "delta=-15" in code
    assert "delta_color='inverse'" in code
    assert "border=True" in code
    assert "background-color: #112233" in code
    assert "width=420" in code
    assert "height=180" in code
    assert "chart_data=[1.0, 2.0, 3.5]" in code
    assert "chart_type='bar'" in code
    assert "delta_arrow='down'" in code
    assert "format='dollar'" in code


def test_codegen_metric_chart_data_text_has_effect() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="metric-chart",
                type="metric",
                props={
                    "label": "Trend",
                    "value": "0",
                    "delta": "",
                    "chart_data": "1,2,3,4",
                    "chart_type": "line",
                    "border": False,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "row = st.container(horizontal=True)" in code
    assert "with row:" in code
    assert "chart_data=[1.0, 2.0, 3.0, 4.0]" in code
    assert "delta=0" in code
    assert "border=True" in code


def test_codegen_metric_widget_chart_data_from_text_and_empty_delta() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="metric2",
                type="metric",
                props={
                    "label": "Trend",
                    "value": "100",
                    "delta": "",
                    "chart_data": "1,2,3,4",
                    "chart_type": "line",
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "chart_data=[1.0, 2.0, 3.0, 4.0]" in code
    assert "delta=0" in code


def test_codegen_json_widget_uses_sample_data_with_custom_controls() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="json1",
                type="json",
                props={
                    "expanded": "custom",
                    "custom_expanded": 2,
                    "width": "custom",
                    "custom_width": 280,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.json(" in code
    assert "'foo': 'bar'" in code
    assert "expanded=2" in code
    assert "width=280" in code


def test_codegen_json_widget_maps_contain_width_to_content() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="json2",
                type="json",
                props={
                    "expanded": "true",
                    "custom_expanded": 2,
                    "width": "contain",
                    "custom_width": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.json(" in code
    assert "expanded=True" in code
    assert "width='content'" in code


def test_codegen_area_chart_widget_uses_sample_data() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="area1",
                type="area_chart",
                props={
                    "x_label": "X Label",
                    "y_label": "Y Label",
                    "stack": "normalize",
                    "width": "custom",
                    "custom_width": 360,
                    "height": "custom",
                    "custom_height": 240,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "import pandas as pd" in code
    assert "# Replace with your data" in code
    assert "chart_data = pd.DataFrame(" in code
    assert "from samples.Chart_data_sample import get_chart_data_sample" not in code
    assert "st.area_chart(" in code
    assert "x_label='X Label'" in code
    assert "y_label='Y Label'" in code
    assert "stack='normalize'" in code
    assert "width=360" in code
    assert "height=240" in code


def test_codegen_area_chart_content_dimensions_and_optional_args() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="area2",
                type="area_chart",
                props={
                    "x_label": "",
                    "y_label": "",
                    "stack": "none",
                    "width": "content",
                    "custom_width": 320,
                    "height": "stretch",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "chart_data = pd.DataFrame(" in code
    assert "st.area_chart(" in code
    assert "width='content'" in code
    assert "height='stretch'" in code
    assert "stack=" not in code


def test_codegen_bar_chart_widget_uses_sample_data() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="bar1",
                type="bar_chart",
                props={
                    "x_label": "X Label",
                    "y_label": "Y Label",
                    "horizontal": True,
                    "sort": "custom",
                    "custom_sort": "-b",
                    "stack": "layered",
                    "width": "custom",
                    "custom_width": 420,
                    "height": "custom",
                    "custom_height": 260,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "import pandas as pd" in code
    assert "# Replace with your data" in code
    assert "chart_data = pd.DataFrame(" in code
    assert "st.bar_chart(" in code
    assert "x_label='X Label'" in code
    assert "y_label='Y Label'" in code
    assert "horizontal=True" in code
    assert "sort='-b'" in code
    assert "stack='layered'" in code
    assert "width=420" in code
    assert "height=260" in code


def test_codegen_bar_chart_defaults_and_optional_args() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="bar2",
                type="bar_chart",
                props={
                    "x_label": "",
                    "y_label": "",
                    "horizontal": False,
                    "sort": "false",
                    "custom_sort": "",
                    "stack": "none",
                    "width": "content",
                    "custom_width": 320,
                    "height": "stretch",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.bar_chart(" in code
    assert "horizontal=False" in code
    assert "sort=False" in code
    assert "width='content'" in code
    assert "height='stretch'" in code
    assert "stack=" not in code


def test_codegen_line_chart_widget_uses_sample_data() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="line1",
                type="line_chart",
                props={
                    "x_label": "X Label",
                    "y_label": "Y Label",
                    "width": "custom",
                    "custom_width": 400,
                    "height": "custom",
                    "custom_height": 280,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "import pandas as pd" in code
    assert "# Replace with your data" in code
    assert "chart_data = pd.DataFrame(" in code
    assert "from samples.Chart_data_sample import get_chart_data_sample" not in code
    assert "st.line_chart(" in code
    assert "x_label='X Label'" in code
    assert "y_label='Y Label'" in code
    assert "width=400" in code
    assert "height=280" in code


def test_codegen_line_chart_content_dimensions_and_optional_args() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="line2",
                type="line_chart",
                props={
                    "x_label": "",
                    "y_label": "",
                    "width": "content",
                    "custom_width": 320,
                    "height": "stretch",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "chart_data = pd.DataFrame(" in code
    assert "st.line_chart(" in code
    assert "width='content'" in code
    assert "height='stretch'" in code
    # Empty labels should not appear
    assert "x_label=" not in code
    assert "y_label=" not in code


def test_codegen_line_chart_default_dimensions() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="line3",
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
    assert "st.line_chart(" in code
    assert "width='stretch'" in code
    assert "height='content'" in code


def test_codegen_scatter_chart_widget_uses_sample_data() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="scatter1",
                type="scatter_chart",
                props={
                    "x_label": "X Axis",
                    "y_label": "Y Axis",
                    "size": "100",
                    "width": "custom",
                    "custom_width": 450,
                    "height": "custom",
                    "custom_height": 300,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "import pandas as pd" in code
    assert "# Replace with your data" in code
    assert "chart_data = pd.DataFrame(" in code
    assert "from samples.Chart_data_sample import get_chart_data_sample" not in code
    assert "st.scatter_chart(" in code
    assert "x_label='X Axis'" in code
    assert "y_label='Y Axis'" in code
    assert "size=100.0" in code
    assert "width=450" in code
    assert "height=300" in code


def test_codegen_scatter_chart_content_dimensions_and_optional_args() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="scatter2",
                type="scatter_chart",
                props={
                    "x_label": "",
                    "y_label": "",
                    "size": "",
                    "width": "content",
                    "custom_width": 320,
                    "height": "stretch",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "chart_data = pd.DataFrame(" in code
    assert "st.scatter_chart(" in code
    assert "width='content'" in code
    assert "height='stretch'" in code
    # Empty labels and size should not appear
    assert "x_label=" not in code
    assert "y_label=" not in code
    assert "size=" not in code


def test_codegen_scatter_chart_default_dimensions() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="scatter3",
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
    assert "st.scatter_chart(" in code
    assert "width='stretch'" in code
    assert "height='content'" in code



def test_codegen_graphviz_chart_widget_uses_sample_dot() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="graphviz1",
                type="graphviz_chart",
                props={
                    "width": "custom",
                    "custom_width": 500,
                    "height": "custom",
                    "custom_height": 400,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "# Replace with your data" in code
    assert "graph_dot =" in code
    assert "digraph" in code
    assert "run -> intr" in code
    assert "st.graphviz_chart(" in code
    assert "graph_dot" in code
    assert "width=500" in code
    assert "height=400" in code


def test_codegen_graphviz_chart_content_dimensions() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="graphviz2",
                type="graphviz_chart",
                props={
                    "width": "content",
                    "custom_width": 320,
                    "height": "stretch",
                    "custom_height": 320,
                },
            )
        ],
    )

    code = generate_streamlit_code(design)
    assert "st.graphviz_chart(" in code
    assert "width='content'" in code
    assert "height='stretch'" in code
    assert "# Replace with your data" in code


def test_codegen_graphviz_chart_default_dimensions() -> None:
    design = Design(
        name="Test",
        widgets=[
            WidgetInstance(
                id="graphviz3",
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
    assert "st.graphviz_chart(" in code
    assert "width='stretch'" in code
    assert "height='content'" in code

