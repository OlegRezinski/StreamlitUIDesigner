from __future__ import annotations

from streamlit.testing.v1 import AppTest


def test_ui2_text_elements_popover_does_not_include_html() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    button_labels = [button.label for button in at.button]
    assert "st.html" not in button_labels


def test_ui2_text_elements_popover_adds_caption_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    caption_button = at.button(key="ui2_add_Text elements_caption")
    assert caption_button is not None
    assert caption_button.label == "st.caption"
    assert caption_button.disabled is False

    caption_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "caption"
    assert widget.props["text"] == "Caption"


def test_ui2_text_elements_popover_adds_code_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    code_button = at.button(key="ui2_add_Text elements_code")
    assert code_button is not None
    assert code_button.label == "st.code"
    assert code_button.disabled is False

    code_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "code"
    assert widget.props["width"] == "stretch"
    assert widget.props["height"] == "content"


def test_ui2_text_elements_popover_adds_divider_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    divider_button = at.button(key="ui2_add_Text elements_divider")
    assert divider_button is not None
    assert divider_button.label == "st.divider"
    assert divider_button.disabled is False

    divider_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "divider"
    assert widget.props["line_width"] == 1
    assert widget.props["color"] == "#D9D9D9"


def test_ui2_text_elements_popover_adds_echo_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    echo_button = at.button(key="ui2_add_Text elements_echo")
    assert echo_button is not None
    assert echo_button.label == "st.echo"
    assert echo_button.disabled is False

    echo_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "echo"
    assert widget.props["code_location"] == "above"


def test_ui2_text_elements_popover_adds_latex_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    latex_button = at.button(key="ui2_add_Text elements_latex")
    assert latex_button is not None
    assert latex_button.label == "st.latex"
    assert latex_button.disabled is False

    latex_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "latex"
    assert widget.props["width"] == "stretch"
    assert "text" in widget.props


def test_ui2_text_elements_popover_adds_help_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    help_button = at.button(key="ui2_add_Text elements_help")
    assert help_button is not None
    assert help_button.label == "st.help"
    assert help_button.disabled is False

    help_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "help"
    assert widget.props["width"] == "stretch"
    assert widget.props["custom_width"] == 320


def test_ui2_data_elements_popover_adds_dataframe_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    dataframe_button = at.button(key="ui2_add_Data elements_dataframe")
    assert dataframe_button is not None
    assert dataframe_button.label == "st.dataframe"
    assert dataframe_button.disabled is False

    dataframe_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "dataframe"
    assert widget.props["width"] == "stretch"
    assert widget.props["height"] == "auto"
    assert widget.props["selection_mode"] == "multi-row"


def test_ui2_data_elements_popover_adds_data_editor_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    data_editor_button = at.button(key="ui2_add_Data elements_data_editor")
    assert data_editor_button is not None
    assert data_editor_button.label == "st.data_editor"
    assert data_editor_button.disabled is False

    data_editor_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "data_editor"
    assert widget.props["width"] == "stretch"
    assert widget.props["height"] == "auto"
    assert widget.props["num_rows"] == "fixed"
    assert widget.props["disabled"] is False


def test_ui2_data_elements_popover_adds_metric_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    metric_button = at.button(key="ui2_add_Data elements_metric")
    assert metric_button is not None
    assert metric_button.label == "st.metric"
    assert metric_button.disabled is False

    metric_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "metric"
    assert widget.props["label"] == "Metric 1"
    assert widget.props["width"] == "stretch"
    assert widget.props["height"] == "content"


def test_ui2_data_elements_popover_adds_json_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    json_button = at.button(key="ui2_add_Data elements_json")
    assert json_button is not None
    assert json_button.label == "st.json"
    assert json_button.disabled is False

    json_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "json"
    assert widget.props["expanded"] == "true"
    assert widget.props["custom_expanded"] == 2
    assert widget.props["width"] == "stretch"
    assert widget.props["custom_width"] == 320


def test_ui2_chart_elements_popover_adds_area_chart_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    area_chart_button = at.button(key="ui2_add_Chart elements_area_chart")
    assert area_chart_button is not None
    assert area_chart_button.label == "st.area_chart"
    assert area_chart_button.disabled is False

    area_chart_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "area_chart"
    assert widget.props["stack"] == "none"
    assert widget.props["width"] == "stretch"
    assert widget.props["height"] == "content"


def test_ui2_chart_elements_popover_adds_bar_chart_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    bar_chart_button = at.button(key="ui2_add_Chart elements_bar_chart")
    assert bar_chart_button is not None
    assert bar_chart_button.label == "st.bar_chart"
    assert bar_chart_button.disabled is False

    bar_chart_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    assert len(design.widgets) == 1

    widget = design.widgets[0]
    assert widget.type == "bar_chart"
    assert widget.props["horizontal"] is False
    assert widget.props["sort"] == "true"
    assert widget.props["stack"] == "none"
    assert widget.props["width"] == "stretch"
    assert widget.props["height"] == "content"


def test_ui2_layouts_popover_adds_tabs_widget() -> None:
    at = AppTest.from_file("UI_2.py").run(timeout=20)

    tabs_button = at.button(key="ui2_add_Layouts and containers_tabs")
    assert tabs_button is not None
    assert tabs_button.label == "st.tabs"
    assert tabs_button.disabled is False

    tabs_button.click()
    at = at.run(timeout=20)

    design = at.session_state["design"]
    tabs_widgets = [widget for widget in design.widgets if widget.type == "tabs"]
    tab_children = [widget for widget in design.widgets if widget.type == "tab"]

    assert len(tabs_widgets) == 1
    assert len(tab_children) == 2

    widget = tabs_widgets[0]
    assert widget.props["tabs"] == 2
    assert widget.props["width"] == "stretch"
    assert widget.props["custom_width"] == 320
    assert widget.props["default"] == ""
