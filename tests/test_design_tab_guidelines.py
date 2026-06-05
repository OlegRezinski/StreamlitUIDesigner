from __future__ import annotations

from copy import deepcopy

from streamlit.testing.v1 import AppTest

from designer.models import Design, PropDefinition, WidgetDefinition, WidgetInstance
from designer.registry import clear_registry, list_widgets, register_widget
from designer.widgets import register_default_widgets


MAIN_CONTAINER_ID = "__main__"


def _run_app(design: Design | None = None, session_state: dict | None = None) -> AppTest:
    at = AppTest.from_file("app.py")
    if design is not None:
        at.session_state["design"] = design
    if session_state:
        for key, value in session_state.items():
            at.session_state[key] = value
    return at.run(timeout=15)


def test_main_selected_by_default() -> None:
    at = _run_app()
    assert at.session_state["selected_id"] == MAIN_CONTAINER_ID
    assert at.session_state["hierarchy_checked_id"] == MAIN_CONTAINER_ID
    assert at.session_state["add_to_container"] == MAIN_CONTAINER_ID
    assert at.selectbox(key="main_screen_width") is not None


def test_tree_selection_sets_container_for_column_child() -> None:
    container = WidgetInstance(id="c1", type="columns_container", props={"columns": 1})
    column = WidgetInstance(id="col1", type="column", parent_id="c1")
    child = WidgetInstance(id="w1", type="text_input", props={"label": "A"}, parent_id="col1")
    design = Design(name="Test", widgets=[container, column, child])

    at = _run_app(design, {"hierarchy_checked_id": "col1", "hierarchy_checked_prev": ["col1"]})
    assert at.session_state["add_to_container"] == "c1"
    assert at.session_state["target_column_id"] == "col1"


def test_tree_selection_sets_main_for_top_level_widget() -> None:
    widget = WidgetInstance(id="w2", type="text_input", props={"label": "Top"})
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "w2", "hierarchy_checked_prev": ["w2"]})
    assert at.session_state["add_to_container"] == MAIN_CONTAINER_ID
    assert at.session_state["target_container_id"] is None


def test_container_pane_updates_tree_selection() -> None:
    container = WidgetInstance(id="c2", type="columns_container", props={"columns": 1})
    column = WidgetInstance(id="col2", type="column", parent_id="c2")
    design = Design(name="Test", widgets=[container, column])

    at = _run_app(
        design,
        {
            "add_to_container": "c2",
            "container_pane_prev": MAIN_CONTAINER_ID,
            "suppress_container_pane_sync": False,
        },
    )
    assert at.session_state["hierarchy_checked_id"] == "c2"


def test_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(id="w3", type="text_input", props={"label": "Name"})
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "w3", "hierarchy_checked_prev": ["w3"]})
    prop_key = f"prop_{widget.id}_label"
    assert at.text_input(key=prop_key) is not None


def test_title_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="title1",
        type="title",
        props={
            "text": "Page Title",
            "size": 40,
            "color": "#000000",
            "horizontal_alignment": "left",
            "vertical_alignment": "center",
            "style": "normal",
            "bold": True,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "title1", "hierarchy_checked_prev": ["title1"]})
    assert at.text_input(key="prop_title1_text") is not None
    assert at.color_picker(key="prop_title1_color") is not None
    assert at.selectbox(key="prop_title1_horizontal_alignment") is not None
    assert at.checkbox(key="prop_title1_bold") is not None


def test_header_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="header1",
        type="header",
        props={
            "text": "Section Header",
            "size": 32,
            "color": "#000000",
            "horizontal_alignment": "left",
            "vertical_alignment": "center",
            "style": "normal",
            "bold": True,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "header1", "hierarchy_checked_prev": ["header1"]})
    assert at.text_input(key="prop_header1_text") is not None
    assert at.color_picker(key="prop_header1_color") is not None
    assert at.selectbox(key="prop_header1_horizontal_alignment") is not None
    assert at.checkbox(key="prop_header1_bold") is not None


def test_subheader_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="subheader1",
        type="subheader",
        props={
            "text": "Section Subheader",
            "size": 28,
            "color": "#000000",
            "horizontal_alignment": "left",
            "vertical_alignment": "center",
            "style": "normal",
            "bold": True,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "subheader1", "hierarchy_checked_prev": ["subheader1"]})
    assert at.text_input(key="prop_subheader1_text") is not None
    assert at.color_picker(key="prop_subheader1_color") is not None
    assert at.selectbox(key="prop_subheader1_horizontal_alignment") is not None
    assert at.checkbox(key="prop_subheader1_bold") is not None


def test_markdown_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="markdown1",
        type="markdown",
        props={
            "text": "Body markdown",
            "size": 16,
            "color": "#000000",
            "horizontal_alignment": "left",
            "vertical_alignment": "center",
            "style": "normal",
            "bold": False,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "markdown1", "hierarchy_checked_prev": ["markdown1"]})
    assert at.text_input(key="prop_markdown1_text") is not None
    assert at.color_picker(key="prop_markdown1_color") is not None
    assert at.selectbox(key="prop_markdown1_horizontal_alignment") is not None
    assert at.checkbox(key="prop_markdown1_bold") is not None


def test_badge_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="badge1",
        type="badge",
        props={
            "text": "Badge",
            "size": 14,
            "text_color": "#FFFFFF",
            "background_color": "#2E6CF6",
            "horizontal_alignment": "left",
            "vertical_alignment": "center",
            "style": "normal",
            "bold": False,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "badge1", "hierarchy_checked_prev": ["badge1"]})
    assert at.text_input(key="prop_badge1_text") is not None
    assert at.color_picker(key="prop_badge1_text_color") is not None
    assert at.color_picker(key="prop_badge1_background_color") is not None
    assert at.selectbox(key="prop_badge1_horizontal_alignment") is not None
    assert at.checkbox(key="prop_badge1_bold") is not None


def test_caption_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="caption1",
        type="caption",
        props={
            "text": "Caption",
            "size": 14,
            "color": "#000000",
            "horizontal_alignment": "left",
            "vertical_alignment": "center",
            "style": "normal",
            "bold": False,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "caption1", "hierarchy_checked_prev": ["caption1"]})
    assert at.text_input(key="prop_caption1_text") is not None
    assert at.color_picker(key="prop_caption1_color") is not None
    assert at.selectbox(key="prop_caption1_horizontal_alignment") is not None
    assert at.checkbox(key="prop_caption1_bold") is not None


def test_code_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="code1",
        type="code",
        props={
            "width": "stretch",
            "height": "content",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "code1", "hierarchy_checked_prev": ["code1"]})
    assert at.selectbox(key="prop_code1_width") is not None
    assert at.selectbox(key="prop_code1_height") is not None


def test_divider_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="divider1",
        type="divider",
        props={
            "line_width": 1,
            "color": "#D9D9D9",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "divider1", "hierarchy_checked_prev": ["divider1"]})
    assert at.number_input(key="prop_divider1_line_width") is not None
    assert at.color_picker(key="prop_divider1_color") is not None


def test_echo_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="echo1",
        type="echo",
        props={
            "code_location": "above",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "echo1", "hierarchy_checked_prev": ["echo1"]})
    assert at.selectbox(key="prop_echo1_code_location") is not None


def test_latex_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="latex1",
        type="latex",
        props={
            "text": r"x^2 + y^2 = z^2",
            "help": "Tooltip",
            "width": "stretch",
            "custom_width": 320,
            "font_size": 16,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "latex1", "hierarchy_checked_prev": ["latex1"]})
    assert at.text_area(key="prop_latex1_text") is not None
    assert at.text_area(key="prop_latex1_help") is not None
    assert at.selectbox(key="prop_latex1_width") is not None
    assert at.number_input(key="prop_latex1_custom_width") is not None
    assert at.number_input(key="prop_latex1_font_size") is not None


def test_latex_custom_width_is_disabled_unless_custom_width_mode_selected() -> None:
    widget = WidgetInstance(
        id="latex2",
        type="latex",
        props={
            "text": r"x^2 + y^2 = z^2",
            "help": "",
            "width": "stretch",
            "custom_width": 320,
            "font_size": 16,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "latex2", "hierarchy_checked_prev": ["latex2"]})
    assert at.number_input(key="prop_latex2_custom_width").proto.disabled is True

    at.selectbox(key="prop_latex2_width").select("custom")
    at = at.run(timeout=15)
    assert at.number_input(key="prop_latex2_custom_width").proto.disabled is False


def test_help_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="help1",
        type="help",
        props={
            "text": "help text",
            "width": "stretch",
            "custom_width": 320,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "help1", "hierarchy_checked_prev": ["help1"]})
    assert at.text_input(key="prop_help1_text") is not None
    assert at.selectbox(key="prop_help1_width") is not None
    assert at.number_input(key="prop_help1_custom_width") is not None


def test_help_custom_width_is_disabled_unless_custom_width_mode_selected() -> None:
    widget = WidgetInstance(
        id="help2",
        type="help",
        props={
            "text": "help text",
            "width": "stretch",
            "custom_width": 320,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "help2", "hierarchy_checked_prev": ["help2"]})
    assert at.number_input(key="prop_help2_custom_width").proto.disabled is True


def test_metric_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="metric1",
        type="metric",
        props={
            "label": "Metric",
            "value": "0",
            "delta": "",
            "delta_color": "normal",
            "help": "",
            "label_visibility": "visible",
            "border": False,
            "background_color": "#FFFFFF",
            "height": "content",
            "custom_height": 120,
            "width": "stretch",
            "custom_width": 320,
            "chart_data": [],
            "chart_type": "line",
            "delta_arrow": "auto",
            "format": "",
            "delta_description": "",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "metric1", "hierarchy_checked_prev": ["metric1"]})
    assert at.text_input(key="prop_metric1_label") is not None
    assert at.selectbox(key="prop_metric1_delta_color") is not None
    assert at.color_picker(key="prop_metric1_background_color") is not None
    assert at.number_input(key="prop_metric1_custom_width") is not None
    assert at.number_input(key="prop_metric1_custom_height") is not None


def test_json_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="json1",
        type="json",
        props={
            "expanded": "true",
            "custom_expanded": 2,
            "width": "stretch",
            "custom_width": 320,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "json1", "hierarchy_checked_prev": ["json1"]})
    assert at.selectbox(key="prop_json1_expanded") is not None
    assert at.number_input(key="prop_json1_custom_expanded") is not None
    assert at.selectbox(key="prop_json1_width") is not None
    assert at.number_input(key="prop_json1_custom_width") is not None


def test_json_custom_controls_are_disabled_unless_custom_mode_selected() -> None:
    widget = WidgetInstance(
        id="json2",
        type="json",
        props={
            "expanded": "true",
            "custom_expanded": 2,
            "width": "stretch",
            "custom_width": 320,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "json2", "hierarchy_checked_prev": ["json2"]})
    assert at.number_input(key="prop_json2_custom_expanded").proto.disabled is True
    assert at.number_input(key="prop_json2_custom_width").proto.disabled is True

    at.selectbox(key="prop_json2_expanded").select("custom")
    at = at.run(timeout=15)
    at.selectbox(key="prop_json2_width").select("custom")
    at = at.run(timeout=15)

    assert at.number_input(key="prop_json2_custom_expanded").proto.disabled is False
    assert at.number_input(key="prop_json2_custom_width").proto.disabled is False


def test_area_chart_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="area1",
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
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "area1", "hierarchy_checked_prev": ["area1"]})
    assert at.text_input(key="prop_area1_x_label") is not None
    assert at.text_input(key="prop_area1_y_label") is not None
    assert at.selectbox(key="prop_area1_stack") is not None
    assert at.selectbox(key="prop_area1_width") is not None
    assert at.number_input(key="prop_area1_custom_width") is not None
    assert at.selectbox(key="prop_area1_height") is not None
    assert at.number_input(key="prop_area1_custom_height") is not None


def test_area_chart_custom_dimensions_are_disabled_unless_custom_mode_selected() -> None:
    widget = WidgetInstance(
        id="area2",
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
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "area2", "hierarchy_checked_prev": ["area2"]})
    assert at.number_input(key="prop_area2_custom_width").proto.disabled is True
    assert at.number_input(key="prop_area2_custom_height").proto.disabled is True

    at.selectbox(key="prop_area2_width").select("custom")
    at = at.run(timeout=15)
    at.selectbox(key="prop_area2_height").select("custom")
    at = at.run(timeout=15)

    assert at.number_input(key="prop_area2_custom_width").proto.disabled is False
    assert at.number_input(key="prop_area2_custom_height").proto.disabled is False


def test_bar_chart_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="bar1",
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
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "bar1", "hierarchy_checked_prev": ["bar1"]})
    assert at.text_input(key="prop_bar1_x_label") is not None
    assert at.text_input(key="prop_bar1_y_label") is not None
    assert at.checkbox(key="prop_bar1_horizontal") is not None
    assert at.selectbox(key="prop_bar1_sort") is not None
    assert at.text_input(key="prop_bar1_custom_sort") is not None
    assert at.selectbox(key="prop_bar1_stack") is not None
    assert at.selectbox(key="prop_bar1_width") is not None
    assert at.number_input(key="prop_bar1_custom_width") is not None
    assert at.selectbox(key="prop_bar1_height") is not None
    assert at.number_input(key="prop_bar1_custom_height") is not None


def test_bar_chart_custom_controls_are_disabled_unless_custom_mode_selected() -> None:
    widget = WidgetInstance(
        id="bar2",
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
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "bar2", "hierarchy_checked_prev": ["bar2"]})
    assert at.text_input(key="prop_bar2_custom_sort").proto.disabled is True
    assert at.number_input(key="prop_bar2_custom_width").proto.disabled is True
    assert at.number_input(key="prop_bar2_custom_height").proto.disabled is True

    at.selectbox(key="prop_bar2_sort").select("custom")
    at = at.run(timeout=15)
    at.selectbox(key="prop_bar2_width").select("custom")
    at = at.run(timeout=15)
    at.selectbox(key="prop_bar2_height").select("custom")
    at = at.run(timeout=15)

    assert at.text_input(key="prop_bar2_custom_sort").proto.disabled is False
    assert at.number_input(key="prop_bar2_custom_width").proto.disabled is False
    assert at.number_input(key="prop_bar2_custom_height").proto.disabled is False


def test_line_chart_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="line1",
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
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "line1", "hierarchy_checked_prev": ["line1"]})
    assert at.text_input(key="prop_line1_x_label") is not None
    assert at.text_input(key="prop_line1_y_label") is not None
    assert at.selectbox(key="prop_line1_width") is not None
    assert at.number_input(key="prop_line1_custom_width") is not None
    assert at.selectbox(key="prop_line1_height") is not None
    assert at.number_input(key="prop_line1_custom_height") is not None


def test_line_chart_custom_dimensions_are_disabled_unless_custom_mode_selected() -> None:
    widget = WidgetInstance(
        id="line2",
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
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "line2", "hierarchy_checked_prev": ["line2"]})
    assert at.number_input(key="prop_line2_custom_width").proto.disabled is True
    assert at.number_input(key="prop_line2_custom_height").proto.disabled is True

    at.selectbox(key="prop_line2_width").select("custom")
    at = at.run(timeout=15)
    at.selectbox(key="prop_line2_height").select("custom")
    at = at.run(timeout=15)

    assert at.number_input(key="prop_line2_custom_width").proto.disabled is False
    assert at.number_input(key="prop_line2_custom_height").proto.disabled is False



def test_dataframe_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="df1",
        type="dataframe",
        props={
            "width": "stretch",
            "custom_width": 320,
            "height": "auto",
            "custom_height": 320,
            "selection_mode": "multi-row",
            "hide_index": False,
            "row_height": "",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "df1", "hierarchy_checked_prev": ["df1"]})
    assert at.selectbox(key="prop_df1_width") is not None
    assert at.number_input(key="prop_df1_custom_width") is not None
    assert at.selectbox(key="prop_df1_height") is not None
    assert at.number_input(key="prop_df1_custom_height") is not None
    assert at.selectbox(key="prop_df1_selection_mode") is not None
    assert at.checkbox(key="prop_df1_hide_index") is not None
    assert at.text_input(key="prop_df1_row_height") is not None


def test_dataframe_custom_dimensions_are_disabled_unless_custom_mode_selected() -> None:
    widget = WidgetInstance(
        id="df2",
        type="dataframe",
        props={
            "width": "stretch",
            "custom_width": 320,
            "height": "auto",
            "custom_height": 320,
            "selection_mode": "multi-row",
            "hide_index": False,
            "row_height": "",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "df2", "hierarchy_checked_prev": ["df2"]})
    assert at.number_input(key="prop_df2_custom_width").proto.disabled is True
    assert at.number_input(key="prop_df2_custom_height").proto.disabled is True

    at.selectbox(key="prop_df2_width").select("custom")
    at = at.run(timeout=15)
    assert at.number_input(key="prop_df2_custom_width").proto.disabled is False

    at.selectbox(key="prop_df2_height").select("custom")
    at = at.run(timeout=15)
    assert at.number_input(key="prop_df2_custom_height").proto.disabled is False


def test_data_editor_properties_pane_tracks_selected_widget() -> None:
    widget = WidgetInstance(
        id="de1",
        type="data_editor",
        props={
            "width": "stretch",
            "custom_width": 320,
            "height": "auto",
            "custom_height": 320,
            "hide_index": False,
            "num_rows": "fixed",
            "row_height": "",
            "disabled": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "de1", "hierarchy_checked_prev": ["de1"]})
    assert at.selectbox(key="prop_de1_width") is not None
    assert at.number_input(key="prop_de1_custom_width") is not None
    assert at.selectbox(key="prop_de1_height") is not None
    assert at.number_input(key="prop_de1_custom_height") is not None
    assert at.checkbox(key="prop_de1_hide_index") is not None
    assert at.selectbox(key="prop_de1_num_rows") is not None
    assert at.text_input(key="prop_de1_row_height") is not None
    assert at.selectbox(key="prop_de1_disabled") is not None


def test_data_editor_custom_dimensions_are_disabled_unless_custom_mode_selected() -> None:
    widget = WidgetInstance(
        id="de2",
        type="data_editor",
        props={
            "width": "stretch",
            "custom_width": 320,
            "height": "auto",
            "custom_height": 320,
            "hide_index": False,
            "num_rows": "fixed",
            "row_height": "",
            "disabled": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "de2", "hierarchy_checked_prev": ["de2"]})
    assert at.number_input(key="prop_de2_custom_width").proto.disabled is True
    assert at.number_input(key="prop_de2_custom_height").proto.disabled is True

    at.selectbox(key="prop_de2_width").select("custom")
    at = at.run(timeout=15)
    assert at.number_input(key="prop_de2_custom_width").proto.disabled is False

    at.selectbox(key="prop_de2_height").select("custom")
    at = at.run(timeout=15)
    assert at.number_input(key="prop_de2_custom_height").proto.disabled is False


def test_data_editor_disabled_property_updates_from_selectbox() -> None:
    widget = WidgetInstance(
        id="de3",
        type="data_editor",
        props={
            "width": "stretch",
            "custom_width": 320,
            "height": "auto",
            "custom_height": 320,
            "hide_index": False,
            "num_rows": "fixed",
            "row_height": "",
            "disabled": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "de3", "hierarchy_checked_prev": ["de3"]})
    at.selectbox(key="prop_de3_disabled").select("True")
    at = at.run(timeout=15)

    updated_widget = next(item for item in at.session_state["design"].widgets if item.id == "de3")
    assert updated_widget.props["disabled"] is True


def test_app_refreshes_stale_badge_registry_definition() -> None:
    clear_registry()
    register_widget(
        WidgetDefinition(
            type="badge",
            label="Badge",
            props_schema=[PropDefinition("size", "Size", "int", 14)],
            defaults={"size": 14},
            codegen=lambda widget: [],
            render=lambda widget: None,
        )
    )

    widget = WidgetInstance(
        id="badge_stale",
        type="badge",
        props={
            "text": "Badge",
            "size": 14,
            "text_color": "#FFFFFF",
            "background_color": "#2E6CF6",
            "horizontal_alignment": "left",
            "vertical_alignment": "center",
            "style": "normal",
            "bold": False,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "badge_stale", "hierarchy_checked_prev": ["badge_stale"], "registry_ready": True})
    assert at.text_input(key="prop_badge_stale_text") is not None


def _build_design_for_widget(widget_type: str, defaults: dict) -> tuple[Design, str]:
    widget_id = f"{widget_type}_test"
    widget_props = deepcopy(defaults)

    if widget_type == "column":
        container = WidgetInstance(
            id="columns_parent",
            type="columns_container",
            props={"label": "Columns", "background_color": "#FFFFFF", "columns": 1},
        )
        widget = WidgetInstance(
            id=widget_id,
            type="column",
            props=widget_props,
            parent_id=container.id,
        )
        return Design(name="Test", widgets=[container, widget]), widget_id

    widget = WidgetInstance(id=widget_id, type=widget_type, props=widget_props)
    return Design(name="Test", widgets=[widget]), widget_id


def _prop_accessor_name(input_type: str) -> str:
    if input_type in {"text", "options", "date"}:
        return "text_input"
    if input_type == "multiline":
        return "text_area"
    if input_type == "bool":
        return "checkbox"
    if input_type == "bool_select":
        return "selectbox"
    if input_type in {"number", "int"}:
        return "number_input"
    if input_type == "select":
        return "selectbox"
    if input_type == "color":
        return "color_picker"
    raise AssertionError(f"Unsupported prop input type: {input_type}")


def _updated_prop_value(prop: PropDefinition):
    if prop.name == "columns":
        return 2
    if prop.name == "ratio":
        return 2
    if prop.input_type == "text":
        return f"Updated {prop.name}"
    if prop.input_type == "multiline":
        return f"Updated {prop.name}\nline 2"
    if prop.input_type == "bool":
        return not bool(prop.default)
    if prop.input_type == "bool_select":
        return not bool(prop.default)
    if prop.input_type == "number":
        return float(prop.default) + 1.5
    if prop.input_type == "int":
        return int(prop.default) + 1
    if prop.input_type == "options":
        return "Alpha, Beta, Gamma"
    if prop.input_type == "select":
        options = prop.options or []
        for option in options:
            if option != prop.default:
                return option
        return options[0] if options else prop.default
    if prop.input_type == "date":
        return "2026-01-15"
    if prop.input_type == "color":
        return "#123456"
    raise AssertionError(f"Unsupported prop input type: {prop.input_type}")


def _expected_prop_value(prop: PropDefinition, updated_value):
    if prop.input_type == "options":
        return [item.strip() for item in str(updated_value).split(",") if item.strip()]
    if prop.input_type == "number":
        return float(updated_value)
    if prop.input_type == "int":
        return int(updated_value)
    if prop.input_type == "bool":
        return bool(updated_value)
    if prop.input_type == "bool_select":
        return bool(updated_value)
    return updated_value


def _set_widget_control_value(control, prop: PropDefinition, updated_value) -> None:
    if prop.input_type == "bool":
        if updated_value:
            control.check()
        else:
            control.uncheck()
        return
    if prop.input_type == "bool_select":
        control.select("True" if updated_value else "False")
        return
    if prop.input_type == "select":
        control.select(updated_value)
        return
    control.set_value(updated_value)


def test_all_widget_properties_exist_display_and_function() -> None:
    clear_registry()
    register_default_widgets()

    # Widgets using ButtonGroup have a Streamlit test framework bug when value=None
    BUTTON_GROUP_WIDGETS = {"feedback", "pills", "segmented_control"}

    for definition in list_widgets():
        if definition.type in BUTTON_GROUP_WIDGETS:
            continue
        design, selected_id = _build_design_for_widget(definition.type, definition.defaults)

        for prop in definition.props_schema:
            if prop.name == "custom_width":
                selected_widget = next(widget for widget in design.widgets if widget.id == selected_id)
                selected_widget.props["width"] = "custom"
            if prop.name == "custom_height":
                selected_widget = next(widget for widget in design.widgets if widget.id == selected_id)
                selected_widget.props["height"] = "custom"
            if prop.name == "custom_sort":
                selected_widget = next(widget for widget in design.widgets if widget.id == selected_id)
                selected_widget.props["sort"] = "custom"
            if prop.name == "custom_expanded":
                selected_widget = next(widget for widget in design.widgets if widget.id == selected_id)
                selected_widget.props["expanded"] = "custom"

            at = _run_app(
                design,
                {"hierarchy_checked_id": selected_id, "hierarchy_checked_prev": [selected_id]},
            )
            key = f"prop_{selected_id}_{prop.name}"
            accessor_name = _prop_accessor_name(prop.input_type)
            control = getattr(at, accessor_name)(key=key)
            assert control is not None, f"Missing control for {definition.type}.{prop.name}"

            updated_value = _updated_prop_value(prop)
            _set_widget_control_value(control, prop, updated_value)
            at = at.run(timeout=15)

            updated_widget = next(widget for widget in at.session_state["design"].widgets if widget.id == selected_id)
            assert updated_widget.props[prop.name] == _expected_prop_value(prop, updated_value), (
                f"Property {definition.type}.{prop.name} did not update correctly"
            )


def test_single_selection_state_is_one_item() -> None:
    at = _run_app()
    assert "hierarchy_checked_prev" in at.session_state
    checked_prev = at.session_state["hierarchy_checked_prev"]
    assert isinstance(checked_prev, list)
    assert len(checked_prev) <= 1


def test_tree_selection_sets_container_for_columns_container() -> None:
    container = WidgetInstance(id="c_main", type="columns_container", props={"columns": 2})
    column_a = WidgetInstance(id="c_main_col1", type="column", parent_id="c_main")
    column_b = WidgetInstance(id="c_main_col2", type="column", parent_id="c_main")
    design = Design(name="Test", widgets=[container, column_a, column_b])

    at = _run_app(design, {"hierarchy_checked_id": "c_main", "hierarchy_checked_prev": ["c_main"]})
    assert at.session_state["add_to_container"] == "c_main"
    assert at.session_state["target_column_id"] is None


def test_tree_selection_sets_container_for_widget_inside_column() -> None:
    container = WidgetInstance(id="c1", type="columns_container", props={"columns": 1})
    column = WidgetInstance(id="col1", type="column", parent_id="c1")
    child = WidgetInstance(id="w1", type="text_input", props={"label": "A"}, parent_id="col1")
    design = Design(name="Test", widgets=[container, column, child])

    at = _run_app(design, {"hierarchy_checked_id": "w1", "hierarchy_checked_prev": ["w1"]})
    assert at.session_state["add_to_container"] == "c1"
    assert at.session_state["target_column_id"] == "col1"


def test_container_pane_change_updates_selected_id() -> None:
    container = WidgetInstance(id="c2", type="columns_container", props={"columns": 1})
    column = WidgetInstance(id="col2", type="column", parent_id="c2")
    widget = WidgetInstance(id="w2", type="text_input", props={"label": "X"})
    design = Design(name="Test", widgets=[container, column, widget])

    at = _run_app(
        design,
        {
            "selected_id": "w2",
            "add_to_container": "c2",
            "container_pane_prev": MAIN_CONTAINER_ID,
            "suppress_container_pane_sync": False,
        },
    )
    assert at.session_state["selected_id"] == "c2"
    assert at.session_state["hierarchy_checked_id"] == "c2"


def test_main_properties_present_when_main_selected() -> None:
    at = _run_app()
    assert at.selectbox(key="main_screen_width") is not None
    assert at.color_picker(key="main_background_color") is not None
    assert at.text_input(key="main_background_image") is not None


def test_top_level_widget_sets_main_container() -> None:
    widget = WidgetInstance(id="w_top", type="text_input", props={"label": "Top"})
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"hierarchy_checked_id": "w_top", "hierarchy_checked_prev": ["w_top"]})
    assert at.session_state["add_to_container"] == MAIN_CONTAINER_ID
    assert at.session_state["target_container_id"] is None
    assert at.session_state["target_column_id"] is None


def test_container_pane_shows_main_and_container_options() -> None:
    container = WidgetInstance(id="c_opt", type="columns_container", props={"columns": 1})
    column = WidgetInstance(id="c_opt_col", type="column", parent_id="c_opt")
    design = Design(name="Test", widgets=[container, column])

    at = _run_app(design)
    selectbox = at.selectbox(key="add_to_container")
    assert "Main" in selectbox.options
    assert "Columns (c_opt)" in selectbox.options


def test_container_pane_sets_default_target_column_when_not_column_selected() -> None:
    container = WidgetInstance(id="c_def", type="columns_container", props={"columns": 2})
    col1 = WidgetInstance(id="c_def_col1", type="column", parent_id="c_def")
    col2 = WidgetInstance(id="c_def_col2", type="column", parent_id="c_def")
    design = Design(name="Test", widgets=[container, col1, col2])

    at = _run_app(
        design,
        {
            "add_to_container": "c_def",
            "container_pane_prev": MAIN_CONTAINER_ID,
            "suppress_container_pane_sync": False,
        },
    )
    assert at.session_state["hierarchy_checked_id"] == "c_def"
    assert at.session_state["target_column_id"] is None


def test_columns_container_selection_clears_target_column() -> None:
    container = WidgetInstance(id="c_clear", type="columns_container", props={"columns": 1})
    column = WidgetInstance(id="c_clear_col", type="column", parent_id="c_clear")
    design = Design(name="Test", widgets=[container, column])

    at = _run_app(design, {"hierarchy_checked_id": "c_clear", "hierarchy_checked_prev": ["c_clear"]})
    assert at.session_state["target_column_id"] is None


def test_properties_pane_guidance_when_no_selection() -> None:
    widget = WidgetInstance(id="w_no", type="text_input", props={"label": "Name"})
    design = Design(name="Test", widgets=[widget])

    at = _run_app(design, {"selected_id": None, "hierarchy_checked_id": None, "hierarchy_checked_prev": []})
    infos = at.get("info")
    assert infos
    assert "Select a widget" in infos[0].value


def test_no_chain_reruns_on_idle_state() -> None:
    at = AppTest.from_file("app.py").run(timeout=15)
    initial_selected = at.session_state["selected_id"]
    initial_checked = at.session_state["hierarchy_checked_id"]
    initial_tree_version = at.session_state["hierarchy_tree_version"]
    initial_container_prev = at.session_state["container_pane_prev"]

    at = at.run(timeout=15)
    assert at.session_state["selected_id"] == initial_selected
    assert at.session_state["hierarchy_checked_id"] == initial_checked
    assert at.session_state["hierarchy_tree_version"] == initial_tree_version
    assert at.session_state["container_pane_prev"] == initial_container_prev
