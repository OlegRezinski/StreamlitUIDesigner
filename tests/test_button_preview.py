from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from designer.models import Design, WidgetInstance


def _find_markdown_with(at: AppTest, needle: str) -> str:
    candidate = ""
    for md in at.markdown:
        if needle in md.value:
            if "<style>" in md.value:
                return md.value
            candidate = md.value
    return candidate


def _sample_code_text() -> str:
    sample_path = Path(__file__).resolve().parents[1] / "samples" / "Code_sample.py"
    return sample_path.read_text(encoding="utf-8").rstrip()


def test_button_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="btn-props",
        type="button",
        props={
            "label": "Preview Button",
            "background_color": "#123456",
            "text_color": "#ABCDEF",
            "width": "120px",
            "height": "40px",
            "expand": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(btn.label == "Preview Button" for btn in at.button)

    css = _find_markdown_with(at, "st-key-preview_button_btn-props")
    assert css
    assert "background-color: #123456" in css
    assert "color: #ABCDEF" in css
    assert "width: 120px" in css
    assert "height: 40px" in css


def test_button_preview_expand_sets_full_width() -> None:
    widget = WidgetInstance(
        id="btn-expand",
        type="button",
        props={
            "label": "Expand Button",
            "background_color": "#111111",
            "text_color": "#FFFFFF",
            "width": "90px",
            "height": "30px",
            "expand": True,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(btn.label == "Expand Button" for btn in at.button)

    css = _find_markdown_with(at, "st-key-preview_button_btn-expand")
    assert css
    assert "width: 100%" in css


def test_text_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="text-props",
        type="text",
        props={
            "text": "Preview Text",
            "size": 18,
            "color": "#112233",
            "horizontal_alignment": "center",
            "vertical_alignment": "bottom",
            "style": "serif",
            "bold": True,
            "italic": True,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(text.value == "Preview Text" for text in at.text)

    css = _find_markdown_with(at, ".st-key-preview_text_text-props [data-testid=\"stText\"]")
    assert css
    assert "font-size: 18px" in css
    assert "color: #112233" in css
    assert "justify-content: center" in css
    assert "align-items: flex-end" in css
    assert "font-family: serif" in css
    assert "font-weight: 700" in css
    assert "font-style: italic" in css


def test_title_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="title-props",
        type="title",
        props={
            "text": "Designer Title",
            "size": 46,
            "color": "#345678",
            "horizontal_alignment": "center",
            "vertical_alignment": "bottom",
            "style": "monospace",
            "bold": False,
            "italic": True,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(title.value == "Designer Title" for title in at.title)

    css = _find_markdown_with(at, ".st-key-preview_title_title-props [data-testid=\"stHeading\"] h1")
    assert css
    assert "font-size: 46px" in css
    assert "color: #345678" in css
    assert "justify-content: center" in css
    assert "align-items: flex-end" in css
    assert "font-family: monospace" in css
    assert "font-weight: 400" in css
    assert "font-style: italic" in css


def test_header_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="header-props",
        type="header",
        props={
            "text": "Preview Header",
            "size": 36,
            "color": "#56789A",
            "horizontal_alignment": "right",
            "vertical_alignment": "top",
            "style": "serif",
            "bold": True,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(header.value == "Preview Header" for header in at.header)

    css = _find_markdown_with(at, ".st-key-preview_header_header-props [data-testid=\"stHeading\"] h2")
    assert css
    assert "font-size: 36px" in css
    assert "color: #56789A" in css
    assert "justify-content: flex-end" in css
    assert "align-items: flex-start" in css
    assert "font-family: serif" in css
    assert "font-weight: 700" in css
    assert "font-style: normal" in css


def test_subheader_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="subheader-props",
        type="subheader",
        props={
            "text": "Preview Subheader",
            "size": 31,
            "color": "#6789AB",
            "horizontal_alignment": "center",
            "vertical_alignment": "bottom",
            "style": "monospace",
            "bold": False,
            "italic": True,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(subheader.value == "Preview Subheader" for subheader in at.subheader)

    css = _find_markdown_with(at, ".st-key-preview_subheader_subheader-props [data-testid=\"stHeading\"] h3")
    assert css
    assert "font-size: 31px" in css
    assert "color: #6789AB" in css
    assert "justify-content: center" in css
    assert "align-items: flex-end" in css
    assert "font-family: monospace" in css
    assert "font-weight: 400" in css
    assert "font-style: italic" in css


def test_markdown_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="markdown-props",
        type="markdown",
        props={
            "text": "Preview **Markdown**",
            "size": 19,
            "color": "#789ABC",
            "horizontal_alignment": "right",
            "vertical_alignment": "top",
            "style": "serif",
            "bold": True,
            "italic": False,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any("Preview **Markdown**" in md.value for md in at.markdown if "<style>" not in md.value)

    css = _find_markdown_with(at, ".st-key-preview_markdown_markdown-props [data-testid=\"stMarkdown\"]")
    assert css
    assert "font-size: 19px" in css
    assert "color: #789ABC" in css
    assert "justify-content: flex-start" in css
    assert "align-items: flex-end" in css
    assert "font-family: serif" in css
    assert "font-weight: 700" in css
    assert "font-style: normal" in css


def test_badge_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="badge-props",
        type="badge",
        props={
            "text": "Preview Badge",
            "size": 17,
            "text_color": "#FAFBFC",
            "background_color": "#456789",
            "horizontal_alignment": "center",
            "vertical_alignment": "bottom",
            "style": "monospace",
            "bold": True,
            "italic": True,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(":blue-badge[Preview Badge]" == md.value for md in at.markdown)

    css = _find_markdown_with(at, ".st-key-preview_badge_badge-props [data-testid=\"stMarkdown\"]")
    assert css
    assert "background-color: #456789" in css
    assert "color: #FAFBFC" in css
    assert "font-size: 17px" in css
    assert "align-items: center" in css
    assert "justify-content: flex-end" in css
    assert "font-family: monospace" in css
    assert "font-weight: 700" in css
    assert "font-style: italic" in css


def test_caption_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="caption-props",
        type="caption",
        props={
            "text": "Preview Caption",
            "size": 15,
            "color": "#89ABCD",
            "horizontal_alignment": "center",
            "vertical_alignment": "top",
            "style": "serif",
            "bold": True,
            "italic": True,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(caption.value == "Preview Caption" for caption in at.caption)

    css = _find_markdown_with(at, '.st-key-preview_caption_caption-props [data-testid="stCaptionContainer"]')
    assert css
    assert "font-size: 15px" in css
    assert "color: #89ABCD" in css
    assert "justify-content: flex-start" in css
    assert "align-items: center" in css
    assert "font-family: serif" in css
    assert "font-weight: 700" in css
    assert "font-style: italic" in css


def test_code_preview_uses_sample_code_file() -> None:
    widget = WidgetInstance(
        id="code-props",
        type="code",
        props={
            "width": "content",
            "height": "stretch",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    sample_code = _sample_code_text()
    assert any(code.value == sample_code for code in at.code)


def test_divider_preview_reflects_all_properties() -> None:
    widget = WidgetInstance(
        id="divider-props",
        type="divider",
        props={
            "line_width": 4,
            "color": "#C0FFEE",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert len(at.divider) == 1

    css = _find_markdown_with(at, ".st-key-preview_divider_divider-props hr")
    assert css
    assert "border-top: 4px solid #C0FFEE" in css


def test_echo_preview_code_location_above_renders_code_before_output() -> None:
    widget = WidgetInstance(
        id="echo-above",
        type="echo",
        props={
            "code_location": "above",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    main_items = [(type(x).__name__, getattr(x, "value", None)) for x in at.main]
    code_index = next(i for i, item in enumerate(main_items) if item == ("Code", "_render_echo_sample_body()"))
    output_index = next(i for i, item in enumerate(main_items) if item == ("Markdown", "Echo output"))
    assert code_index < output_index


def test_echo_preview_code_location_below_renders_code_after_output() -> None:
    widget = WidgetInstance(
        id="echo-below",
        type="echo",
        props={
            "code_location": "below",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    main_items = [(type(x).__name__, getattr(x, "value", None)) for x in at.main]
    code_index = next(i for i, item in enumerate(main_items) if item == ("Code", "_render_echo_sample_body()"))
    output_index = next(i for i, item in enumerate(main_items) if item == ("Markdown", "Echo output"))
    assert output_index < code_index


def test_latex_preview_reflects_properties() -> None:
    widget = WidgetInstance(
        id="latex-props",
        type="latex",
        props={
            "text": r"\\int_0^1 x^2 dx",
            "help": "Helpful **tooltip**",
            "width": "custom",
            "custom_width": 280,
            "font_size": 22,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert any(r"\\int_0^1 x^2 dx" in latex.value for latex in at.latex)
    assert any("Helpful **tooltip**" in str(latex.proto) for latex in at.latex)

    css = _find_markdown_with(at, ".st-key-preview_latex_latex-props .katex")
    assert css
    assert "font-size: 22px" in css


def test_help_preview_renders_real_help_output() -> None:
    widget = WidgetInstance(
        id="help-props",
        type="help",
        props={
            "text": "help text",
            "width": "custom",
            "custom_width": 280,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    main_items = [(type(x).__name__, getattr(x, "value", None)) for x in at.main]
    assert ("UnknownElement", "'help text'") in main_items


def test_dataframe_preview_reflects_properties() -> None:
    widget = WidgetInstance(
        id="dataframe-props",
        type="dataframe",
        props={
            "width": "custom",
            "custom_width": 360,
            "height": "stretch",
            "custom_height": 240,
            "selection_mode": "single-row",
            "hide_index": True,
            "row_height": "30",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert len(at.dataframe) == 1
    assert at.dataframe[0].value.to_dict("list") == {
        "Name": ["Bob", "Alice", "James"],
        "Age": [25, 35, 45],
        "Country": ["USA", "England", "Australia"],
    }

    css = _find_markdown_with(at, '.st-key-preview_dataframe_dataframe-props [data-testid="stDataFrame"]')
    assert css
    assert "height: 100%" in css


def test_data_editor_preview_reflects_properties() -> None:
    widget = WidgetInstance(
        id="data-editor-props",
        type="data_editor",
        props={
            "width": "custom",
            "custom_width": 360,
            "height": "stretch",
            "custom_height": 240,
            "hide_index": True,
            "num_rows": "add",
            "row_height": "30",
            "disabled": ["Name", 0, "_index"],
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert len(at.dataframe) == 1
    assert at.dataframe[0].value.to_dict("list") == {
        "Name": ["Bob", "Alice", "James"],
        "Age": [25, 35, 45],
        "Country": ["USA", "England", "Australia"],
    }

    css = _find_markdown_with(at, '.st-key-preview_data_editor_data-editor-props [data-testid="stDataFrame"]')
    assert css
    assert "height: 100%" in css


def test_metric_preview_reflects_background_color() -> None:
    widget = WidgetInstance(
        id="metric-bg",
        type="metric",
        props={
            "label": "Metric",
            "value": "10",
            "delta": "1",
            "delta_color": "normal",
            "help": "",
            "label_visibility": "visible",
            "border": True,
            "background_color": "#224466",
            "height": "content",
            "custom_height": 120,
            "width": "stretch",
            "custom_width": 320,
            "chart_data": [],
            "chart_type": "line",
            "delta_arrow": "auto",
            "format": "None",
            "delta_description": "",
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    css = _find_markdown_with(at, '.st-key-preview_metric_metric-bg [data-testid="stMetric"]')
    assert css
    assert "background-color: #224466" in css


def test_json_preview_uses_sample_json_data() -> None:
    widget = WidgetInstance(
        id="json-props",
        type="json",
        props={
            "expanded": "custom",
            "custom_expanded": 2,
            "width": "custom",
            "custom_width": 280,
        },
    )
    design = Design(name="Test", widgets=[widget])

    at = AppTest.from_file("app.py")
    at.session_state["design"] = design
    at = at.run(timeout=15)

    assert len(at.json) == 1
    value = at.json[0].value
    assert '"foo": "bar"' in value
    assert '"level1"' in value



