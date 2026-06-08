from __future__ import annotations

import ast
import inspect
import json
from datetime import date
from pathlib import Path
from typing import Any, List
import html

import streamlit as st

from .models import PropDefinition, WidgetDefinition, WidgetInstance
from .registry import has_widget, register_widget


_SAMPLE_CODE_PATH = Path(__file__).resolve().parents[1] / "samples" / "Code_sample.py"
_SAMPLE_PDF_PATH = Path(__file__).resolve().parents[1] / "static" / "pdf_sample.pdf"
_FALLBACK_SAMPLE_CODE = 'def hello():\n    print("Hello, Streamlit!")'
_SAMPLE_CHART_DATA_PATH = Path(__file__).resolve().parents[1] / "samples" / "Chart_data_sample.py"
_SAMPLE_JSON_PATH = Path(__file__).resolve().parents[1] / "samples" / "Json_sample.json"
_FALLBACK_SAMPLE_JSON_DATA = {
    "foo": "bar",
    "stuff": ["stuff 1", "stuff 2", "stuff 3"],
    "level1": {"level2": {"level3": {"a": "b"}}},
}
_SAMPLE_DATAFRAME_DATA = {
    "Name": ["Bob", "Alice", "James"],
    "Age": [25, 35, 45],
    "Country": ["USA", "England", "Australia"],
}
_FALLBACK_AREA_CHART_DATA = {
    "a": [0.12, -0.33, 0.44, 0.18, -0.07],
    "b": [-0.21, 0.15, -0.12, 0.31, 0.22],
    "c": [0.08, 0.21, -0.19, 0.27, -0.11],
}
_DATAFRAME_SELECTION_MODES = [
    "single-row",
    "multi-row",
    "single-column",
    "multi-column",
    "single-cell",
    "multi-cell",
]
_DATA_EDITOR_NUM_ROWS = ["fixed", "dynamic", "add", "delete"]
_ST_METRIC_PARAMS = set(inspect.signature(st.metric).parameters.keys())
_ST_BUTTON_PARAMS = set(inspect.signature(st.button).parameters.keys())
_SAMPLE_MAP_DATA = {
    "lat": [37.7749, 34.0522, 40.7128, 41.8781, 29.7604],
    "lon": [-122.4194, -118.2437, -74.0060, -87.6298, -95.3698],
}
_FALLBACK_SCATTER_CHART_DATA = {
    "x": [1.2, 2.5, 3.1, 4.8, 5.3, 6.7, 7.2, 8.0, 9.4, 10.1],
    "y": [2.3, 3.1, 1.8, 5.2, 4.0, 6.1, 5.5, 7.8, 6.9, 8.5],
}
_SAMPLE_GRAPHVIZ_DOT = """digraph {
    run -> intr
    intr -> runbl
    runbl -> run
    run -> kernel
    kernel -> zombie
    kernel -> sleep
    kernel -> runmem
    sleep -> swap
    swap -> runswap
    runswap -> new
    runswap -> runmem
    new -> runmem
    sleep -> runmem
}"""


def _ensure_options(options: List[str]) -> List[str]:
    cleaned = [opt.strip() for opt in options if opt.strip()]
    return cleaned or ["Option 1", "Option 2"]


def _clamp_index(index: Any, options: List[str]) -> int:
    try:
        idx = int(index)
    except (TypeError, ValueError):
        idx = 0
    if not options:
        return 0
    return max(0, min(idx, len(options) - 1))


def _clamp_value(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def _date_from_iso(value: Any) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    return date.today()


def _safe_step(value: Any) -> float:
    try:
        step = float(value)
    except (TypeError, ValueError):
        return 1.0
    return step if step > 0 else 1.0


def _button_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        parsed = _safe_int(custom_width, 200)
        return parsed if parsed > 0 else "content"
    return "content"


def _button_color_value(value: Any) -> str:
    text = str(value).strip()
    return text if text else ""


def _button_css_rule(button_key: Any, background_color: Any, text_color: Any) -> str:
    bg = _button_color_value(background_color)
    fg = _button_color_value(text_color)
    if not bg and not fg:
        return ""

    declarations: list[str] = []
    if bg:
        declarations.append(f"background-color: {html.escape(bg, quote=True)} !important;")
    if fg:
        declarations.append(f"color: {html.escape(fg, quote=True)} !important;")

    key = html.escape(str(button_key), quote=True)
    return f".st-key-{key} button {{ {' '.join(declarations)} }}"


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _single_quoted_python_string(value: Any) -> str:
    text = str(value)
    escaped = (
        text.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f"'{escaped}'"


def _sample_code_text() -> str:
    try:
        text = _SAMPLE_CODE_PATH.read_text(encoding="utf-8").rstrip()
    except OSError:
        return _FALLBACK_SAMPLE_CODE
    return text or _FALLBACK_SAMPLE_CODE


def _sample_dataframe_data() -> dict[str, list[Any]]:
    return {key: list(values) for key, values in _SAMPLE_DATAFRAME_DATA.items()}


def _sample_json_data() -> Any:
    try:
        text = _SAMPLE_JSON_PATH.read_text(encoding="utf-8")
    except OSError:
        return dict(_FALLBACK_SAMPLE_JSON_DATA)

    stripped = text.strip()
    if not stripped:
        return dict(_FALLBACK_SAMPLE_JSON_DATA)

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Support sample file content that wraps JSON in a Python st.json(...) snippet.
    try:
        module = ast.parse(text)
    except SyntaxError:
        return dict(_FALLBACK_SAMPLE_JSON_DATA)

    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else (func.id if isinstance(func, ast.Name) else "")
        if name != "json" or not node.args:
            continue
        try:
            return ast.literal_eval(node.args[0])
        except (ValueError, SyntaxError):
            continue

    return dict(_FALLBACK_SAMPLE_JSON_DATA)


def _sample_area_chart_data() -> Any:
    try:
        from samples.Chart_data_sample import get_chart_data_sample

        return get_chart_data_sample()
    except Exception:
        return {key: list(values) for key, values in _FALLBACK_AREA_CHART_DATA.items()}


def _code_dimension_option(value: Any, default: str) -> str:
    normalized = str(value).strip().lower()
    return normalized if normalized in {"content", "stretch"} else default


def _latex_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        try:
            parsed = int(custom_width)
        except (TypeError, ValueError):
            return "stretch"
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _latex_help(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _dataframe_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        try:
            parsed = int(custom_width)
        except (TypeError, ValueError):
            return "stretch"
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _dataframe_height_value(height_mode: Any, custom_height: Any) -> str | int:
    normalized = str(height_mode).strip().lower()
    if normalized in {"auto", "content", "stretch"}:
        return "auto"
    if normalized == "custom":
        try:
            parsed = int(custom_height)
        except (TypeError, ValueError):
            return "auto"
        return parsed if parsed > 0 else "auto"
    return "auto"


def _dataframe_selection_mode(value: Any) -> str:
    normalized = str(value).strip().lower()
    return normalized if normalized in _DATAFRAME_SELECTION_MODES else "multi-row"


def _dataframe_row_height_value(value: Any) -> int | None:
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    try:
        parsed = int(text)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _data_editor_num_rows(value: Any) -> str:
    normalized = str(value).strip().lower()
    return normalized if normalized in _DATA_EDITOR_NUM_ROWS else "fixed"


def _normalize_data_editor_disabled_items(values: Any) -> list[str | int]:
    if isinstance(values, (str, bytes)):
        source = [values]
    else:
        try:
            source = list(values)
        except TypeError:
            source = [values]

    normalized: list[str | int] = []
    for item in source:
        if isinstance(item, bool):
            normalized.append(str(item))
            continue
        if isinstance(item, int):
            normalized.append(item)
            continue
        text = str(item).strip().strip("\"'")
        if not text:
            continue
        try:
            normalized.append(int(text))
        except ValueError:
            normalized.append(text)
    return normalized


def parse_data_editor_disabled(value: Any) -> bool | list[str | int]:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (list, tuple, set)):
        items = _normalize_data_editor_disabled_items(value)
        return items or False

    text = str(value).strip()
    if not text:
        return False

    lowered = text.lower()
    if lowered in {"false", "none", "no", "off"}:
        return False
    if lowered in {"true", "yes", "on"}:
        return True

    if text[:1] in "[({":
        try:
            parsed = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            parsed = None
        else:
            return parse_data_editor_disabled(parsed)

    items = _normalize_data_editor_disabled_items(text.replace("\n", ",").split(","))
    return items or False


def format_data_editor_disabled(value: Any) -> str:
    parsed = parse_data_editor_disabled(value)
    if isinstance(parsed, bool):
        return "True" if parsed else "False"
    return ", ".join(str(item) for item in parsed)


def _help_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        try:
            parsed = int(custom_width)
        except (TypeError, ValueError):
            return "stretch"
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _metric_scalar_value(value: Any, *, allow_none: bool) -> int | float | str | None:
    if value is None:
        return None if allow_none else ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return value

    text = str(value).strip()
    if not text:
        return None if allow_none else ""
    if allow_none and text.lower() in {"none", "null"}:
        return None

    try:
        if any(ch in text for ch in (".", "e", "E")):
            return float(text)
        return int(text)
    except ValueError:
        return text


def _metric_text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    return text


def _metric_chart_data(value: Any) -> list[float] | None:
    if value is None:
        return None
    if isinstance(value, (str, bytes)):
        source = str(value).replace("\n", ",").split(",")
    else:
        try:
            source = list(value)
        except TypeError:
            source = [value]

    parsed: list[float] = []
    for item in source:
        text = str(item).strip()
        if not text:
            continue
        try:
            parsed.append(float(text))
        except ValueError:
            continue
    return parsed or None


def _metric_enum(value: Any, options: list[str], default: str) -> str:
    normalized = str(value).strip().lower()
    return normalized if normalized in options else default


def _json_expanded_value(expanded_mode: Any, custom_expanded: Any) -> bool | int:
    if isinstance(expanded_mode, bool):
        return expanded_mode
    if isinstance(expanded_mode, int):
        return max(0, expanded_mode)

    normalized = str(expanded_mode).strip().lower()
    if normalized == "custom":
        return max(0, _safe_int(custom_expanded, 2))
    if normalized in {"false", "collapsed"}:
        return False
    if normalized in {"true", "expanded"}:
        return True

    try:
        return max(0, int(normalized))
    except ValueError:
        return True


def _json_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized in {"contain", "content"}:
        return "content"
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _area_chart_optional_text(value: Any) -> str | None:
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    return text


def _area_chart_y_value(value: Any) -> str | list[str] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        result = [str(item).strip() for item in value if str(item).strip()]
        if not result:
            return None
        return result[0] if len(result) == 1 else result

    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    items = [item.strip() for item in text.replace("\n", ",").split(",") if item.strip()]
    if not items:
        return None
    return items[0] if len(items) == 1 else items


def _area_chart_color_value(value: Any) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            parsed = None
        if isinstance(parsed, (list, tuple)):
            result = [str(item).strip() for item in parsed if str(item).strip()]
            return result or None
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        return None
    return parts[0] if len(parts) == 1 else parts


def _area_chart_stack_value(value: Any) -> bool | str | None:
    normalized = str(value).strip().lower()
    if normalized in {"", "none", "null"}:
        return None
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return normalized if normalized in {"normalize", "center"} else None


def _area_chart_dimension_value(mode: Any, custom_value: Any, default: str) -> str | int:
    normalized = str(mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        parsed = _safe_int(custom_value, 320)
        return parsed if parsed > 0 else default
    return default


def _map_dimension_value(mode: Any, custom_value: Any, default: str | int) -> str | int:
    """Return dimension for st.map (supports 'stretch' or int)."""
    normalized = str(mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        parsed = _safe_int(custom_value, 500)
        return parsed if parsed > 0 else default
    return default


def _bar_chart_horizontal_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def _bar_chart_sort_value(sort_mode: Any, custom_sort: Any) -> bool | str:
    if isinstance(sort_mode, bool):
        return sort_mode

    normalized = str(sort_mode).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    if normalized == "custom":
        custom_value = _area_chart_optional_text(custom_sort)
        return custom_value if custom_value is not None else True

    text = str(sort_mode).strip()
    return text if text else True


def _bar_chart_stack_value(value: Any) -> bool | str | None:
    normalized = str(value).strip().lower()
    if normalized in {"", "none", "null"}:
        return None
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return normalized if normalized in {"layered", "normalize", "center"} else None


def _area_chart_codegen_data_literal() -> dict[str, list[float]]:
    data = _sample_area_chart_data()
    if hasattr(data, "to_dict"):
        try:
            raw = data.to_dict(orient="list")
        except TypeError:
            raw = data.to_dict()
    elif isinstance(data, dict):
        raw = data
    else:
        return {key: list(values) for key, values in _FALLBACK_AREA_CHART_DATA.items()}

    normalized: dict[str, list[float]] = {}
    for key, values in raw.items():
        try:
            iterable = list(values)
        except TypeError:
            iterable = [values]
        numeric: list[float] = []
        for item in iterable:
            try:
                numeric.append(float(item))
            except (TypeError, ValueError):
                continue
        if numeric:
            normalized[str(key)] = numeric

    return normalized or {key: list(values) for key, values in _FALLBACK_AREA_CHART_DATA.items()}


def _echo_code_location(value: Any) -> str:
    normalized = str(value).strip().lower()
    return normalized if normalized in {"above", "below"} else "above"


def _render_echo_sample_body() -> None:
    st.write("Echo output")


def _echo_sample_code_line() -> str:
    return "st.write('Echo output')"


def _text_style(widget: WidgetInstance) -> str:
    size = _safe_int(widget.props.get("size", 16), 16)
    color = str(widget.props.get("color", "#000000")).strip()
    h_align = str(widget.props.get("horizontal_alignment", "left")).strip().lower()
    v_align = str(widget.props.get("vertical_alignment", "center")).strip().lower()
    style = str(widget.props.get("style", "normal")).strip().lower()
    bold = bool(widget.props.get("bold", False))
    italic = bool(widget.props.get("italic", False))

    h_map = {"left": "flex-start", "center": "center", "right": "flex-end"}
    v_map = {"top": "flex-start", "center": "center", "bottom": "flex-end"}
    font_family = "inherit" if style == "normal" else style

    styles = [
        "display: flex",
        f"justify-content: {h_map.get(h_align, 'flex-start')}",
        f"align-items: {v_map.get(v_align, 'center')}",
        "width: fit-content",
        f"font-size: {size}px",
        f"color: {color}",
        f"font-weight: {'700' if bold else '400'}",
        f"font-style: {'italic' if italic else 'normal'}",
        f"font-family: {font_family}",
        f"min-height: {max(size, 12)}px",
    ]
    return "; ".join(styles)


def _heading_style(widget: WidgetInstance, default_size: int, default_bold: bool = True) -> str:
    size = _safe_int(widget.props.get("size", default_size), default_size)
    color = str(widget.props.get("color", "#000000")).strip()
    h_align = str(widget.props.get("horizontal_alignment", "left")).strip().lower()
    v_align = str(widget.props.get("vertical_alignment", "center")).strip().lower()
    style = str(widget.props.get("style", "normal")).strip().lower()
    bold = bool(widget.props.get("bold", default_bold))
    italic = bool(widget.props.get("italic", False))

    h_map = {"left": "flex-start", "center": "center", "right": "flex-end"}
    v_map = {"top": "flex-start", "center": "center", "bottom": "flex-end"}
    font_family = "inherit" if style == "normal" else style

    styles = [
        "display: flex",
        f"justify-content: {h_map.get(h_align, 'flex-start')}",
        f"align-items: {v_map.get(v_align, 'center')}",
        "width: 100%",
        "margin: 0 !important",
        f"text-align: {h_align} !important",
        f"min-height: {max(size, 24)}px",
        f"font-size: {size}px !important",
        f"color: {color} !important",
        f"font-weight: {'700' if bold else '400'} !important",
        f"font-style: {'italic' if italic else 'normal'} !important",
        f"font-family: {font_family} !important",
    ]
    return "; ".join(styles)


def _title_style(widget: WidgetInstance) -> str:
    return _heading_style(widget, default_size=40, default_bold=True)


def _header_style(widget: WidgetInstance) -> str:
    return _heading_style(widget, default_size=32, default_bold=True)


def _subheader_style(widget: WidgetInstance) -> str:
    return _heading_style(widget, default_size=28, default_bold=True)


def _markdown_container_style(widget: WidgetInstance) -> str:
    size = _safe_int(widget.props.get("size", 16), 16)
    h_align = str(widget.props.get("horizontal_alignment", "left")).strip().lower()
    v_align = str(widget.props.get("vertical_alignment", "center")).strip().lower()

    h_map = {"left": "flex-start", "center": "center", "right": "flex-end"}
    v_map = {"top": "flex-start", "center": "center", "bottom": "flex-end"}

    styles = [
        "display: flex",
        "flex-direction: column",
        f"justify-content: {v_map.get(v_align, 'center')}",
        f"align-items: {h_map.get(h_align, 'flex-start')}",
        "width: 100%",
        f"text-align: {h_align} !important",
        f"min-height: {max(size, 24)}px",
    ]
    return "; ".join(styles)


def _markdown_content_style(widget: WidgetInstance) -> str:
    size = _safe_int(widget.props.get("size", 16), 16)
    color = str(widget.props.get("color", "#000000")).strip()
    style = str(widget.props.get("style", "normal")).strip().lower()
    bold = bool(widget.props.get("bold", False))
    italic = bool(widget.props.get("italic", False))
    font_family = "inherit" if style == "normal" else style

    styles = [
        f"font-size: {size}px !important",
        f"color: {color} !important",
        f"font-weight: {'700' if bold else '400'} !important",
        f"font-style: {'italic' if italic else 'normal'} !important",
        f"font-family: {font_family} !important",
        "width: 100%",
        "margin-top: 0 !important",
        "margin-bottom: 0 !important",
    ]
    return "; ".join(styles)


def _badge_container_style(widget: WidgetInstance) -> str:
    size = _safe_int(widget.props.get("size", 14), 14)
    h_align = str(widget.props.get("horizontal_alignment", "left")).strip().lower()
    v_align = str(widget.props.get("vertical_alignment", "center")).strip().lower()

    h_map = {"left": "flex-start", "center": "center", "right": "flex-end"}
    v_map = {"top": "flex-start", "center": "center", "bottom": "flex-end"}

    styles = [
        "display: flex",
        "flex-direction: column",
        f"justify-content: {v_map.get(v_align, 'center')}",
        f"align-items: {h_map.get(h_align, 'flex-start')}",
        "width: 100%",
        f"text-align: {h_align} !important",
        f"min-height: {max(size + 8, 24)}px",
    ]
    return "; ".join(styles)


def _badge_content_style(widget: WidgetInstance) -> str:
    size = _safe_int(widget.props.get("size", 14), 14)
    text_color = str(widget.props.get("text_color", "#FFFFFF")).strip()
    background_color = str(widget.props.get("background_color", "#2E6CF6")).strip()
    style = str(widget.props.get("style", "normal")).strip().lower()
    bold = bool(widget.props.get("bold", False))
    italic = bool(widget.props.get("italic", False))
    font_family = "inherit" if style == "normal" else style

    styles = [
        "display: inline-flex !important",
        "align-items: center !important",
        "justify-content: center !important",
        "gap: 0.35rem !important",
        "width: fit-content !important",
        "max-width: 100%",
        "padding: 0.25rem 0.7rem !important",
        "border-radius: 999px !important",
        f"background-color: {background_color} !important",
        f"color: {text_color} !important",
        f"font-size: {size}px !important",
        f"font-weight: {'700' if bold else '400'} !important",
        f"font-style: {'italic' if italic else 'normal'} !important",
        f"font-family: {font_family} !important",
        "line-height: 1.2 !important",
        "margin: 0 !important",
        "border: none !important",
    ]
    return "; ".join(styles)


def _text_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_text" if preview else "text"
    return f"{prefix}_{widget.id}"


def _text_css_rule(container_key: str, style: str) -> str:
    escaped = html.escape(style, quote=True)
    return (
        f".st-key-{container_key} [data-testid=\"stText\"] {{ {escaped} }} "
        f".st-key-{container_key} [data-testid=\"stText\"] * {{ color: inherit !important; font-size: inherit !important; font-weight: inherit !important; font-style: inherit !important; font-family: inherit !important; }}"
    )


def _heading_container_key(kind: str, widget: WidgetInstance, preview: bool = False) -> str:
    prefix = f"preview_{kind}" if preview else kind
    return f"{prefix}_{widget.id}"


def _heading_css_rule(container_key: str, tag: str, style: str) -> str:
    escaped = html.escape(style, quote=True)
    return (
        f".st-key-{container_key} [data-testid=\"stHeading\"] {tag} {{ {escaped} }} "
        f".st-key-{container_key} {tag} {{ {escaped} }}"
    )


def _markdown_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_markdown" if preview else "markdown"
    return f"{prefix}_{widget.id}"


def _caption_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_caption" if preview else "caption"
    return f"{prefix}_{widget.id}"


def _latex_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_latex" if preview else "latex"
    return f"{prefix}_{widget.id}"


def _dataframe_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_dataframe" if preview else "dataframe"
    return f"{prefix}_{widget.id}"


def _data_editor_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_data_editor" if preview else "data_editor"
    return f"{prefix}_{widget.id}"


def _divider_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_divider" if preview else "divider"
    return f"{prefix}_{widget.id}"


def _markdown_css_rule(container_key: str, container_style: str, content_style: str) -> str:
    escaped_container_style = html.escape(container_style, quote=True)
    escaped_content_style = html.escape(content_style, quote=True)
    return (
        f".st-key-{container_key} [data-testid=\"stMarkdown\"] {{ {escaped_container_style} }} "
        f".st-key-{container_key} [data-testid=\"stMarkdownContainer\"], "
        f".st-key-{container_key} [data-testid=\"stMarkdownContainer\"] * {{ {escaped_content_style} }}"
    )


def _caption_css_rule(container_key: str, container_style: str, content_style: str) -> str:
    escaped_container_style = html.escape(container_style, quote=True)
    escaped_content_style = html.escape(content_style, quote=True)
    return (
        f".st-key-{container_key} [data-testid=\"stCaptionContainer\"] {{ {escaped_container_style} }} "
        f".st-key-{container_key} [data-testid=\"stCaptionContainer\"], "
        f".st-key-{container_key} [data-testid=\"stCaptionContainer\"] * {{ {escaped_content_style} }}"
    )


def _latex_css_rule(container_key: str, font_size: int) -> str:
    safe_size = max(8, font_size)
    return f'.st-key-{container_key} .katex {{ font-size: {safe_size}px !important; }}'


def _dataframe_css_rule(container_key: str, height_mode: Any) -> str:
    normalized = str(height_mode).strip().lower()
    if normalized != "stretch":
        return ""
    return f'.st-key-{container_key} [data-testid="stDataFrame"] {{ height: 100% !important; }}'


def _table_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_table" if preview else "table"
    return f"{prefix}_{widget.id}"


def _metric_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_metric" if preview else "metric"
    return f"{prefix}_{widget.id}"


def _metric_css_rule(container_key: str, background_color: Any) -> str:
    color = html.escape(str(background_color).strip() or "#FFFFFF", quote=True)
    return f'.st-key-{container_key} [data-testid="stMetric"] {{ background-color: {color} !important; }}'


def _table_css_rule(
    container_key: str,
    width_mode: Any,
    custom_width: Any,
    height_mode: Any,
    custom_height: Any,
    border: Any,
) -> str:
    selector = f'.st-key-{container_key} [data-testid="stTable"]'
    width = str(width_mode).strip().lower()
    height = str(height_mode).strip().lower()
    custom_width_int = _safe_int(custom_width, 0)
    custom_height_int = _safe_int(custom_height, 0)

    rules: list[str] = []
    if width == "content":
        rules.append(f"{selector} {{ width: fit-content !important; }}")
    elif width == "custom" and custom_width_int > 0:
        rules.append(
            f"{selector} {{ width: {custom_width_int}px !important; max-width: {custom_width_int}px !important; }}"
        )
    else:
        rules.append(f"{selector} {{ width: 100% !important; }}")

    if height == "stretch":
        rules.append(f"{selector} {{ height: 100% !important; }}")
    elif height == "custom" and custom_height_int > 0:
        rules.append(f"{selector} {{ max-height: {custom_height_int}px !important; overflow-y: auto !important; }}")

    if border == "horizontal":
        rules.append(f"{selector} table {{ border-collapse: collapse !important; border-spacing: 0 !important; }}")
        rules.append(
            f"{selector} th, {selector} td {{ border-left: none !important; border-right: none !important; "
            "border-top: 1px solid rgba(49, 51, 63, 0.2) !important; border-bottom: 1px solid rgba(49, 51, 63, 0.2) !important; }}"
        )
    elif border is False:
        rules.append(f"{selector} table, {selector} th, {selector} td {{ border: none !important; }}")

    return " ".join(rules)


def _divider_css_rule(container_key: str, line_width: int, color: str) -> str:
    safe_width = max(1, line_width)
    safe_color = html.escape(str(color).strip() or "#D9D9D9", quote=True)
    return (
        f".st-key-{container_key} hr {{ "
        f"border: 0 !important; border-top: {safe_width}px solid {safe_color} !important; "
        "opacity: 1 !important; margin: 0.25rem 0 !important; width: 100% !important; }}"
    )


def _badge_container_key(widget: WidgetInstance, preview: bool = False) -> str:
    prefix = "preview_badge" if preview else "badge"
    return f"{prefix}_{widget.id}"


def _badge_css_rule(container_key: str, container_style: str, content_style: str) -> str:
    escaped_container_style = html.escape(container_style, quote=True)
    escaped_content_style = html.escape(content_style, quote=True)
    base_selector = f".st-key-{container_key} [data-testid=\"stMarkdownContainer\"]"
    return (
        f".st-key-{container_key} [data-testid=\"stMarkdown\"] {{ {escaped_container_style} }} "
        f"{base_selector} p, {base_selector} > span, {base_selector} p > span {{ {escaped_content_style} }} "
        f"{base_selector} p *, {base_selector} > span *, {base_selector} p > span * {{ color: inherit !important; font-size: inherit !important; font-weight: inherit !important; font-style: inherit !important; font-family: inherit !important; }}"
    )


def _codegen_badge(widget: WidgetInstance) -> List[str]:
    text = widget.props.get("text", "Badge")
    container_style = _badge_container_style(widget)
    content_style = _badge_content_style(widget)
    container_key = _badge_container_key(widget)
    return [
        f"with st.container(key={container_key!r}):",
        f"    st.badge({text!r}, color='blue', width='content')",
        "st.markdown(",
        f"    '<style>{_badge_css_rule(container_key, container_style, content_style)}</style>',",
        "    unsafe_allow_html=True,",
        ")",
    ]


def _codegen_button(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Button")
    custom_key = str(widget.props.get("key", "")).strip()
    key = custom_key if custom_key else widget.id
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    btn_type = widget.props.get("type", "secondary")
    icon = str(widget.props.get("icon", "")).strip()
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "content")
    custom_width = widget.props.get("custom_width", 200)
    background_color = widget.props.get("background_color", "")
    text_color = widget.props.get("text_color", "")
    width = _button_width_value(width_mode, custom_width)
    css_rule = _button_css_rule(key, background_color, text_color)

    lines = [
        "st.button(",
        f"    {label!r},",
        f"    key={key!r},",
    ]
    if help_text is not None:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    type={btn_type!r},")
    if icon:
        lines.append(f"    icon={icon!r},")
        if "icon_position" in _ST_BUTTON_PARAMS:
            lines.append("    icon_position='left',")
    if disabled:
        lines.append(f"    disabled={disabled},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(")")
    if css_rule:
        lines.extend(
            [
                "st.markdown(",
                f"    '<style>{css_rule}</style>',",
                "    unsafe_allow_html=True,",
                ")",
            ]
        )
    return lines


def _codegen_checkbox(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Checkbox")
    checked = bool(widget.props.get("checked", False))
    disabled = bool(widget.props.get("disabled", False))
    label_visibility = "visible" if widget.props.get("label_visibility", True) else "hidden"
    return [
        f"st.checkbox({label!r}, value={checked}, disabled={disabled}, label_visibility={label_visibility!r}, key={widget.id!r})",
    ]


def _codegen_selectbox(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Selectbox")
    raw_options = widget.props.get("options", ["Option 1", "Option 2"])
    if isinstance(raw_options, str):
        options = _ensure_options([opt.strip() for opt in raw_options.split(",")])
    else:
        options = _ensure_options(raw_options)
    index = _clamp_index(widget.props.get("index", 0), options)
    return [
        f"st.selectbox({label!r}, options={options!r}, index={index}, key={widget.id!r})",
    ]


def _codegen_radio(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Radio")
    raw_options = widget.props.get("options", ["Option 1", "Option 2"])
    if isinstance(raw_options, str):
        options = _ensure_options([opt.strip() for opt in raw_options.split(",")])
    else:
        options = _ensure_options(raw_options)
    index = _clamp_index(widget.props.get("index", 0), options)
    return [
        f"st.radio({label!r}, options={options!r}, index={index}, key={widget.id!r})",
    ]


def _codegen_slider(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Slider")
    min_val = float(widget.props.get("min", 0.0))
    max_val = float(widget.props.get("max", 100.0))
    value = _clamp_value(float(widget.props.get("value", 50.0)), min_val, max_val)
    step = _safe_step(widget.props.get("step", 1.0))
    return [
        f"st.slider({label!r}, min_value={min_val}, max_value={max_val}, value={value}, step={step}, key={widget.id!r})",
    ]


def _codegen_number_input(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Number input")
    min_val = float(widget.props.get("min", 0.0))
    max_val = float(widget.props.get("max", 100.0))
    value = _clamp_value(float(widget.props.get("value", 0.0)), min_val, max_val)
    step = _safe_step(widget.props.get("step", 1.0))
    return [
        f"st.number_input({label!r}, min_value={min_val}, max_value={max_val}, value={value}, step={step}, key={widget.id!r})",
    ]


def _codegen_date_input(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Date input")
    value = _date_from_iso(widget.props.get("value", ""))
    return [
        f"st.date_input({label!r}, value={value!r}, key={widget.id!r})",
    ]


def _codegen_file_uploader(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "File uploader")
    raw_types = widget.props.get("types", ["csv", "png"])
    if isinstance(raw_types, str):
        types = [t.strip() for t in raw_types.split(",") if t.strip()]
    else:
        types = list(raw_types)
    return [
        f"st.file_uploader({label!r}, type={types or None!r}, key={widget.id!r})",
    ]


def _codegen_toggle(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Toggle")
    value = bool(widget.props.get("value", False))
    return [
        f"st.toggle({label!r}, value={value}, key={widget.id!r})",
    ]


def _codegen_multiselect(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Multiselect")
    raw_options = widget.props.get("options", ["Option 1", "Option 2"])
    if isinstance(raw_options, str):
        options = _ensure_options([opt.strip() for opt in raw_options.split(",")])
    else:
        options = _ensure_options(raw_options)
    raw_default = widget.props.get("default", [])
    if isinstance(raw_default, str):
        default = [d.strip() for d in raw_default.split(",") if d.strip()]
    else:
        default = list(raw_default)
    default = [d for d in default if d in options]
    return [
        f"st.multiselect({label!r}, options={options!r}, default={default!r}, key={widget.id!r})",
    ]


def _codegen_color_picker(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Color picker")
    value = widget.props.get("value", "#00A3FF")
    return [
        f"st.color_picker({label!r}, value={value!r}, key={widget.id!r})",
    ]


def _codegen_noop(_widget: WidgetInstance) -> List[str]:
    return []


def _render_noop(_widget: WidgetInstance) -> None:
    pass


def _codegen_text_input(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Text input")
    value = widget.props.get("value", "")
    expand = bool(widget.props.get("expand", False))
    lines = [f"st.text_input({label!r}, value={value!r}, key={widget.id!r})"]
    lines.extend(
        [
            "st.markdown(",
            f"    '<style>{_date_input_width_css(widget.id, expand)}</style>',",
            "    unsafe_allow_html=True,",
            ")",
        ]
    )
    return lines


def _codegen_text_area(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Text area")
    value = widget.props.get("value", "")
    expand = bool(widget.props.get("expand", False))
    lines = [f"st.text_area({label!r}, value={value!r}, key={widget.id!r})"]
    lines.extend(
        [
            "st.markdown(",
            f"    '<style>{_date_input_width_css(widget.id, expand)}</style>',",
            "    unsafe_allow_html=True,",
            ")",
        ]
    )
    return lines


def _codegen_text(widget: WidgetInstance) -> List[str]:
    text = widget.props.get("text", "Text")
    style = _text_style(widget)
    container_key = _text_container_key(widget)
    return [
        f"with st.container(key={container_key!r}):",
        f"    st.text({text!r})",
        "st.markdown(",
        f"    '<style>{_text_css_rule(container_key, style)}</style>',",
        "    unsafe_allow_html=True,",
        ")",
    ]


def _codegen_title(widget: WidgetInstance) -> List[str]:
    text = widget.props.get("text", "Title")
    style = _title_style(widget)
    container_key = _heading_container_key("title", widget)
    css = _heading_css_rule(container_key, 'h1', style)
    return [
        f"with st.container(key={container_key!r}):",
        f"    st.title({text!r})",
        "st.markdown(",
        f"    '<style>{css}</style>',",
        "    unsafe_allow_html=True,",
        ")",
    ]


def _codegen_header(widget: WidgetInstance) -> List[str]:
    text = widget.props.get("text", "Header")
    style = _header_style(widget)
    container_key = _heading_container_key("header", widget)
    css = _heading_css_rule(container_key, 'h2', style)
    return [
        f"with st.container(key={container_key!r}):",
        f"    st.header({text!r})",
        "st.markdown(",
        f"    '<style>{css}</style>',",
        "    unsafe_allow_html=True,",
        ")",
    ]


def _codegen_subheader(widget: WidgetInstance) -> List[str]:
    text = widget.props.get("text", "Subheader")
    style = _subheader_style(widget)
    container_key = _heading_container_key("subheader", widget)
    css = _heading_css_rule(container_key, 'h3', style)
    return [
        f"with st.container(key={container_key!r}):",
        f"    st.subheader({text!r})",
        "st.markdown(",
        f"    '<style>{css}</style>',",
        "    unsafe_allow_html=True,",
        ")",
    ]


def _codegen_markdown(widget: WidgetInstance) -> List[str]:
    text = widget.props.get("text", "Markdown")
    container_style = _markdown_container_style(widget)
    content_style = _markdown_content_style(widget)
    container_key = _markdown_container_key(widget)
    return [
        f"with st.container(key={container_key!r}):",
        f"    st.markdown({_single_quoted_python_string(text)})",
        "st.markdown(",
        f"    '<style>{_markdown_css_rule(container_key, container_style, content_style)}</style>',",
        "    unsafe_allow_html=True,",
        ")",
    ]


def _codegen_caption(widget: WidgetInstance) -> List[str]:
    text = widget.props.get("text", "Caption")
    container_style = _markdown_container_style(widget)
    content_style = _markdown_content_style(widget)
    container_key = _caption_container_key(widget)
    return [
        f"with st.container(key={container_key!r}):",
        f"    st.caption({text!r})",
        "st.markdown(",
        f"    '<style>{_caption_css_rule(container_key, container_style, content_style)}</style>',",
        "    unsafe_allow_html=True,",
        ")",
    ]


def _codegen_code(widget: WidgetInstance) -> List[str]:
    body = _sample_code_text()
    width = _code_dimension_option(widget.props.get("width", "stretch"), "stretch")
    height = _code_dimension_option(widget.props.get("height", "content"), "content")
    return [
        "st.code(",
        f"    {body!r},",
        "    language='python',",
        f"    width={width!r},",
        f"    height={height!r},",
        ")",
    ]


def _codegen_divider(widget: WidgetInstance) -> List[str]:
    line_width = _safe_int(widget.props.get("line_width", 1), 1)
    color = str(widget.props.get("color", "#D9D9D9")).strip() or "#D9D9D9"
    container_key = _divider_container_key(widget)
    return [
        f"with st.container(key={container_key!r}):",
        "    st.divider()",
        "st.markdown(",
        f"    '<style>{_divider_css_rule(container_key, line_width, color)}</style>',",
        "    unsafe_allow_html=True,",
        ")",
    ]


def _codegen_echo(widget: WidgetInstance) -> List[str]:
    code_location = _echo_code_location(widget.props.get("code_location", "above"))
    return [
        f"with st.echo(code_location={code_location!r}):",
        f"    {_echo_sample_code_line()}",
    ]


def _codegen_latex(widget: WidgetInstance) -> List[str]:
    text = widget.props.get("text", r"x^2 + y^2 = z^2")
    help_text = _latex_help(widget.props.get("help", ""))
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    font_size = _safe_int(widget.props.get("font_size", 16), 16)
    width = _latex_width_value(width_mode, custom_width)
    container_key = _latex_container_key(widget)
    lines = [
        f"with st.container(key={container_key!r}):",
        "    st.latex(",
        f"        {text!r},",
    ]
    if help_text is not None:
        lines.append(f"        help={help_text!r},")
    lines.extend(
        [
            f"        width={width!r}," if isinstance(width, str) else f"        width={width},",
            "    )",
            "st.markdown(",
            f"    '<style>{_latex_css_rule(container_key, font_size)}</style>',",
            "    unsafe_allow_html=True,",
            ")",
        ]
    )
    return lines


def _codegen_dataframe(widget: WidgetInstance) -> List[str]:
    data = _sample_dataframe_data()
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    height_mode = widget.props.get("height", "auto")
    custom_height = widget.props.get("custom_height", 320)
    selection_mode = _dataframe_selection_mode(widget.props.get("selection_mode", "multi-row"))
    hide_index = bool(widget.props.get("hide_index", False))
    row_height = _dataframe_row_height_value(widget.props.get("row_height", ""))
    width = _dataframe_width_value(width_mode, custom_width)
    height = _dataframe_height_value(height_mode, custom_height)
    container_key = _dataframe_container_key(widget)
    css_rule = _dataframe_css_rule(container_key, height_mode)
    lines = [
        f"with st.container(key={container_key!r}):",
        "    st.dataframe(",
        f"        {data!r},",
        f"        width={width!r}," if isinstance(width, str) else f"        width={width},",
        f"        height={height!r}," if isinstance(height, str) else f"        height={height},",
        f"        selection_mode={selection_mode!r},",
        f"        hide_index={hide_index},",
        f"        row_height={row_height},",
        "    )",
    ]
    if css_rule:
        lines.extend(
            [
                "st.markdown(",
                f"    '<style>{css_rule}</style>',",
                "    unsafe_allow_html=True,",
                ")",
            ]
        )
    return lines


def _codegen_data_editor(widget: WidgetInstance) -> List[str]:
    data = _sample_dataframe_data()
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    height_mode = widget.props.get("height", "auto")
    custom_height = widget.props.get("custom_height", 320)
    hide_index = bool(widget.props.get("hide_index", False))
    num_rows = _data_editor_num_rows(widget.props.get("num_rows", "fixed"))
    row_height = _dataframe_row_height_value(widget.props.get("row_height", ""))
    disabled = parse_data_editor_disabled(widget.props.get("disabled", False))
    width = _dataframe_width_value(width_mode, custom_width)
    height = _dataframe_height_value(height_mode, custom_height)
    container_key = _data_editor_container_key(widget)
    css_rule = _dataframe_css_rule(container_key, height_mode)
    lines = [
        f"with st.container(key={container_key!r}):",
        "    st.data_editor(",
        f"        {data!r},",
        f"        width={width!r}," if isinstance(width, str) else f"        width={width},",
        f"        height={height!r}," if isinstance(height, str) else f"        height={height},",
        f"        hide_index={hide_index},",
        f"        num_rows={num_rows!r},",
        f"        disabled={disabled!r},",
        f"        key={widget.id!r},",
        f"        row_height={row_height},",
        "    )",
    ]
    if css_rule:
        lines.extend(
            [
                "st.markdown(",
                f"    '<style>{css_rule}</style>',",
                "    unsafe_allow_html=True,",
                ")",
            ]
        )
    return lines


def _codegen_help(widget: WidgetInstance) -> List[str]:
    text = str(widget.props.get("text", "help text"))
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    width = _help_width_value(width_mode, custom_width)
    width_part = f"width={width!r}" if isinstance(width, str) else f"width={width}"
    return [f"st.help({text!r}, {width_part})"]


def _codegen_metric(widget: WidgetInstance) -> List[str]:
    label = str(widget.props.get("label", "Metric"))
    value = _metric_scalar_value(widget.props.get("value", "0"), allow_none=True)
    delta = _metric_scalar_value(widget.props.get("delta", ""), allow_none=True)
    delta_color = _metric_enum(widget.props.get("delta_color", "normal"), ["normal", "inverse", "off", "red", "orange", "yellow", "green", "blue", "violet", "gray", "grey", "primary"], "normal")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    label_visibility = _metric_enum(widget.props.get("label_visibility", "visible"), ["visible", "hidden", "collapsed"], "visible")
    border = bool(widget.props.get("border", False))
    background_color = str(widget.props.get("background_color", "#FFFFFF")).strip() or "#FFFFFF"
    width_mode = _metric_enum(widget.props.get("width", "stretch"), ["stretch", "content", "custom"], "stretch")
    custom_width = _safe_int(widget.props.get("custom_width", 320), 320)
    height_mode = _metric_enum(widget.props.get("height", "content"), ["content", "stretch", "custom"], "content")
    custom_height = _safe_int(widget.props.get("custom_height", 120), 120)
    chart_data = _metric_chart_data(widget.props.get("chart_data", []))
    chart_type = _metric_enum(widget.props.get("chart_type", "line"), ["line", "bar", "area"], "line")
    delta_arrow = _metric_enum(widget.props.get("delta_arrow", "auto"), ["auto", "up", "down", "off"], "auto")
    number_format = _metric_text_or_none(widget.props.get("format", ""))
    delta_description = _metric_text_or_none(widget.props.get("delta_description", ""))
    container_key = _metric_container_key(widget)
    css_rule = _metric_css_rule(container_key, background_color)

    width_value: str | int = custom_width if width_mode == "custom" and custom_width > 0 else width_mode
    height_value: str | int = custom_height if height_mode == "custom" and custom_height > 0 else height_mode

    # Keep sparkline visible in preview/generated apps when chart data is configured.
    if chart_data:
        border = True
        if delta is None:
            delta = 0

    metric_lines = ["st.metric(", f"    {label!r},"]
    if "value" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    value={value!r},")
    if "delta" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    delta={delta!r},")
    if "delta_color" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    delta_color={delta_color!r},")
    if "help" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    help={help_text!r},")
    if "label_visibility" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    label_visibility={label_visibility!r},")
    if "border" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    border={border},")
    if "width" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    width={width_value!r}," if isinstance(width_value, str) else f"    width={width_value},")
    if "height" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    height={height_value!r}," if isinstance(height_value, str) else f"    height={height_value},")
    if "chart_data" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    chart_data={chart_data!r},")
    if "chart_type" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    chart_type={chart_type!r},")
    if "delta_arrow" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    delta_arrow={delta_arrow!r},")
    if "format" in _ST_METRIC_PARAMS:
        metric_lines.append(f"    format={number_format!r},")
    metric_lines.append(")")

    lines = [f"with st.container(key={container_key!r}):"]
    if chart_data:
        lines.append("    row = st.container(horizontal=True)")
        lines.append("    with row:")
        lines.extend([f"        {line}" for line in metric_lines])
    else:
        lines.extend([f"    {line}" for line in metric_lines])

    if delta_description:
        lines.append(f"    st.caption({delta_description!r})")

    lines.extend(
        [
            "st.markdown(",
            f"    '<style>{css_rule}</style>',",
            "    unsafe_allow_html=True,",
            ")",
        ]
    )
    return lines


def _codegen_json(widget: WidgetInstance) -> List[str]:
    data = _sample_json_data()
    expanded = _json_expanded_value(widget.props.get("expanded", "true"), widget.props.get("custom_expanded", 2))
    width = _json_width_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320))
    return [
        "st.json(",
        f"    {data!r},",
        f"    expanded={expanded!r},",
        f"    width={width!r}," if isinstance(width, str) else f"    width={width},",
        ")",
    ]


def _codegen_area_chart(widget: WidgetInstance) -> List[str]:
    x_label = _area_chart_optional_text(widget.props.get("x_label", ""))
    y_label = _area_chart_optional_text(widget.props.get("y_label", ""))
    stack = _area_chart_stack_value(widget.props.get("stack", "none"))
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")

    chart_data_literal = _area_chart_codegen_data_literal()

    lines = [
        "import pandas as pd",
        "# Replace with your data",
        f"chart_data = pd.DataFrame({chart_data_literal!r})",
        "st.area_chart(",
        "    chart_data,",
    ]
    if x_label is not None:
        lines.append(f"    x_label={x_label!r},")
    if y_label is not None:
        lines.append(f"    y_label={y_label!r},")
    if stack is not None:
        lines.append(f"    stack={stack!r},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(f"    height={height!r}," if isinstance(height, str) else f"    height={height},")
    lines.append(")")
    return lines


def _codegen_bar_chart(widget: WidgetInstance) -> List[str]:
    x_label = _area_chart_optional_text(widget.props.get("x_label", ""))
    y_label = _area_chart_optional_text(widget.props.get("y_label", ""))
    horizontal = _bar_chart_horizontal_value(widget.props.get("horizontal", False))
    sort = _bar_chart_sort_value(widget.props.get("sort", "true"), widget.props.get("custom_sort", ""))
    stack = _bar_chart_stack_value(widget.props.get("stack", "none"))
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")

    chart_data_literal = _area_chart_codegen_data_literal()

    lines = [
        "import pandas as pd",
        "# Replace with your data",
        f"chart_data = pd.DataFrame({chart_data_literal!r})",
        "st.bar_chart(",
        "    chart_data,",
    ]
    if x_label is not None:
        lines.append(f"    x_label={x_label!r},")
    if y_label is not None:
        lines.append(f"    y_label={y_label!r},")
    lines.append(f"    horizontal={horizontal},")
    lines.append(f"    sort={sort!r},")
    if stack is not None:
        lines.append(f"    stack={stack!r},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(f"    height={height!r}," if isinstance(height, str) else f"    height={height},")
    lines.append(")")
    return lines


def _codegen_line_chart(widget: WidgetInstance) -> List[str]:
    x_label = _area_chart_optional_text(widget.props.get("x_label", ""))
    y_label = _area_chart_optional_text(widget.props.get("y_label", ""))
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")

    chart_data_literal = _area_chart_codegen_data_literal()

    lines = [
        "import pandas as pd",
        "# Replace with your data",
        f"chart_data = pd.DataFrame({chart_data_literal!r})",
        "st.line_chart(",
        "    chart_data,",
    ]
    if x_label is not None:
        lines.append(f"    x_label={x_label!r},")
    if y_label is not None:
        lines.append(f"    y_label={y_label!r},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(f"    height={height!r}," if isinstance(height, str) else f"    height={height},")
    lines.append(")")
    return lines


def _codegen_map(widget: WidgetInstance) -> List[str]:
    latitude = _area_chart_optional_text(widget.props.get("latitude", ""))
    longitude = _area_chart_optional_text(widget.props.get("longitude", ""))
    size = widget.props.get("size", "")
    zoom = _safe_int(widget.props.get("zoom", 11), 11)
    width = _map_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _map_dimension_value(widget.props.get("height", "custom"), widget.props.get("custom_height", 500), 500)

    map_data = dict(_SAMPLE_MAP_DATA)

    lines = [
        "import pandas as pd",
        "# Replace with your data",
        f"map_data = pd.DataFrame({map_data!r})",
        "st.map(",
        "    map_data,",
    ]
    if latitude is not None:
        lines.append(f"    latitude={latitude!r},")
    if longitude is not None:
        lines.append(f"    longitude={longitude!r},")
    size_text = str(size).strip()
    if size_text:
        try:
            size_num = float(size_text)
            lines.append(f"    size={size_num},")
        except ValueError:
            lines.append(f"    size={size_text!r},")
    lines.append(f"    zoom={zoom},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(f"    height={height!r}," if isinstance(height, str) else f"    height={height},")
    lines.append(")")
    return lines


def _scatter_chart_size_value(value: Any) -> float | None:
    """Return the size for scatter_chart: a positive number or None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    try:
        num = float(text)
        return num if num > 0 else None
    except (TypeError, ValueError):
        return None


def _codegen_scatter_chart(widget: WidgetInstance) -> List[str]:
    x_label = _area_chart_optional_text(widget.props.get("x_label", ""))
    y_label = _area_chart_optional_text(widget.props.get("y_label", ""))
    size = _scatter_chart_size_value(widget.props.get("size", ""))
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")

    chart_data_literal = dict(_FALLBACK_SCATTER_CHART_DATA)

    lines = [
        "import pandas as pd",
        "# Replace with your data",
        f"chart_data = pd.DataFrame({chart_data_literal!r})",
        "st.scatter_chart(",
        "    chart_data,",
    ]
    if x_label is not None:
        lines.append(f"    x_label={x_label!r},")
    if y_label is not None:
        lines.append(f"    y_label={y_label!r},")
    if size is not None:
        lines.append(f"    size={size},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(f"    height={height!r}," if isinstance(height, str) else f"    height={height},")
    lines.append(")")
    return lines


def _codegen_graphviz_chart(widget: WidgetInstance) -> List[str]:
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")

    lines = [
        "# Replace with your data",
        f"graph_dot = {_SAMPLE_GRAPHVIZ_DOT!r}",
        "st.graphviz_chart(",
        "    graph_dot,",
    ]
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(f"    height={height!r}," if isinstance(height, str) else f"    height={height},")
    lines.append(")")
    return lines


def _download_button_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _codegen_download_button(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Download")
    data = widget.props.get("data", "Your data goes here")
    file_name = widget.props.get("file_name", "Your_file_name.txt")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    btn_type = widget.props.get("type", "secondary")
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    width = _download_button_width_value(width_mode, custom_width)

    lines = [
        "st.download_button(",
        f"    {label!r},",
        f"    data={data!r},",
        f"    file_name={file_name!r},",
        f"    mime=None,",
        f"    key={widget.id!r},",
    ]
    if help_text is not None:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    type={btn_type!r},")
    lines.append(f"    icon=':material/download:',")
    lines.append(f"    disabled={disabled},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(")")
    return lines


def _render_download_button(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Download")
    data = str(widget.props.get("data", "Your data goes here"))
    file_name = widget.props.get("file_name", "Your_file_name.txt")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    btn_type = widget.props.get("type", "secondary")
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    width = _download_button_width_value(width_mode, custom_width)
    key = _preview_key(widget)

    kwargs: dict[str, Any] = {
        "data": data,
        "file_name": file_name,
        "mime": None,
        "key": key,
        "type": btn_type,
        "icon": ":material/download:",
        "disabled": disabled,
    }
    if help_text is not None:
        kwargs["help"] = help_text

    st.download_button(label, **kwargs)

    if isinstance(width, str) and width == "stretch":
        css = f".st-key-{key} {{ width: 100% !important; }} .st-key-{key} button {{ width: 100% !important; }}"
    elif isinstance(width, int):
        css = f".st-key-{key} button {{ width: {width}px !important; }}"
    elif width == "content":
        css = f".st-key-{key} {{ width: fit-content !important; display: inline-block; }}"
    else:
        css = ""
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _link_button_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _codegen_link_button(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Link")
    url = widget.props.get("url", "https://www.streamlit.io")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    btn_type = widget.props.get("type", "secondary")
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    width = _link_button_width_value(width_mode, custom_width)

    lines = [
        "st.link_button(",
        f"    {label!r},",
        f"    url={url!r},",
    ]
    if help_text is not None:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    type={btn_type!r},")
    lines.append("    icon=':material/link:',")
    lines.append(f"    disabled={disabled},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(")")
    return lines


def _render_link_button(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Link")
    url = widget.props.get("url", "https://www.streamlit.io")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    btn_type = widget.props.get("type", "secondary")
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    width = _link_button_width_value(width_mode, custom_width)

    kwargs: dict[str, Any] = {
        "type": btn_type,
        "icon": ":material/link:",
        "disabled": disabled,
        "width": width,
    }
    if help_text is not None:
        kwargs["help"] = help_text

    st.link_button(label, url, **kwargs)


def _page_link_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "content"
    return "content"


def _codegen_page_link(widget: WidgetInstance) -> List[str]:
    page = widget.props.get("page", "https://www.streamlit.io")
    label = widget.props.get("label", "Page link")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "content")
    custom_width = widget.props.get("custom_width", 320)
    width = _page_link_width_value(width_mode, custom_width)

    lines = [
        "st.page_link(",
        f"    {page!r},",
        f"    label={label!r},",
        "    icon=':material/thumb_up:',",
    ]
    if help_text is not None:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    disabled={disabled},")
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(")")
    return lines


def _render_page_link(widget: WidgetInstance) -> None:
    page = widget.props.get("page", "https://www.streamlit.io")
    label = widget.props.get("label", "Page link")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "content")
    custom_width = widget.props.get("custom_width", 320)
    width = _page_link_width_value(width_mode, custom_width)

    kwargs: dict[str, Any] = {
        "label": label,
        "icon": ":material/thumb_up:",
        "disabled": disabled,
        "width": width,
    }
    if help_text is not None:
        kwargs["help"] = help_text

    try:
        st.page_link(page, **kwargs)
    except Exception:
        # st.page_link requires a registered page path; fall back to a link button preview
        st.link_button(label, url=page if str(page).startswith("http") else "#", disabled=disabled)


def _feedback_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "content"
    return "content"


def _codegen_feedback(widget: WidgetInstance) -> List[str]:
    options = widget.props.get("options", "thumbs")
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "content")
    custom_width = widget.props.get("custom_width", 320)
    width = _feedback_width_value(width_mode, custom_width)

    lines = [
        "st.feedback(",
        f"    {options!r},",
        f"    key={widget.id!r},",
        "    default=None,",
        f"    disabled={disabled},",
    ]
    lines.append(f"    width={width!r}," if isinstance(width, str) else f"    width={width},")
    lines.append(")")
    return lines


def _render_feedback(widget: WidgetInstance) -> None:
    options = widget.props.get("options", "thumbs")
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "content")
    custom_width = widget.props.get("custom_width", 320)
    width = _feedback_width_value(width_mode, custom_width)
    key = _preview_key(widget)

    st.feedback(
        options,
        key=key,
        default=None,
        disabled=disabled,
        width=width,
    )


def _pills_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "content"
    return "content"


def _codegen_pills(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Pills")
    options_raw = widget.props.get("options", "Option 1, Option 2, Option 3")
    options = [o.strip() for o in str(options_raw).split(",") if o.strip()]
    selection_mode = widget.props.get("selection_mode", "single")
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _pills_width_value(widget.props.get("width", "content"), widget.props.get("custom_width", 320))

    lines = [
        "st.pills(",
        f"    {label!r},",
        f"    {options!r},",
        f"    selection_mode={selection_mode!r},",
        f"    key={widget.id!r},",
        "    default=None,",
        "    icon=None,",
    ]
    if help_text:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    disabled={disabled},")
    lines.append(f"    label_visibility={label_visibility!r},")
    lines.append(f"    width={width_val!r},")
    lines.append(")")
    return lines


def _render_pills(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Pills")
    options_raw = widget.props.get("options", "Option 1, Option 2, Option 3")
    options = [o.strip() for o in str(options_raw).split(",") if o.strip()]
    selection_mode = widget.props.get("selection_mode", "single")
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _pills_width_value(widget.props.get("width", "content"), widget.props.get("custom_width", 320))
    key = _preview_key(widget)

    kwargs: dict[str, Any] = {
        "selection_mode": selection_mode,
        "key": key,
        "default": None,
        "disabled": disabled,
        "label_visibility": label_visibility,
        "width": width_val,
    }
    if help_text:
        kwargs["help"] = help_text

    st.pills(label, options, **kwargs)


def _segmented_control_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized in {"stretch", "content"}:
        return normalized
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "content"
    return "content"


def _codegen_segmented_control(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Segmented control")
    options_raw = widget.props.get("options", "Option 1, Option 2, Option 3")
    options = [o.strip() for o in str(options_raw).split(",") if o.strip()]
    selection_mode = widget.props.get("selection_mode", "single")
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _segmented_control_width_value(
        widget.props.get("width", "content"), widget.props.get("custom_width", 320)
    )

    lines = [
        "st.segmented_control(",
        f"    {label!r},",
        f"    {options!r},",
        f"    selection_mode={selection_mode!r},",
        f"    key={widget.id!r},",
        "    default=None,",
    ]
    if help_text:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    disabled={disabled},")
    lines.append(f"    label_visibility={label_visibility!r},")
    lines.append(f"    width={width_val!r},")
    lines.append(")")
    return lines


def _render_segmented_control(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Segmented control")
    options_raw = widget.props.get("options", "Option 1, Option 2, Option 3")
    options = [o.strip() for o in str(options_raw).split(",") if o.strip()]
    selection_mode = widget.props.get("selection_mode", "single")
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _segmented_control_width_value(
        widget.props.get("width", "content"), widget.props.get("custom_width", 320)
    )
    key = _preview_key(widget)

    kwargs: dict[str, Any] = {
        "selection_mode": selection_mode,
        "key": key,
        "default": None,
        "disabled": disabled,
        "label_visibility": label_visibility,
        "width": width_val,
    }
    if help_text:
        kwargs["help"] = help_text

    st.segmented_control(label, options, **kwargs)


def _select_slider_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _codegen_select_slider(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Select slider")
    options_raw = widget.props.get("options", "Option 1, Option 2, Option 3")
    options = [o.strip() for o in str(options_raw).split(",") if o.strip()]
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _select_slider_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )

    lines = [
        "st.select_slider(",
        f"    {label!r},",
        f"    options={options!r},",
        f"    value=None,",
        f"    key={widget.id!r},",
    ]
    if help_text:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    disabled={disabled},")
    lines.append(f"    label_visibility={label_visibility!r},")
    lines.append(f"    width={width_val!r},")
    lines.append(")")
    return lines


def _render_select_slider(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Select slider")
    options_raw = widget.props.get("options", "Option 1, Option 2, Option 3")
    options = [o.strip() for o in str(options_raw).split(",") if o.strip()]
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _select_slider_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )
    key = _preview_key(widget)

    kwargs: dict[str, Any] = {
        "options": options,
        "key": key,
        "disabled": disabled,
        "label_visibility": label_visibility,
        "width": width_val,
    }
    if help_text:
        kwargs["help"] = help_text

    st.select_slider(label, **kwargs)


def _datetime_input_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _codegen_datetime_input(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Datetime input")
    value_raw = widget.props.get("value", "now")
    min_value_raw = widget.props.get("min_value", "") or ""
    max_value_raw = widget.props.get("max_value", "") or ""
    fmt = widget.props.get("format", "YYYY/MM/DD")
    step = _safe_int(widget.props.get("step", 900), 900)
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _datetime_input_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )

    # Resolve value
    if not value_raw or str(value_raw).strip() == "":
        value_code = "None"
    else:
        value_code = repr(str(value_raw).strip())

    # Resolve min/max
    min_code = repr(str(min_value_raw).strip()) if str(min_value_raw).strip() else "None"
    max_code = repr(str(max_value_raw).strip()) if str(max_value_raw).strip() else "None"

    lines = [
        "st.datetime_input(",
        f"    {label!r},",
        f"    value={value_code},",
        f"    min_value={min_code},",
        f"    max_value={max_code},",
        f"    key={widget.id!r},",
        f"    format={fmt!r},",
        f"    step={step},",
    ]
    if help_text:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    disabled={disabled},")
    lines.append(f"    label_visibility={label_visibility!r},")
    lines.append(f"    width={width_val!r},")
    lines.append(")")
    return lines


def _render_datetime_input(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Datetime input")
    value_raw = widget.props.get("value", "now")
    min_value_raw = widget.props.get("min_value", "") or ""
    max_value_raw = widget.props.get("max_value", "") or ""
    fmt = widget.props.get("format", "YYYY/MM/DD")
    step = _safe_int(widget.props.get("step", 900), 900)
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _datetime_input_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )
    key = _preview_key(widget)

    value = str(value_raw).strip() if value_raw and str(value_raw).strip() else "now"
    min_value = str(min_value_raw).strip() if str(min_value_raw).strip() else None
    max_value = str(max_value_raw).strip() if str(max_value_raw).strip() else None

    kwargs: dict[str, Any] = {
        "value": value,
        "key": key,
        "format": fmt,
        "step": step,
        "disabled": disabled,
        "label_visibility": label_visibility,
        "width": width_val,
    }
    if min_value:
        kwargs["min_value"] = min_value
    if max_value:
        kwargs["max_value"] = max_value
    if help_text:
        kwargs["help"] = help_text

    st.datetime_input(label, **kwargs)


def _time_input_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _codegen_time_input(widget: WidgetInstance) -> List[str]:
    label = widget.props.get("label", "Time input")
    value_raw = widget.props.get("value", "now")
    step = _safe_int(widget.props.get("step", 900), 900)
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _time_input_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )

    if not value_raw or str(value_raw).strip() == "":
        value_code = "None"
    else:
        value_code = repr(str(value_raw).strip())

    lines = [
        "st.time_input(",
        f"    {label!r},",
        f"    value={value_code},",
        f"    key={widget.id!r},",
        f"    step={step},",
    ]
    if help_text:
        lines.append(f"    help={help_text!r},")
    lines.append(f"    disabled={disabled},")
    lines.append(f"    label_visibility={label_visibility!r},")
    lines.append(f"    width={width_val!r},")
    lines.append(")")
    return lines


def _render_time_input(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Time input")
    value_raw = widget.props.get("value", "now")
    step = _safe_int(widget.props.get("step", 900), 900)
    disabled = bool(widget.props.get("disabled", False))
    help_text = widget.props.get("help", "") or None
    label_visibility = widget.props.get("label_visibility", "visible")
    width_val = _time_input_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )
    key = _preview_key(widget)

    value = str(value_raw).strip() if value_raw and str(value_raw).strip() else "now"

    kwargs: dict[str, Any] = {
        "value": value,
        "key": key,
        "step": step,
        "disabled": disabled,
        "label_visibility": label_visibility,
        "width": width_val,
    }
    if help_text:
        kwargs["help"] = help_text

    st.time_input(label, **kwargs)


def _chat_input_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _codegen_chat_input(widget: WidgetInstance) -> List[str]:
    placeholder = widget.props.get("placeholder", "Your message")
    custom_key = str(widget.props.get("key", "")).strip()
    key = custom_key if custom_key else widget.id
    disabled = bool(widget.props.get("disabled", False))
    width_val = _chat_input_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )

    lines = [
        "st.chat_input(",
        f"    {placeholder!r},",
        f"    key={key!r},",
        "    max_chars=None,",
        "    accept_file=False,",
        "    accept_audio=False,",
        f"    disabled={disabled},",
        f"    width={width_val!r}," if isinstance(width_val, str) else f"    width={width_val},",
        ")",
    ]
    return lines


def _render_chat_input(widget: WidgetInstance) -> None:
    placeholder = widget.props.get("placeholder", "Your message")
    disabled = bool(widget.props.get("disabled", False))
    width_val = _chat_input_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )
    key = _preview_key(widget)

    st.chat_input(
        placeholder,
        key=key,
        max_chars=None,
        accept_file=False,
        accept_audio=False,
        disabled=disabled,
        width=width_val,
    )


def _image_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "content"
    return "content"


def _image_optional_text(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text if text else None


def _codegen_image(widget: WidgetInstance) -> List[str]:
    image_url = widget.props.get("image", "./static/img_placeholder.jpg")
    caption = _image_optional_text(widget.props.get("caption", ""))
    width_val = _image_width_value(
        widget.props.get("width", "content"), widget.props.get("custom_width", 320)
    )
    output_format = widget.props.get("output_format", "auto")

    lines = [
        "st.image(",
        f"    {image_url!r},",
        f"    caption={caption!r},",
        f"    width={width_val!r},",
        f"    output_format={output_format!r},",
        ")",
    ]
    return lines


def _render_image(widget: WidgetInstance) -> None:
    image_url = widget.props.get("image", "./static/img_placeholder.jpg")
    caption = _image_optional_text(widget.props.get("caption", ""))
    width_val = _image_width_value(
        widget.props.get("width", "content"), widget.props.get("custom_width", 320)
    )
    output_format = widget.props.get("output_format", "auto")

    st.image(
        image_url,
        caption=caption,
        width=width_val,
        output_format=output_format,
    )


def _logo_optional_text(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text if text else None


def _codegen_logo(widget: WidgetInstance) -> List[str]:
    image = widget.props.get("image", "./static/img_placeholder.jpg")
    size = widget.props.get("size", "medium")
    icon_image = _logo_optional_text(widget.props.get("icon_image", ""))

    lines = [
        "st.logo(",
        f"    {image!r},",
        f"    size={size!r},",
        f"    icon_image={icon_image!r},",
        ")",
    ]
    return lines


def _render_logo(widget: WidgetInstance) -> None:
    image = widget.props.get("image", "./static/img_placeholder.jpg")
    size = widget.props.get("size", "medium")
    icon_image = _logo_optional_text(widget.props.get("icon_image", ""))

    # st.logo renders in the top-left corner of the app, not in the body.
    # Show a visible placeholder in the canvas so the widget is not invisible.
    size_px = {"small": 20, "medium": 24, "large": 32}.get(str(size), 24)
    icon_part = f" | icon: `{icon_image}`" if icon_image else ""
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;padding:4px 8px;"
        f"border:1px dashed #aaa;border-radius:4px;background:#f8f8f8;width:fit-content;'>"
        f"<span style='font-size:11px;color:#888;'>🏷 Logo</span>"
        f"<img src='{image}' style='max-height:{size_px}px;max-width:120px;object-fit:contain;' "
        f"onerror=\"this.style.display='none'\">"
        f"<span style='font-size:11px;color:#555;'>size={size}{icon_part}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.logo(image, size=size, icon_image=icon_image)


def _pdf_height_value(height_mode: Any, custom_height: Any) -> int | str:
    normalized = str(height_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    # "custom" or anything else -> integer height
    try:
        parsed = int(custom_height)
    except (TypeError, ValueError):
        return 500
    return parsed if parsed > 0 else 500


def _codegen_pdf(widget: WidgetInstance) -> List[str]:
    data = str(widget.props.get("data", str(_SAMPLE_PDF_PATH))).strip() or str(_SAMPLE_PDF_PATH)
    height_mode = widget.props.get("height", "custom")
    custom_height = widget.props.get("custom_height", 500)
    height = _pdf_height_value(height_mode, custom_height)
    key = widget.id

    lines = [
        "# Replace with your data",
        "st.pdf(",
        f"    {data!r},",
        f"    height={height!r}," if isinstance(height, str) else f"    height={height},",
        f"    key={key!r},",
        ")",
    ]
    return lines


def _render_pdf(widget: WidgetInstance) -> None:
    data = str(widget.props.get("data", str(_SAMPLE_PDF_PATH))).strip() or str(_SAMPLE_PDF_PATH)
    height_mode = widget.props.get("height", "custom")
    custom_height = widget.props.get("custom_height", 500)
    height = _pdf_height_value(height_mode, custom_height)
    key = _preview_key(widget)

    try:
        st.pdf(data, height=height, key=key)  # type: ignore[attr-defined]
    except Exception:
        st.info(f"PDF preview: {data} | height={height}")


_preview_key_counters: dict[str, int] = {}


def reset_preview_keys() -> None:
    """Call once at the start of each preview render pass to allow key reuse across reruns."""
    _preview_key_counters.clear()


def _preview_key(widget: WidgetInstance) -> str:
    base = f"wgt_preview_{widget.type}_{widget.id}"
    count = _preview_key_counters.get(base, 0)
    _preview_key_counters[base] = count + 1
    return base if count == 0 else f"{base}_{count}"


def _date_input_width_css(widget_id: str, expand: bool) -> str:
    if not expand:
        return ""
    return f'div[data-testid="stWidgetLabel"][id*="{widget_id}"] + div {{ width: 100% !important; }}'


def _render_title(widget: WidgetInstance) -> None:
    text = widget.props.get("text", "Title")
    style = _title_style(widget)
    container_key = _heading_container_key("title", widget, preview=True)
    with st.container(key=container_key):
        st.title(text)
    st.markdown(f"<style>{_heading_css_rule(container_key, 'h1', style)}</style>", unsafe_allow_html=True)


def _render_header(widget: WidgetInstance) -> None:
    text = widget.props.get("text", "Header")
    style = _header_style(widget)
    container_key = _heading_container_key("header", widget, preview=True)
    with st.container(key=container_key):
        st.header(text)
    st.markdown(f"<style>{_heading_css_rule(container_key, 'h2', style)}</style>", unsafe_allow_html=True)


def _render_subheader(widget: WidgetInstance) -> None:
    text = widget.props.get("text", "Subheader")
    style = _subheader_style(widget)
    container_key = _heading_container_key("subheader", widget, preview=True)
    with st.container(key=container_key):
        st.subheader(text)
    st.markdown(f"<style>{_heading_css_rule(container_key, 'h3', style)}</style>", unsafe_allow_html=True)


def _render_markdown(widget: WidgetInstance) -> None:
    text = widget.props.get("text", "Markdown")
    container_style = _markdown_container_style(widget)
    content_style = _markdown_content_style(widget)
    container_key = _markdown_container_key(widget, preview=True)
    with st.container(key=container_key):
        st.markdown(text)
    st.markdown(f"<style>{_markdown_css_rule(container_key, container_style, content_style)}</style>", unsafe_allow_html=True)


def _render_badge(widget: WidgetInstance) -> None:
    text = widget.props.get("text", "Badge")
    container_style = _badge_container_style(widget)
    content_style = _badge_content_style(widget)
    container_key = _badge_container_key(widget, preview=True)
    with st.container(key=container_key):
        st.badge(text, color="blue", width="content")
    st.markdown(f"<style>{_badge_css_rule(container_key, container_style, content_style)}</style>", unsafe_allow_html=True)


def _render_caption(widget: WidgetInstance) -> None:
    text = widget.props.get("text", "Caption")
    container_style = _markdown_container_style(widget)
    content_style = _markdown_content_style(widget)
    container_key = _caption_container_key(widget, preview=True)
    with st.container(key=container_key):
        st.caption(text)
    st.markdown(f"<style>{_caption_css_rule(container_key, container_style, content_style)}</style>", unsafe_allow_html=True)


def _render_text(widget: WidgetInstance) -> None:
    text = widget.props.get("text", "Text")
    style = _text_style(widget)
    container_key = _text_container_key(widget, preview=True)
    with st.container(key=container_key):
        st.text(text)
    st.markdown(f"<style>{_text_css_rule(container_key, style)}</style>", unsafe_allow_html=True)


def _render_button(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Button")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    btn_type = widget.props.get("type", "secondary")
    icon = str(widget.props.get("icon", "")).strip() or None
    disabled = bool(widget.props.get("disabled", False))
    width_mode = widget.props.get("width", "content")
    custom_width = widget.props.get("custom_width", 200)
    background_color = widget.props.get("background_color", "")
    text_color = widget.props.get("text_color", "")
    width = _button_width_value(width_mode, custom_width)
    key = _preview_key(widget)
    css_rule = _button_css_rule(key, background_color, text_color)

    kwargs: dict[str, Any] = {
        "key": key,
        "type": btn_type,
        "disabled": disabled,
        "width": width,
    }
    if help_text is not None:
        kwargs["help"] = help_text
    if icon:
        kwargs["icon"] = icon
        if "icon_position" in _ST_BUTTON_PARAMS:
            kwargs["icon_position"] = "left"

    st.button(label, **kwargs)
    if css_rule:
        st.markdown(f"<style>{css_rule}</style>", unsafe_allow_html=True)


def _render_checkbox(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Checkbox")
    checked = bool(widget.props.get("checked", False))
    disabled = bool(widget.props.get("disabled", False))
    label_visibility = "visible" if widget.props.get("label_visibility", True) else "hidden"
    st.checkbox(label, value=checked, disabled=disabled, label_visibility=label_visibility, key=_preview_key(widget))


def _render_selectbox(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Selectbox")
    raw_options = widget.props.get("options", ["Option 1", "Option 2"])
    if isinstance(raw_options, str):
        options = _ensure_options([opt.strip() for opt in raw_options.split(",")])
    else:
        options = _ensure_options(raw_options)
    index = _clamp_index(widget.props.get("index", 0), options)
    st.selectbox(label, options=options, index=index, key=_preview_key(widget))


def _render_radio(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Radio")
    raw_options = widget.props.get("options", ["Option 1", "Option 2"])
    if isinstance(raw_options, str):
        options = _ensure_options([opt.strip() for opt in raw_options.split(",")])
    else:
        options = _ensure_options(raw_options)
    index = _clamp_index(widget.props.get("index", 0), options)
    st.radio(label, options=options, index=index, key=_preview_key(widget))


def _render_slider(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Slider")
    min_val = float(widget.props.get("min", 0.0))
    max_val = float(widget.props.get("max", 100.0))
    value = _clamp_value(float(widget.props.get("value", 50.0)), min_val, max_val)
    step = _safe_step(widget.props.get("step", 1.0))
    st.slider(label, min_value=min_val, max_value=max_val, value=value, step=step, key=_preview_key(widget))


def _render_number_input(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Number input")
    min_val = float(widget.props.get("min", 0.0))
    max_val = float(widget.props.get("max", 100.0))
    value = _clamp_value(float(widget.props.get("value", 0.0)), min_val, max_val)
    step = _safe_step(widget.props.get("step", 1.0))
    st.number_input(label, min_value=min_val, max_value=max_val, value=value, step=step, key=_preview_key(widget))


def _render_date_input(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Date input")
    value = _date_from_iso(widget.props.get("value", ""))
    st.date_input(label, value=value, key=_preview_key(widget))


def _render_file_uploader(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "File uploader")
    raw_types = widget.props.get("types", ["csv", "png"])
    if isinstance(raw_types, str):
        types = [t.strip() for t in raw_types.split(",") if t.strip()]
    else:
        types = list(raw_types)
    st.file_uploader(label, type=types or None, key=_preview_key(widget))


def _render_toggle(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Toggle")
    value = bool(widget.props.get("value", False))
    st.toggle(label, value=value, key=_preview_key(widget))


def _render_multiselect(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Multiselect")
    raw_options = widget.props.get("options", ["Option 1", "Option 2"])
    if isinstance(raw_options, str):
        options = _ensure_options([opt.strip() for opt in raw_options.split(",")])
    else:
        options = _ensure_options(raw_options)
    raw_default = widget.props.get("default", [])
    if isinstance(raw_default, str):
        default = [d.strip() for d in raw_default.split(",") if d.strip()]
    else:
        default = list(raw_default)
    default = [d for d in default if d in options]
    st.multiselect(label, options=options, default=default, key=_preview_key(widget))


def _render_color_picker(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Color picker")
    value = widget.props.get("value", "#00A3FF")
    st.color_picker(label, value=value, key=_preview_key(widget))


def _render_text_input(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Text input")
    value = widget.props.get("value", "")
    expand = bool(widget.props.get("expand", False))
    st.text_input(label, value=value, key=_preview_key(widget))
    if expand:
        css = _date_input_width_css(widget.id, expand)
        if css:
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _render_text_area(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Text area")
    value = widget.props.get("value", "")
    expand = bool(widget.props.get("expand", False))
    st.text_area(label, value=value, key=_preview_key(widget))
    if expand:
        css = _date_input_width_css(widget.id, expand)
        if css:
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _render_code(widget: WidgetInstance) -> None:
    body = _sample_code_text()
    width = _code_dimension_option(widget.props.get("width", "stretch"), "stretch")
    height = _code_dimension_option(widget.props.get("height", "content"), "content")
    st.code(body, language="python", width=width, height=height)


def _render_divider(widget: WidgetInstance) -> None:
    line_width = _safe_int(widget.props.get("line_width", 1), 1)
    color = str(widget.props.get("color", "#D9D9D9")).strip() or "#D9D9D9"
    container_key = _divider_container_key(widget, preview=True)
    with st.container(key=container_key):
        st.divider()
    st.markdown(f"<style>{_divider_css_rule(container_key, line_width, color)}</style>", unsafe_allow_html=True)


def _render_echo(widget: WidgetInstance) -> None:
    code_location = _echo_code_location(widget.props.get("code_location", "above"))
    with st.echo(code_location=code_location):
        _render_echo_sample_body()


def _render_latex(widget: WidgetInstance) -> None:
    text = widget.props.get("text", r"x^2 + y^2 = z^2")
    help_text = _latex_help(widget.props.get("help", ""))
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    font_size = _safe_int(widget.props.get("font_size", 16), 16)
    width = _latex_width_value(width_mode, custom_width)
    container_key = _latex_container_key(widget, preview=True)
    kwargs: dict[str, Any] = {"width": width}
    if help_text is not None:
        kwargs["help"] = help_text
    with st.container(key=container_key):
        st.latex(text, **kwargs)
    st.markdown(f"<style>{_latex_css_rule(container_key, font_size)}</style>", unsafe_allow_html=True)


def _render_dataframe(widget: WidgetInstance) -> None:
    data = _sample_dataframe_data()
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    height_mode = widget.props.get("height", "auto")
    custom_height = widget.props.get("custom_height", 320)
    selection_mode = _dataframe_selection_mode(widget.props.get("selection_mode", "multi-row"))
    hide_index = bool(widget.props.get("hide_index", False))
    row_height = _dataframe_row_height_value(widget.props.get("row_height", ""))
    width = _dataframe_width_value(width_mode, custom_width)
    height = _dataframe_height_value(height_mode, custom_height)
    container_key = _dataframe_container_key(widget, preview=True)
    css_rule = _dataframe_css_rule(container_key, height_mode)
    with st.container(key=container_key):
        st.dataframe(data, width=width, height=height, selection_mode=selection_mode, hide_index=hide_index, row_height=row_height)
    if css_rule:
        st.markdown(f"<style>{css_rule}</style>", unsafe_allow_html=True)


def _render_data_editor(widget: WidgetInstance) -> None:
    data = _sample_dataframe_data()
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    height_mode = widget.props.get("height", "auto")
    custom_height = widget.props.get("custom_height", 320)
    hide_index = bool(widget.props.get("hide_index", False))
    num_rows = _data_editor_num_rows(widget.props.get("num_rows", "fixed"))
    row_height = _dataframe_row_height_value(widget.props.get("row_height", ""))
    disabled = parse_data_editor_disabled(widget.props.get("disabled", False))
    width = _dataframe_width_value(width_mode, custom_width)
    height = _dataframe_height_value(height_mode, custom_height)
    container_key = _data_editor_container_key(widget, preview=True)
    css_rule = _dataframe_css_rule(container_key, height_mode)
    with st.container(key=container_key):
        st.data_editor(data, width=width, height=height, hide_index=hide_index, num_rows=num_rows, disabled=disabled, key=_preview_key(widget), row_height=row_height)
    if css_rule:
        st.markdown(f"<style>{css_rule}</style>", unsafe_allow_html=True)


def _render_help(widget: WidgetInstance) -> None:
    text = str(widget.props.get("text", "help text"))
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 320)
    width = _help_width_value(width_mode, custom_width)
    st.help(text, width=width)


def _render_metric(widget: WidgetInstance) -> None:
    label = str(widget.props.get("label", "Metric"))
    value = _metric_scalar_value(widget.props.get("value", "0"), allow_none=True)
    delta = _metric_scalar_value(widget.props.get("delta", ""), allow_none=True)
    delta_color = _metric_enum(widget.props.get("delta_color", "normal"), ["normal", "inverse", "off", "red", "orange", "yellow", "green", "blue", "violet", "gray", "grey", "primary"], "normal")
    help_text = _metric_text_or_none(widget.props.get("help", ""))
    label_visibility = _metric_enum(widget.props.get("label_visibility", "visible"), ["visible", "hidden", "collapsed"], "visible")
    border = bool(widget.props.get("border", False))
    background_color = str(widget.props.get("background_color", "#FFFFFF")).strip() or "#FFFFFF"
    width_mode = _metric_enum(widget.props.get("width", "stretch"), ["stretch", "content", "custom"], "stretch")
    custom_width = _safe_int(widget.props.get("custom_width", 320), 320)
    height_mode = _metric_enum(widget.props.get("height", "content"), ["content", "stretch", "custom"], "content")
    custom_height = _safe_int(widget.props.get("custom_height", 120), 120)
    chart_data = _metric_chart_data(widget.props.get("chart_data", []))
    chart_type = _metric_enum(widget.props.get("chart_type", "line"), ["line", "bar", "area"], "line")
    delta_arrow = _metric_enum(widget.props.get("delta_arrow", "auto"), ["auto", "up", "down", "off"], "auto")
    number_format = _metric_text_or_none(widget.props.get("format", ""))
    delta_description = _metric_text_or_none(widget.props.get("delta_description", ""))
    container_key = _metric_container_key(widget, preview=True)
    css_rule = _metric_css_rule(container_key, background_color)

    width_value: str | int = custom_width if width_mode == "custom" and custom_width > 0 else width_mode
    height_value: str | int = custom_height if height_mode == "custom" and custom_height > 0 else height_mode

    if chart_data:
        border = True
        if delta is None:
            delta = 0

    metric_kwargs: dict[str, Any] = {}
    if "value" in _ST_METRIC_PARAMS:
        metric_kwargs["value"] = value
    if "delta" in _ST_METRIC_PARAMS:
        metric_kwargs["delta"] = delta
    if "delta_color" in _ST_METRIC_PARAMS:
        metric_kwargs["delta_color"] = delta_color
    if help_text is not None and "help" in _ST_METRIC_PARAMS:
        metric_kwargs["help"] = help_text
    if "label_visibility" in _ST_METRIC_PARAMS:
        metric_kwargs["label_visibility"] = label_visibility
    if "border" in _ST_METRIC_PARAMS:
        metric_kwargs["border"] = border
    if "width" in _ST_METRIC_PARAMS:
        metric_kwargs["width"] = width_value
    if "height" in _ST_METRIC_PARAMS:
        metric_kwargs["height"] = height_value
    if chart_data and "chart_data" in _ST_METRIC_PARAMS:
        metric_kwargs["chart_data"] = chart_data
    if "chart_type" in _ST_METRIC_PARAMS:
        metric_kwargs["chart_type"] = chart_type
    if "delta_arrow" in _ST_METRIC_PARAMS:
        metric_kwargs["delta_arrow"] = delta_arrow
    if number_format is not None and "format" in _ST_METRIC_PARAMS:
        metric_kwargs["format"] = number_format

    with st.container(key=container_key):
        if chart_data:
            row = st.container(horizontal=True)
            with row:
                st.metric(label, **metric_kwargs)
        else:
            st.metric(label, **metric_kwargs)
        if delta_description:
            st.caption(delta_description)

    st.markdown(f"<style>{css_rule}</style>", unsafe_allow_html=True)


def _render_json(widget: WidgetInstance) -> None:
    data = _sample_json_data()
    expanded = _json_expanded_value(widget.props.get("expanded", "true"), widget.props.get("custom_expanded", 2))
    width = _json_width_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320))
    # st.json only accepts 'stretch' or int; map 'content' -> 'stretch'
    if isinstance(width, str) and width not in ("stretch",):
        width = "stretch"
    st.json(data, expanded=expanded, width=width)


def _render_table(widget: WidgetInstance) -> None:
    data = _sample_dataframe_data()
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 0)
    height_mode = widget.props.get("height", "auto")
    custom_height = widget.props.get("custom_height", 0)
    border = widget.props.get("border", True)
    container_key = _table_container_key(widget, preview=True)
    css_rule = _table_css_rule(container_key, width_mode, custom_width, height_mode, custom_height, border)
    with st.container(key=container_key):
        st.table(data)
    if css_rule:
        st.markdown(f"<style>{css_rule}</style>", unsafe_allow_html=True)


def _render_area_chart(widget: WidgetInstance) -> None:
    data = _sample_area_chart_data()
    x_label = _area_chart_optional_text(widget.props.get("x_label", ""))
    y_label = _area_chart_optional_text(widget.props.get("y_label", ""))
    stack = _area_chart_stack_value(widget.props.get("stack", "none"))
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")
    kwargs: dict[str, Any] = {"width": width, "height": height}
    if x_label is not None:
        kwargs["x_label"] = x_label
    if y_label is not None:
        kwargs["y_label"] = y_label
    if stack is not None:
        kwargs["stack"] = stack
    st.area_chart(data, **kwargs)


def _render_bar_chart(widget: WidgetInstance) -> None:
    data = _sample_area_chart_data()
    x_label = _area_chart_optional_text(widget.props.get("x_label", ""))
    y_label = _area_chart_optional_text(widget.props.get("y_label", ""))
    horizontal = _bar_chart_horizontal_value(widget.props.get("horizontal", False))
    sort = _bar_chart_sort_value(widget.props.get("sort", "true"), widget.props.get("custom_sort", ""))
    stack = _bar_chart_stack_value(widget.props.get("stack", "none"))
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")
    # Validate sort: if it's a string column name, verify it exists in sample data
    if isinstance(sort, str) and sort not in data.columns:
        sort = True
    kwargs: dict[str, Any] = {"horizontal": horizontal, "sort": sort, "width": width, "height": height}
    if x_label is not None:
        kwargs["x_label"] = x_label
    if y_label is not None:
        kwargs["y_label"] = y_label
    if stack is not None:
        kwargs["stack"] = stack
    st.bar_chart(data, **kwargs)


def _render_line_chart(widget: WidgetInstance) -> None:
    data = _sample_area_chart_data()
    x_label = _area_chart_optional_text(widget.props.get("x_label", ""))
    y_label = _area_chart_optional_text(widget.props.get("y_label", ""))
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")
    kwargs: dict[str, Any] = {"width": width, "height": height}
    if x_label is not None:
        kwargs["x_label"] = x_label
    if y_label is not None:
        kwargs["y_label"] = y_label
    st.line_chart(data, **kwargs)


def _render_map(widget: WidgetInstance) -> None:
    import pandas as pd
    data = pd.DataFrame(_SAMPLE_MAP_DATA)
    latitude = _area_chart_optional_text(widget.props.get("latitude", ""))
    longitude = _area_chart_optional_text(widget.props.get("longitude", ""))
    size = widget.props.get("size", "")
    zoom = _safe_int(widget.props.get("zoom", 11), 11)
    width = _map_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _map_dimension_value(widget.props.get("height", "custom"), widget.props.get("custom_height", 500), 500)
    kwargs: dict[str, Any] = {"zoom": zoom, "width": width, "height": height}
    if latitude is not None:
        kwargs["latitude"] = latitude
    if longitude is not None:
        kwargs["longitude"] = longitude
    size_text = str(size).strip()
    if size_text:
        try:
            kwargs["size"] = float(size_text)
        except ValueError:
            kwargs["size"] = size_text
    st.map(data, **kwargs)


def _render_scatter_chart(widget: WidgetInstance) -> None:
    import pandas as pd
    data = pd.DataFrame(_FALLBACK_SCATTER_CHART_DATA)
    x_label = _area_chart_optional_text(widget.props.get("x_label", ""))
    y_label = _area_chart_optional_text(widget.props.get("y_label", ""))
    size = _scatter_chart_size_value(widget.props.get("size", ""))
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")
    kwargs: dict[str, Any] = {"width": width, "height": height}
    if x_label is not None:
        kwargs["x_label"] = x_label
    if y_label is not None:
        kwargs["y_label"] = y_label
    if size is not None:
        kwargs["size"] = size
    st.scatter_chart(data, **kwargs)


def _render_graphviz_chart(widget: WidgetInstance) -> None:
    width = _area_chart_dimension_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320), "stretch")
    height = _area_chart_dimension_value(widget.props.get("height", "content"), widget.props.get("custom_height", 320), "content")
    st.graphviz_chart(_SAMPLE_GRAPHVIZ_DOT, width=width, height=height)


def _audio_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _codegen_table(widget: WidgetInstance) -> List[str]:
    width_mode = widget.props.get("width", "stretch")
    custom_width = widget.props.get("custom_width", 0)
    height_mode = widget.props.get("height", "auto")
    custom_height = widget.props.get("custom_height", 0)
    border = widget.props.get("border", True)
    container_key = _table_container_key(widget)
    css_rule = _table_css_rule(container_key, width_mode, custom_width, height_mode, custom_height, border)
    lines = [
        "from samples.DataFrame_sample import df_sample",
        f"with st.container(key={container_key!r}):",
        "    st.table(df_sample)",
    ]
    if css_rule:
        lines.extend([
            "st.markdown(",
            f"    '<style>{css_rule}</style>',",
            "    unsafe_allow_html=True,",
            ")",
        ])
    return lines


def _codegen_audio(widget: WidgetInstance) -> List[str]:
    fmt = widget.props.get("format", "audio/wav")
    start_time = _safe_int(widget.props.get("start_time", 0), 0)
    loop = bool(widget.props.get("loop", False))
    autoplay = bool(widget.props.get("autoplay", False))
    width_val = _audio_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )

    lines = [
        "st.audio(",
        '    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",',
        f"    format={fmt!r},",
        f"    start_time={start_time},",
        "    end_time=None,",
        f"    loop={loop},",
        f"    autoplay={autoplay},",
        f"    width={width_val!r}," if isinstance(width_val, str) else f"    width={width_val},",
        ")",
    ]
    return lines


def _render_audio(widget: WidgetInstance) -> None:
    fmt = widget.props.get("format", "audio/wav")
    start_time = _safe_int(widget.props.get("start_time", 0), 0)
    loop = bool(widget.props.get("loop", False))
    autoplay = bool(widget.props.get("autoplay", False))
    width_val = _audio_width_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 320))
    st.audio(
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        format=fmt,
        start_time=start_time,
        end_time=None,
        loop=loop,
        autoplay=autoplay,
        width=width_val,
    )


def _video_width_value(width_mode: Any, custom_width: Any) -> int | str:
    if str(width_mode).strip().lower() == "custom":
        try:
            v = int(custom_width)
            return v if v > 0 else 400
        except (TypeError, ValueError):
            return 400
    return "stretch"


def _codegen_video(widget: WidgetInstance) -> List[str]:
    data = widget.props.get("data", "./static/mp4_sample.mp4")
    fmt = widget.props.get("format", "video/mp4")
    start_time = _safe_int(widget.props.get("start_time", 0), 0)
    loop = bool(widget.props.get("loop", False))
    autoplay = bool(widget.props.get("autoplay", False))
    muted = bool(widget.props.get("muted", False))
    width_val = _video_width_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 400))
    key = widget.id

    lines = [
        "# Replace with your video data",
        "# All video formats can be found in https://www.iana.org/assignments/media-types/media-types.xhtml.",
        "st.video(",
    ]
    lines.append(f"    {data!r},")
    lines.append(f"    format={fmt!r},")
    if start_time != 0:
        lines.append(f"    start_time={start_time},")
    if loop:
        lines.append("    loop=True,")
    if autoplay:
        lines.append("    autoplay=True,")
    if muted:
        lines.append("    muted=True,")
    if isinstance(width_val, str):
        lines.append(f"    width={width_val!r},")
    else:
        lines.append(f"    width={width_val},")
    lines.append(f"    key={key!r},")
    lines.append(")")
    return lines


def _render_video(widget: WidgetInstance) -> None:
    data = widget.props.get("data", "./static/mp4_sample.mp4")
    fmt = widget.props.get("format", "video/mp4")
    start_time = _safe_int(widget.props.get("start_time", 0), 0)
    loop = bool(widget.props.get("loop", False))
    autoplay = bool(widget.props.get("autoplay", False))
    muted = bool(widget.props.get("muted", False))
    width_val = _video_width_value(widget.props.get("width", "stretch"), widget.props.get("custom_width", 400))
    kwargs: dict = {
        "format": fmt,
        "start_time": start_time,
        "loop": loop,
        "autoplay": autoplay,
        "muted": muted,
        "width": width_val,
    }
    import os as _os
    video_data: object = data
    if data and not data.startswith(("http://", "https://", "data:")):
        try:
            with open(data, "rb") as _f:
                video_data = _f.read()
        except Exception:
            pass
    st.video(video_data, **kwargs)


def _render_audio_input_codegen(widget) -> list:
    label = str(widget.props.get("label", "Record audio")).strip() or "Record audio"
    key_raw = str(widget.props.get("key", "")).strip()
    if not key_raw:
        key_raw = f"audio_input_{widget.id[:8]}"
    args = [repr(label)]
    # sample_rate
    sr_raw = str(widget.props.get("sample_rate", "16000")).strip()
    if sr_raw == "None":
        args.append("sample_rate=None")
    elif sr_raw != "16000":
        args.append(f"sample_rate={sr_raw}")
    # key always generated
    args.append(f"key={key_raw!r}")
    # help
    help_raw = str(widget.props.get("help", "")).strip()
    if help_raw:
        args.append(f"help={help_raw!r}")
    # disabled
    if widget.props.get("disabled", False):
        args.append("disabled=True")
    # label_visibility
    lv = widget.props.get("label_visibility", "visible")
    if lv != "visible":
        args.append(f"label_visibility={lv!r}")
    # width
    width_mode = widget.props.get("width", "stretch")
    if width_mode == "custom":
        w = max(1, int(widget.props.get("custom_width", 320)))
        args.append(f"width={w}")
    else:
        args.append(f"width={width_mode!r}")
    return [f"audio_value = st.audio_input({', '.join(args)})"]


def _render_audio_input(widget) -> None:
    label = str(widget.props.get("label", "Record audio")).strip() or "Record audio"
    key_raw = str(widget.props.get("key", "")).strip()
    if not key_raw:
        key_raw = f"audio_input_{widget.id[:8]}"
    disabled = widget.props.get("disabled", False)
    lv = widget.props.get("label_visibility", "visible")
    width_mode = widget.props.get("width", "stretch")
    if width_mode == "custom":
        width_val = max(1, int(widget.props.get("custom_width", 320)))
    else:
        width_val = width_mode
    st.audio_input(
        label,
        key=key_raw,
        disabled=disabled,
        label_visibility=lv,
        width=width_val,
    )


def _render_camera_input_codegen(widget) -> list:
    label = str(widget.props.get("label", "Take a picture")).strip() or "Take a picture"
    key_raw = str(widget.props.get("key", "")).strip()
    if not key_raw:
        key_raw = f"camera_input_{widget.id[:8]}"
    args = [repr(label)]
    args.append(f"key={key_raw!r}")
    help_raw = str(widget.props.get("help", "")).strip()
    if help_raw:
        args.append(f"help={help_raw!r}")
    if widget.props.get("disabled", False):
        args.append("disabled=True")
    lv = widget.props.get("label_visibility", "visible")
    if lv != "visible":
        args.append(f"label_visibility={lv!r}")
    width_mode = widget.props.get("width", "stretch")
    if width_mode == "custom":
        w = max(1, int(widget.props.get("custom_width", 320)))
        args.append(f"width={w}")
    else:
        args.append(f"width={width_mode!r}")
    return [f"img_file_buffer = st.camera_input({', '.join(args)})"]


def _render_camera_input(widget) -> None:
    label = str(widget.props.get("label", "Take a picture")).strip() or "Take a picture"
    key_raw = str(widget.props.get("key", "")).strip()
    if not key_raw:
        key_raw = f"camera_input_{widget.id[:8]}"
    disabled = widget.props.get("disabled", False)
    lv = widget.props.get("label_visibility", "visible")
    width_mode = widget.props.get("width", "stretch")
    if width_mode == "custom":
        width_val = max(1, int(widget.props.get("custom_width", 320)))
    else:
        width_val = width_mode
    st.camera_input(
        label,
        key=key_raw,
        disabled=disabled,
        label_visibility=lv,
        width=width_val,
    )


def _progress_width_value(width_mode: Any, custom_width: Any) -> str | int:
    normalized = str(width_mode).strip().lower()
    if normalized == "stretch":
        return "stretch"
    if normalized == "custom":
        parsed = _safe_int(custom_width, 320)
        return parsed if parsed > 0 else "stretch"
    return "stretch"


def _codegen_progress(widget: WidgetInstance) -> List[str]:
    value = max(0, min(100, _safe_int(widget.props.get("value", 50), 50)))
    text_raw = str(widget.props.get("text", "")).strip()
    text = text_raw if text_raw else None
    width_val = _progress_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )

    lines = [
        "st.progress(",
        f"    {value},",
        f"    text={text!r},",
    ]
    lines.append(f"    width={width_val!r}," if isinstance(width_val, str) else f"    width={width_val},")
    lines.append(")")
    return lines


def _render_progress(widget: WidgetInstance) -> None:
    value = max(0, min(100, _safe_int(widget.props.get("value", 50), 50)))
    text_raw = str(widget.props.get("text", "")).strip()
    text = text_raw if text_raw else None
    width_val = _progress_width_value(
        widget.props.get("width", "stretch"), widget.props.get("custom_width", 320)
    )
    st.progress(value, text=text, width=width_val)


def register_default_widgets() -> None:
    _register = register_widget

    # --- Text elements ---
    _register(WidgetDefinition(
        type="title",
        label="Title",
        props_schema=[
            PropDefinition("text", "Text", "text", "Title"),
            PropDefinition("size", "Size", "int", 40),
            PropDefinition("color", "Color", "color", "#000000"),
            PropDefinition("horizontal_alignment", "Horizontal alignment", "select", "left", options=["left", "center", "right"]),
            PropDefinition("vertical_alignment", "Vertical alignment", "select", "center", options=["top", "center", "bottom"]),
            PropDefinition("style", "Style", "select", "normal", options=["normal", "serif", "sans-serif", "monospace"]),
            PropDefinition("bold", "Bold", "bool", True),
            PropDefinition("italic", "Italic", "bool", False),
        ],
        defaults={"text": "Title", "size": 40, "color": "#000000", "horizontal_alignment": "left", "vertical_alignment": "center", "style": "normal", "bold": True, "italic": False},
        codegen=_codegen_title,
        render=_render_title,
    ))
    _register(WidgetDefinition(
        type="header",
        label="Header",
        props_schema=[
            PropDefinition("text", "Text", "text", "Header"),
            PropDefinition("size", "Size", "int", 32),
            PropDefinition("color", "Color", "color", "#000000"),
            PropDefinition("horizontal_alignment", "Horizontal alignment", "select", "left", options=["left", "center", "right"]),
            PropDefinition("vertical_alignment", "Vertical alignment", "select", "center", options=["top", "center", "bottom"]),
            PropDefinition("style", "Style", "select", "normal", options=["normal", "serif", "sans-serif", "monospace"]),
            PropDefinition("bold", "Bold", "bool", True),
            PropDefinition("italic", "Italic", "bool", False),
        ],
        defaults={"text": "Header", "size": 32, "color": "#000000", "horizontal_alignment": "left", "vertical_alignment": "center", "style": "normal", "bold": True, "italic": False},
        codegen=_codegen_header,
        render=_render_header,
    ))
    _register(WidgetDefinition(
        type="subheader",
        label="Subheader",
        props_schema=[
            PropDefinition("text", "Text", "text", "Subheader"),
            PropDefinition("size", "Size", "int", 28),
            PropDefinition("color", "Color", "color", "#000000"),
            PropDefinition("horizontal_alignment", "Horizontal alignment", "select", "left", options=["left", "center", "right"]),
            PropDefinition("vertical_alignment", "Vertical alignment", "select", "center", options=["top", "center", "bottom"]),
            PropDefinition("style", "Style", "select", "normal", options=["normal", "serif", "sans-serif", "monospace"]),
            PropDefinition("bold", "Bold", "bool", True),
            PropDefinition("italic", "Italic", "bool", False),
        ],
        defaults={"text": "Subheader", "size": 28, "color": "#000000", "horizontal_alignment": "left", "vertical_alignment": "center", "style": "normal", "bold": True, "italic": False},
        codegen=_codegen_subheader,
        render=_render_subheader,
    ))
    _register(WidgetDefinition(
        type="markdown",
        label="Markdown",
        props_schema=[
            PropDefinition("text", "Text", "text", "Markdown"),
            PropDefinition("size", "Size", "int", 16),
            PropDefinition("color", "Color", "color", "#000000"),
            PropDefinition("horizontal_alignment", "Horizontal alignment", "select", "left", options=["left", "center", "right"]),
            PropDefinition("vertical_alignment", "Vertical alignment", "select", "center", options=["top", "center", "bottom"]),
            PropDefinition("style", "Style", "select", "normal", options=["normal", "serif", "sans-serif", "monospace"]),
            PropDefinition("bold", "Bold", "bool", False),
            PropDefinition("italic", "Italic", "bool", False),
        ],
        defaults={"text": "Markdown", "size": 16, "color": "#000000", "horizontal_alignment": "left", "vertical_alignment": "center", "style": "normal", "bold": False, "italic": False},
        codegen=_codegen_markdown,
        render=_render_markdown,
    ))
    _register(WidgetDefinition(
        type="badge",
        label="Badge",
        props_schema=[
            PropDefinition("text", "Text", "text", "Badge"),
            PropDefinition("size", "Size", "int", 14),
            PropDefinition("text_color", "Text color", "color", "#FFFFFF"),
            PropDefinition("background_color", "Background color", "color", "#2E6CF6"),
            PropDefinition("horizontal_alignment", "Horizontal alignment", "select", "left", options=["left", "center", "right"]),
            PropDefinition("vertical_alignment", "Vertical alignment", "select", "center", options=["top", "center", "bottom"]),
            PropDefinition("style", "Style", "select", "normal", options=["normal", "serif", "sans-serif", "monospace"]),
            PropDefinition("bold", "Bold", "bool", False),
            PropDefinition("italic", "Italic", "bool", False),
        ],
        defaults={"text": "Badge", "size": 14, "text_color": "#FFFFFF", "background_color": "#2E6CF6", "horizontal_alignment": "left", "vertical_alignment": "center", "style": "normal", "bold": False, "italic": False},
        codegen=_codegen_badge,
        render=_render_badge,
    ))
    _register(WidgetDefinition(
        type="caption",
        label="Caption",
        props_schema=[
            PropDefinition("text", "Text", "text", "Caption"),
            PropDefinition("size", "Size", "int", 14),
            PropDefinition("color", "Color", "color", "#000000"),
            PropDefinition("horizontal_alignment", "Horizontal alignment", "select", "left", options=["left", "center", "right"]),
            PropDefinition("vertical_alignment", "Vertical alignment", "select", "center", options=["top", "center", "bottom"]),
            PropDefinition("style", "Style", "select", "normal", options=["normal", "serif", "sans-serif", "monospace"]),
            PropDefinition("bold", "Bold", "bool", False),
            PropDefinition("italic", "Italic", "bool", False),
        ],
        defaults={"text": "Caption", "size": 14, "color": "#000000", "horizontal_alignment": "left", "vertical_alignment": "center", "style": "normal", "bold": False, "italic": False},
        codegen=_codegen_caption,
        render=_render_caption,
    ))
    _register(WidgetDefinition(
        type="code",
        label="Code",
        props_schema=[
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content"]),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch"]),
        ],
        defaults={"width": "stretch", "height": "content"},
        codegen=_codegen_code,
        render=_render_code,
    ))
    _register(WidgetDefinition(
        type="divider",
        label="Divider",
        props_schema=[
            PropDefinition("line_width", "Line width", "int", 1),
            PropDefinition("color", "Color", "color", "#D9D9D9"),
        ],
        defaults={"line_width": 1, "color": "#D9D9D9"},
        codegen=_codegen_divider,
        render=_render_divider,
    ))
    _register(WidgetDefinition(
        type="echo",
        label="Echo",
        props_schema=[
            PropDefinition("code_location", "Code location", "select", "above", options=["above", "below"]),
        ],
        defaults={"code_location": "above"},
        codegen=_codegen_echo,
        render=_render_echo,
    ))
    _register(WidgetDefinition(
        type="latex",
        label="Latex",
        props_schema=[
            PropDefinition("text", "Text", "multiline", r"x^2 + y^2 = z^2"),
            PropDefinition("help", "Help", "multiline", ""),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width (int)", "int", 320),
            PropDefinition("font_size", "Font size", "int", 16),
        ],
        defaults={"text": r"x^2 + y^2 = z^2", "help": "", "width": "stretch", "custom_width": 320, "font_size": 16},
        codegen=_codegen_latex,
        render=_render_latex,
    ))
    _register(WidgetDefinition(
        type="help",
        label="Help",
        props_schema=[
            PropDefinition("text", "Text", "text", "help text"),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (int)", "int", 320),
        ],
        defaults={"text": "help text", "width": "stretch", "custom_width": 320},
        codegen=_codegen_help,
        render=_render_help,
    ))

    # --- Data elements ---
    _register(WidgetDefinition(
        type="dataframe",
        label="DataFrame",
        props_schema=[
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "auto", options=["auto", "stretch", "content", "custom"]),
            PropDefinition("custom_height", "Custom height", "int", 320),
            PropDefinition("selection_mode", "Selection mode", "select", "multi-row", options=["single-row", "multi-row", "single-column", "multi-column", "single-cell", "multi-cell"]),
            PropDefinition("hide_index", "Hide index", "bool", False),
            PropDefinition("row_height", "Row height (int or None)", "text", ""),
        ],
        defaults={"width": "stretch", "custom_width": 320, "height": "auto", "custom_height": 320, "selection_mode": "multi-row", "hide_index": False, "row_height": ""},
        codegen=_codegen_dataframe,
        render=_render_dataframe,
    ))
    _register(WidgetDefinition(
        type="data_editor",
        label="DataEditor",
        props_schema=[
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "auto", options=["auto", "stretch", "content", "custom"]),
            PropDefinition("custom_height", "Custom height", "int", 320),
            PropDefinition("hide_index", "Hide index", "bool", False),
            PropDefinition("num_rows", "Num rows", "select", "fixed", options=["fixed", "dynamic", "add", "delete"]),
            PropDefinition("row_height", "Row height (int or None)", "text", ""),
            PropDefinition("disabled", "Disabled", "bool_select", False),
        ],
        defaults={"width": "stretch", "custom_width": 320, "height": "auto", "custom_height": 320, "hide_index": False, "num_rows": "fixed", "row_height": "", "disabled": False},
        codegen=_codegen_data_editor,
        render=_render_data_editor,
    ))

    # --- Input elements ---
    _register(WidgetDefinition(
        type="text_input",
        label="Text input",
        props_schema=[
            PropDefinition("label", "Label", "text", "Text input"),
            PropDefinition("value", "Default Value", "text", ""),
            PropDefinition("expand", "Expand", "bool", False),
        ],
        defaults={"label": "Text input", "value": "", "expand": False},
        codegen=_codegen_text_input,
        render=_render_text_input,
    ))
    _register(WidgetDefinition(
        type="text_area",
        label="Text area",
        props_schema=[
            PropDefinition("label", "Label", "text", "Text area"),
            PropDefinition("value", "Default Value", "text", ""),
            PropDefinition("expand", "Expand", "bool", False),
        ],
        defaults={"label": "Text area", "value": "", "expand": False},
        codegen=_codegen_text_area,
        render=_render_text_area,
    ))
    _register(WidgetDefinition(
        type="text",
        label="Text",
        props_schema=[
            PropDefinition("text", "Text", "text", "Text"),
            PropDefinition("size", "Size", "int", 16),
            PropDefinition("color", "Color", "color", "#000000"),
            PropDefinition("horizontal_alignment", "Horizontal alignment", "select", "left", options=["left", "center", "right"]),
            PropDefinition("vertical_alignment", "Vertical alignment", "select", "center", options=["top", "center", "bottom"]),
            PropDefinition("style", "Style", "select", "normal", options=["normal", "serif", "sans-serif", "monospace"]),
            PropDefinition("bold", "Bold", "bool", False),
            PropDefinition("italic", "Italic", "bool", False),
        ],
        defaults={"text": "Text", "size": 16, "color": "#000000", "horizontal_alignment": "left", "vertical_alignment": "center", "style": "normal", "bold": False, "italic": False},
        codegen=_codegen_text,
        render=_render_text,
    ))
    _register(WidgetDefinition(
        type="button",
        label="Button",
        props_schema=[
            PropDefinition("label", "Label", "text", "Button"),
            PropDefinition("key", "Key", "text", ""),
            PropDefinition("help", "Help tooltip", "text", ""),
            PropDefinition("type", "Button type", "select", "secondary", options=["primary", "secondary", "tertiary"]),
            PropDefinition("icon", "Icon", "text", ""),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("width", "Width", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 200),
            PropDefinition("background_color", "Background color", "color", "#FFFFFF"),
            PropDefinition("text_color", "Text color", "color", ""),
        ],
        defaults={"label": "Button", "key": "", "help": "", "type": "secondary", "icon": "", "disabled": False, "width": "content", "custom_width": 200, "background_color": "#FFFFFF", "text_color": ""},
        codegen=_codegen_button,
        render=_render_button,
    ))
    _register(WidgetDefinition(
        type="checkbox",
        label="Checkbox",
        props_schema=[
            PropDefinition("label", "Label", "text", "Checkbox"),
            PropDefinition("checked", "Checked", "bool", False),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("label_visibility", "Label visible", "bool", True),
            PropDefinition("expand", "Expand", "bool", False),
        ],
        defaults={"label": "Checkbox", "checked": False, "disabled": False, "label_visibility": True, "expand": False},
        codegen=_codegen_checkbox,
        render=_render_checkbox,
    ))
    _register(WidgetDefinition(
        type="selectbox",
        label="Selectbox",
        props_schema=[
            PropDefinition("label", "Label", "text", "Selectbox"),
            PropDefinition("options", "Options (comma separated)", "text", "Option 1, Option 2"),
            PropDefinition("index", "Selected index", "int", 0),
            PropDefinition("expand", "Expand", "bool", False),
        ],
        defaults={"label": "Selectbox", "options": "Option 1, Option 2", "index": 0, "expand": False},
        codegen=_codegen_selectbox,
        render=_render_selectbox,
    ))
    _register(WidgetDefinition(
        type="radio",
        label="Radio",
        props_schema=[
            PropDefinition("label", "Label", "text", "Radio"),
            PropDefinition("options", "Options (comma separated)", "text", "Option 1, Option 2"),
            PropDefinition("index", "Selected index", "int", 0),
        ],
        defaults={"label": "Radio", "options": "Option 1, Option 2", "index": 0},
        codegen=_codegen_radio,
        render=_render_radio,
    ))
    _register(WidgetDefinition(
        type="slider",
        label="Slider",
        props_schema=[
            PropDefinition("label", "Label", "text", "Slider"),
            PropDefinition("min", "Min", "number", 0.0),
            PropDefinition("max", "Max", "number", 100.0),
            PropDefinition("value", "Value", "number", 50.0),
            PropDefinition("step", "Step", "number", 1.0),
            PropDefinition("expand", "Expand", "bool", False),
        ],
        defaults={"label": "Slider", "min": 0.0, "max": 100.0, "value": 50.0, "step": 1.0, "expand": False},
        codegen=_codegen_slider,
        render=_render_slider,
    ))
    _register(WidgetDefinition(
        type="number_input",
        label="Number input",
        props_schema=[
            PropDefinition("label", "Label", "text", "Number input"),
            PropDefinition("min", "Min", "number", 0.0),
            PropDefinition("max", "Max", "number", 100.0),
            PropDefinition("value", "Value", "number", 0.0),
            PropDefinition("step", "Step", "number", 1.0),
            PropDefinition("expand", "Expand", "bool", False),
        ],
        defaults={"label": "Number input", "min": 0.0, "max": 100.0, "value": 0.0, "step": 1.0, "expand": False},
        codegen=_codegen_number_input,
        render=_render_number_input,
    ))
    _register(WidgetDefinition(
        type="date_input",
        label="Date input",
        props_schema=[
            PropDefinition("label", "Label", "text", "Date input"),
            PropDefinition("value", "Date (YYYY-MM-DD)", "date", date.today().isoformat()),
        ],
        defaults={"label": "Date input", "value": date.today().isoformat()},
        codegen=_codegen_date_input,
        render=_render_date_input,
    ))
    _register(WidgetDefinition(
        type="file_uploader",
        label="File uploader",
        props_schema=[
            PropDefinition("label", "Label", "text", "File uploader"),
            PropDefinition("types", "File types (comma separated)", "text", "csv, png"),
            PropDefinition("expand", "Expand", "bool", False),
        ],
        defaults={"label": "File uploader", "types": "csv, png", "expand": False},
        codegen=_codegen_file_uploader,
        render=_render_file_uploader,
    ))
    _register(WidgetDefinition(
        type="toggle",
        label="Toggle",
        props_schema=[
            PropDefinition("label", "Label", "text", "Toggle"),
            PropDefinition("value", "On", "bool", False),
        ],
        defaults={"label": "Toggle", "value": False},
        codegen=_codegen_toggle,
        render=_render_toggle,
    ))
    _register(WidgetDefinition(
        type="multiselect",
        label="Multiselect",
        props_schema=[
            PropDefinition("label", "Label", "text", "Multiselect"),
            PropDefinition("options", "Options (comma separated)", "text", "Option 1, Option 2"),
            PropDefinition("default", "Default (comma separated)", "text", ""),
            PropDefinition("expand", "Expand", "bool", False),
        ],
        defaults={"label": "Multiselect", "options": "Option 1, Option 2", "default": "", "expand": False},
        codegen=_codegen_multiselect,
        render=_render_multiselect,
    ))
    _register(WidgetDefinition(
        type="color_picker",
        label="Color picker",
        props_schema=[
            PropDefinition("label", "Label", "text", "Color picker"),
            PropDefinition("value", "Color (hex)", "color", "#00A3FF"),
        ],
        defaults={"label": "Color picker", "value": "#00A3FF"},
        codegen=_codegen_color_picker,
        render=_render_color_picker,
    ))

    # --- Layout elements ---
    _register(WidgetDefinition(
        type="container",
        label="Container",
        props_schema=[
            PropDefinition("label", "Label", "text", "Container"),
            PropDefinition("border", "Border", "select", "None", options=["None", "True", "False"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 300),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_height", "Custom height (px)", "int", 300),
            PropDefinition("horizontal", "Horizontal layout", "bool", False),
            PropDefinition("horizontal_alignment", "Horizontal alignment", "select", "left", options=["left", "center", "right", "distribute"]),
            PropDefinition("vertical_alignment", "Vertical alignment", "select", "top", options=["top", "center", "bottom", "distribute"]),
            PropDefinition("gap", "Gap", "select", "small", options=["xxsmall", "xsmall", "small", "medium", "large", "xlarge", "xxlarge", "None"]),
            PropDefinition("background_color", "Background color", "color", "#FFFFFF"),
        ],
        defaults={
            "label": "Container",
            "border": "None",
            "width": "stretch",
            "custom_width": 300,
            "height": "content",
            "custom_height": 300,
            "horizontal": False,
            "horizontal_alignment": "left",
            "vertical_alignment": "top",
            "gap": "small",
            "background_color": "#FFFFFF",
        },
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="empty",
        label="Empty",
        props_schema=[
            PropDefinition("label", "Label", "text", "Empty"),
        ],
        defaults={"label": "Empty"},
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="columns_container",
        label="Columns container",
        props_schema=[
            PropDefinition("label", "Label", "text", "Columns container"),
            PropDefinition("background_color", "Background color", "color", "#FFFFFF"),
            PropDefinition("columns", "Columns", "int", 2),
        ],
        defaults={"label": "Columns container", "background_color": "#FFFFFF", "columns": 2},
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="column",
        label="Column",
        props_schema=[
            PropDefinition("label", "Label", "text", "Column"),
            PropDefinition("background_color", "Background color", "color", "#FFFFFF"),
            PropDefinition("ratio", "Ratio", "int", 1),
        ],
        defaults={"label": "Column", "background_color": "#FFFFFF", "ratio": 1},
        codegen=_codegen_noop,
        render=_render_noop,
    ))

    # --- Table ---
    _register(WidgetDefinition(
        type="table",
        label="Table",
        props_schema=[
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom Width", "int", 0),
            PropDefinition("height", "Height", "select", "auto", options=["auto", "stretch", "content", "custom"]),
            PropDefinition("custom_height", "Custom Height", "int", 0),
            PropDefinition("border", "Border", "select", True, options=[True, False, "horizontal"]),
        ],
        defaults={"width": "stretch", "custom_width": 0, "height": "auto", "custom_height": 0, "border": True},
        codegen=_codegen_table,
        render=_render_table,
    ))

    # --- Metric ---
    _register(WidgetDefinition(
        type="metric",
        label="Metric",
        props_schema=[
            PropDefinition("label", "Label", "text", "Metric"),
            PropDefinition("value", "Value", "text", "0"),
            PropDefinition("delta", "Delta", "text", ""),
            PropDefinition("delta_color", "Delta color", "select", "normal", options=["normal", "inverse", "off", "red", "orange", "yellow", "green", "blue", "violet", "gray", "grey", "primary"]),
            PropDefinition("help", "Help", "text", ""),
            PropDefinition("label_visibility", "Label visibility", "select", "visible", options=["visible", "hidden", "collapsed"]),
            PropDefinition("border", "Border", "bool", False),
            PropDefinition("background_color", "Background color", "color", "#FFFFFF"),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_height", "Custom height (int)", "int", 120),
            PropDefinition("chart_data", "Chart data (comma separated)", "text", ""),
            PropDefinition("chart_type", "Chart type", "select", "line", options=["line", "bar", "area"]),
            PropDefinition("delta_arrow", "Delta arrow", "select", "auto", options=["auto", "up", "down", "off"]),
            PropDefinition("format", "Format", "select", "None", options=["None", "plain", "localized", "percent", "dollar", "euro", "yen", "accounting", "bytes", "compact", "scientific", "engineering", "%d", "%.2f", "%,d"]),
            PropDefinition("delta_description", "Delta description", "text", ""),
        ],
        defaults={"label": "Metric", "value": "0", "delta": "", "delta_color": "normal", "help": "", "label_visibility": "visible", "border": False, "background_color": "#FFFFFF", "width": "stretch", "custom_width": 320, "height": "content", "custom_height": 120, "chart_data": "", "chart_type": "line", "delta_arrow": "auto", "format": "None", "delta_description": ""},
        codegen=_codegen_metric,
        render=_render_metric,
    ))

    # --- Json ---
    _register(WidgetDefinition(
        type="json",
        label="Json",
        props_schema=[
            PropDefinition("expanded", "Expanded", "select", "true", options=["true", "false", "custom"]),
            PropDefinition("custom_expanded", "Custom expanded (int)", "int", 2),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "contain", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
        ],
        defaults={"expanded": "true", "custom_expanded": 2, "width": "stretch", "custom_width": 320},
        codegen=_codegen_json,
        render=_render_json,
    ))

    # --- Charts ---
    _register(WidgetDefinition(
        type="area_chart",
        label="Area chart",
        props_schema=[
            PropDefinition("x_label", "X label", "text", ""),
            PropDefinition("y_label", "Y label", "text", ""),
            PropDefinition("stack", "Stack", "select", "none", options=["none", "true", "false", "normalize", "center"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_height", "Custom height", "int", 320),
        ],
        defaults={"x_label": "", "y_label": "", "stack": "none", "width": "stretch", "custom_width": 320, "height": "content", "custom_height": 320},
        codegen=_codegen_area_chart,
        render=_render_area_chart,
    ))
    _register(WidgetDefinition(
        type="bar_chart",
        label="Bar chart",
        props_schema=[
            PropDefinition("x_label", "X label", "text", ""),
            PropDefinition("y_label", "Y label", "text", ""),
            PropDefinition("horizontal", "Horizontal", "bool", False),
            PropDefinition("sort", "Sort", "select", "true", options=["true", "false", "custom"]),
            PropDefinition("custom_sort", "Custom sort", "text", ""),
            PropDefinition("stack", "Stack", "select", "none", options=["none", "true", "false", "layered", "normalize", "center"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_height", "Custom height", "int", 320),
        ],
        defaults={"x_label": "", "y_label": "", "horizontal": False, "sort": "true", "custom_sort": "", "stack": "none", "width": "stretch", "custom_width": 320, "height": "content", "custom_height": 320},
        codegen=_codegen_bar_chart,
        render=_render_bar_chart,
    ))
    _register(WidgetDefinition(
        type="line_chart",
        label="Line chart",
        props_schema=[
            PropDefinition("x_label", "X label", "text", ""),
            PropDefinition("y_label", "Y label", "text", ""),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_height", "Custom height", "int", 320),
        ],
        defaults={"x_label": "", "y_label": "", "width": "stretch", "custom_width": 320, "height": "content", "custom_height": 320},
        codegen=_codegen_line_chart,
        render=_render_line_chart,
    ))
    _register(WidgetDefinition(
        type="map",
        label="Map",
        props_schema=[
            PropDefinition("latitude", "Latitude", "text", ""),
            PropDefinition("longitude", "Longitude", "text", ""),
            PropDefinition("size", "Size", "text", ""),
            PropDefinition("zoom", "Zoom", "int", 11),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "custom", options=["stretch", "custom"]),
            PropDefinition("custom_height", "Custom height", "int", 500),
        ],
        defaults={"latitude": "", "longitude": "", "size": "", "zoom": 11, "width": "stretch", "custom_width": 320, "height": "custom", "custom_height": 500},
        codegen=_codegen_map,
        render=_render_map,
    ))
    _register(WidgetDefinition(
        type="scatter_chart",
        label="Scatter chart",
        props_schema=[
            PropDefinition("x_label", "X label", "text", ""),
            PropDefinition("y_label", "Y label", "text", ""),
            PropDefinition("size", "Size", "text", ""),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_height", "Custom height", "int", 320),
        ],
        defaults={"x_label": "", "y_label": "", "size": "", "width": "stretch", "custom_width": 320, "height": "content", "custom_height": 320},
        codegen=_codegen_scatter_chart,
        render=_render_scatter_chart,
    ))
    _register(WidgetDefinition(
        type="graphviz_chart",
        label="Graphviz chart",
        props_schema=[
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_height", "Custom height", "int", 320),
        ],
        defaults={"width": "stretch", "custom_width": 320, "height": "content", "custom_height": 320},
        codegen=_codegen_graphviz_chart,
        render=_render_graphviz_chart,
    ))

    # --- Buttons ---
    _register(WidgetDefinition(
        type="download_button",
        label="Download button",
        props_schema=[
            PropDefinition("label", "Label", "text", "Download"),
            PropDefinition("data", "Data", "text", "Your data goes here"),
            PropDefinition("file_name", "File name", "text", "Your_file_name.txt"),
            PropDefinition("type", "Button type", "select", "secondary", options=["primary", "secondary"]),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("help", "Help tooltip", "text", ""),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={"label": "Download", "data": "Your data goes here", "file_name": "Your_file_name.txt", "type": "secondary", "disabled": False, "help": "", "width": "stretch", "custom_width": 320},
        codegen=_codegen_download_button,
        render=_render_download_button,
    ))
    _register(WidgetDefinition(
        type="link_button",
        label="Link button",
        props_schema=[
            PropDefinition("label", "Label", "text", "Link"),
            PropDefinition("url", "URL", "text", "https://www.streamlit.io"),
            PropDefinition("type", "Button type", "select", "secondary", options=["primary", "secondary", "tertiary"]),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("help", "Help tooltip", "text", ""),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={"label": "Link", "url": "https://www.streamlit.io", "type": "secondary", "disabled": False, "help": "", "width": "stretch", "custom_width": 320},
        codegen=_codegen_link_button,
        render=_render_link_button,
    ))
    _register(WidgetDefinition(
        type="page_link",
        label="Page link",
        props_schema=[
            PropDefinition("page", "Page / URL", "text", "https://www.streamlit.io"),
            PropDefinition("label", "Label", "text", "Page link"),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("help", "Help tooltip", "text", ""),
            PropDefinition("width", "Width", "select", "content", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={"page": "https://www.streamlit.io", "label": "Page link", "disabled": False, "help": "", "width": "content", "custom_width": 320},
        codegen=_codegen_page_link,
        render=_render_page_link,
    ))
    _register(WidgetDefinition(
        type="feedback",
        label="Feedback",
        props_schema=[
            PropDefinition("options", "Options", "select", "thumbs", options=["thumbs", "faces", "stars"]),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("width", "Width", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={"options": "thumbs", "disabled": False, "width": "content", "custom_width": 320},
        codegen=_codegen_feedback,
        render=_render_feedback,
    ))
    _register(WidgetDefinition(
        type="pills",
        label="Pills",
        props_schema=[
            PropDefinition("label", "Label", "text", "Pills"),
            PropDefinition("options", "Options (comma separated)", "text", "Option 1, Option 2, Option 3"),
            PropDefinition("selection_mode", "Selection mode", "select", "single", options=["single", "multi"]),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("help", "Help", "text", ""),
            PropDefinition("label_visibility", "Label visibility", "select", "visible", options=["visible", "hidden", "collapsed"]),
            PropDefinition("width", "Width", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
        ],
        defaults={"label": "Pills", "options": "Option 1, Option 2, Option 3", "selection_mode": "single", "disabled": False, "help": "", "label_visibility": "visible", "width": "content", "custom_width": 320},
        codegen=_codegen_pills,
        render=_render_pills,
    ))
    _register(WidgetDefinition(
        type="segmented_control",
        label="Segmented control",
        props_schema=[
            PropDefinition("label", "Label", "text", "Segmented control"),
            PropDefinition("options", "Options (comma separated)", "text", "Option 1, Option 2, Option 3"),
            PropDefinition("selection_mode", "Selection mode", "select", "single", options=["single", "multi"]),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("help", "Help", "text", ""),
            PropDefinition("label_visibility", "Label visibility", "select", "visible", options=["visible", "hidden", "collapsed"]),
            PropDefinition("width", "Width", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
        ],
        defaults={"label": "Segmented control", "options": "Option 1, Option 2, Option 3", "selection_mode": "single", "disabled": False, "help": "", "label_visibility": "visible", "width": "content", "custom_width": 320},
        codegen=_codegen_segmented_control,
        render=_render_segmented_control,
    ))
    _register(WidgetDefinition(
        type="select_slider",
        label="Select slider",
        props_schema=[
            PropDefinition("label", "Label", "text", "Select slider"),
            PropDefinition("options", "Options (comma separated)", "text", "Option 1, Option 2, Option 3"),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("help", "Help", "text", ""),
            PropDefinition("label_visibility", "Label visibility", "select", "visible", options=["visible", "hidden", "collapsed"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
        ],
        defaults={"label": "Select slider", "options": "Option 1, Option 2, Option 3", "disabled": False, "help": "", "label_visibility": "visible", "width": "stretch", "custom_width": 320},
        codegen=_codegen_select_slider,
        render=_render_select_slider,
    ))
    _register(WidgetDefinition(
        type="datetime_input",
        label="Datetime input",
        props_schema=[
            PropDefinition("label", "Label", "text", "Datetime input"),
            PropDefinition("value", "Value", "text", "now"),
            PropDefinition("min_value", "Min value", "text", ""),
            PropDefinition("max_value", "Max value", "text", ""),
            PropDefinition("format", "Format", "select", "YYYY/MM/DD", options=["YYYY/MM/DD", "DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "DD-MM-YYYY", "MM-DD-YYYY", "YYYY.MM.DD", "DD.MM.YYYY", "MM.DD.YYYY"]),
            PropDefinition("step", "Step (seconds)", "int", 900),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("help", "Help", "text", ""),
            PropDefinition("label_visibility", "Label visibility", "select", "visible", options=["visible", "hidden", "collapsed"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
        ],
        defaults={"label": "Datetime input", "value": "now", "min_value": "", "max_value": "", "format": "YYYY/MM/DD", "step": 900, "disabled": False, "help": "", "label_visibility": "visible", "width": "stretch", "custom_width": 320},
        codegen=_codegen_datetime_input,
        render=_render_datetime_input,
    ))
    _register(WidgetDefinition(
        type="time_input",
        label="Time input",
        props_schema=[
            PropDefinition("label", "Label", "text", "Time input"),
            PropDefinition("value", "Value", "text", "now"),
            PropDefinition("step", "Step (seconds)", "int", 900),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("help", "Help", "text", ""),
            PropDefinition("label_visibility", "Label visibility", "select", "visible", options=["visible", "hidden", "collapsed"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
        ],
        defaults={"label": "Time input", "value": "now", "step": 900, "disabled": False, "help": "", "label_visibility": "visible", "width": "stretch", "custom_width": 320},
        codegen=_codegen_time_input,
        render=_render_time_input,
    ))
    _register(WidgetDefinition(
        type="chat_input",
        label="Chat input",
        props_schema=[
            PropDefinition("placeholder", "Placeholder", "text", "Your message"),
            PropDefinition("key", "Key", "text", ""),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={"placeholder": "Your message", "key": "", "disabled": False, "width": "stretch", "custom_width": 320},
        codegen=_codegen_chat_input,
        render=_render_chat_input,
    ))
    _register(WidgetDefinition(
        type="audio",
        label="Audio",
        props_schema=[
            PropDefinition("format", "Format", "select", "audio/wav", options=["audio/wav", "audio/mp3", "audio/ogg", "audio/mpeg", "audio/flac"]),
            PropDefinition("start_time", "Start time (seconds)", "int", 0),
            PropDefinition("loop", "Loop", "bool", False),
            PropDefinition("autoplay", "Autoplay", "bool", False),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={"format": "audio/wav", "start_time": 0, "loop": False, "autoplay": False, "width": "stretch", "custom_width": 320},
        codegen=_codegen_audio,
        render=_render_audio,
    ))
    _register(WidgetDefinition(
        type="image",
        label="Image",
        props_schema=[
            PropDefinition("image", "Image URL", "text", "./static/img_placeholder.jpg"),
            PropDefinition("caption", "Caption", "text", ""),
            PropDefinition("width", "Width", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_width", "Custom width", "int", 320),
            PropDefinition("output_format", "Output format", "select", "auto", options=["auto", "JPEG", "PNG"]),
        ],
        defaults={
            "image": "./static/img_placeholder.jpg",
            "caption": "",
            "width": "content",
            "custom_width": 320,
            "output_format": "auto",
        },
        codegen=_codegen_image,
        render=_render_image,
    ))
    _register(WidgetDefinition(
        type="logo",
        label="Logo",
        props_schema=[
            PropDefinition("image", "Image URL", "text", "./static/img_placeholder.jpg"),
            PropDefinition("size", "Size", "select", "medium", options=["small", "medium", "large"]),
            PropDefinition("icon_image", "Icon image URL", "text", ""),
        ],
        defaults={"image": "./static/img_placeholder.jpg", "size": "medium", "icon_image": ""},
        codegen=_codegen_logo,
        render=_render_logo,
    ))
    _register(WidgetDefinition(
        type="pdf",
        label="PDF",
        props_schema=[
            PropDefinition("data", "PDF data / URL", "text", "https://example.com/sample.pdf"),
            PropDefinition("height", "Height", "select", "custom", options=["custom", "stretch"]),
            PropDefinition("custom_height", "Custom height (px)", "int", 500),
            PropDefinition("key", "Key", "text", ""),
        ],
        defaults={"data": "https://example.com/sample.pdf", "height": "custom", "custom_height": 500, "key": ""},
        codegen=_codegen_pdf,
        render=_render_pdf,
    ))
    _register(WidgetDefinition(
        type="expander",
        label="Expander",
        props_schema=[
            PropDefinition("label", "Label", "text", "Expander"),
            PropDefinition("expanded", "Expanded by default", "bool", False),
            PropDefinition("key", "Key", "text", ""),
            PropDefinition("icon", "Icon", "text", ""),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 400),
            PropDefinition("on_change", "On change", "select", "ignore", options=["ignore", "rerun"]),
        ],
        defaults={"label": "Expander", "expanded": False, "key": "", "icon": "", "disabled": False, "width": "stretch", "custom_width": 400, "on_change": "ignore"},
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="form",
        label="Form",
        props_schema=[
            PropDefinition("label", "Label", "text", "Form"),
            PropDefinition("key", "Key", "text", ""),
            PropDefinition("clear_on_submit", "Clear on submit", "bool", False),
            PropDefinition("enter_to_submit", "Enter to submit", "bool", True),
            PropDefinition("border", "Border", "bool", True),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "content", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 300),
            PropDefinition("height", "Height", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_height", "Custom height (px)", "int", 300),
        ],
        defaults={
            "label": "Form",
            "key": "",
            "clear_on_submit": False,
            "enter_to_submit": True,
            "border": True,
            "width": "stretch",
            "custom_width": 300,
            "height": "content",
            "custom_height": 300,
        },
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="popover",
        label="Popover",
        props_schema=[
            PropDefinition("label", "Label", "text", "Popover"),
            PropDefinition("type", "Button type", "select", "secondary", options=["primary", "secondary", "tertiary"]),
            PropDefinition("help", "Help tooltip", "text", ""),
            PropDefinition("icon", "Icon", "text", ""),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("width", "Width", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 300),
            PropDefinition("key", "Key", "text", ""),
            PropDefinition("on_change", "On change", "select", "ignore", options=["ignore", "rerun"]),
        ],
        defaults={
            "label": "Popover",
            "type": "secondary",
            "help": "",
            "icon": "",
            "disabled": False,
            "width": "content",
            "custom_width": 300,
            "key": "",
            "on_change": "ignore",
        },
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="audio_input",
        label="Audio input",
        props_schema=[
            PropDefinition("label", "Label", "text", "Record audio"),
            PropDefinition("sample_rate", "Sample rate (Hz)", "select", "16000",
                           options=["8000", "11025", "16000", "22050", "24000", "32000", "44100", "48000", "None"]),
            PropDefinition("key", "Key", "text", ""),
            PropDefinition("help", "Help tooltip", "text", ""),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("label_visibility", "Label visibility", "select", "visible",
                           options=["visible", "hidden", "collapsed"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={
            "label": "Record audio",
            "sample_rate": "16000",
            "key": "",
            "help": "",
            "disabled": False,
            "label_visibility": "visible",
            "width": "stretch",
            "custom_width": 320,
        },
        codegen=_render_audio_input_codegen,
        render=_render_audio_input,
    ))
    _register(WidgetDefinition(
        type="camera_input",
        label="Camera input",
        props_schema=[
            PropDefinition("label", "Label", "text", "Take a picture"),
            PropDefinition("key", "Key", "text", ""),
            PropDefinition("help", "Help tooltip", "text", ""),
            PropDefinition("disabled", "Disabled", "bool", False),
            PropDefinition("label_visibility", "Label visibility", "select", "visible",
                           options=["visible", "hidden", "collapsed"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={
            "label": "Take a picture",
            "key": "",
            "help": "",
            "disabled": False,
            "label_visibility": "visible",
            "width": "stretch",
            "custom_width": 320,
        },
        codegen=_render_camera_input_codegen,
        render=_render_camera_input,
    ))
    _register(WidgetDefinition(
        type="video",
        label="Video",
        props_schema=[
            PropDefinition("start_time", "Start time (seconds)", "int", 0),
            PropDefinition("loop", "Loop", "bool", False),
            PropDefinition("autoplay", "Autoplay", "bool", False),
            PropDefinition("muted", "Muted", "bool", False),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 400),
            PropDefinition("key", "Key", "text", ""),
        ],
        defaults={"data": "./static/mp4_sample.mp4", "format": "video/mp4", "start_time": 0,
                  "loop": False, "autoplay": False, "muted": False, "width": "stretch", "custom_width": 400, "key": ""},
        codegen=_codegen_video,
        render=_render_video,
    ))
    _register(WidgetDefinition(
        type="sidebar",
        label="Sidebar",
        props_schema=[
            PropDefinition("label", "Label", "text", "Sidebar"),
        ],
        defaults={"label": "Sidebar"},
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="tabs",
        label="Tabs",
        props_schema=[
            PropDefinition("label", "Label", "text", "Tabs"),
            PropDefinition("tabs", "Number of tabs", "int", 2),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
            PropDefinition("default", "Default tab label", "text", ""),
        ],
        defaults={"label": "Tabs", "tabs": 2, "width": "stretch", "custom_width": 320, "default": ""},
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="tab",
        label="Tab",
        props_schema=[
            PropDefinition("label", "Label", "text", "Tab"),
        ],
        defaults={"label": "Tab"},
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="status",
        label="Status",
        props_schema=[
            PropDefinition("label", "Label", "text", "Status"),
            PropDefinition("expanded", "Expanded", "bool", False),
            PropDefinition("state", "State", "select", "running",
                           options=["running", "complete", "error"]),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={
            "label": "Status",
            "expanded": False,
            "state": "running",
            "width": "stretch",
            "custom_width": 320,
        },
        codegen=_codegen_noop,
        render=_render_noop,
    ))
    _register(WidgetDefinition(
        type="progress",
        label="Progress",
        props_schema=[
            PropDefinition("value", "Value (0-100)", "int", 50),
            PropDefinition("text", "Text", "text", ""),
            PropDefinition("width", "Width", "select", "stretch", options=["stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={"value": 50, "text": "", "width": "stretch", "custom_width": 320},
        codegen=_codegen_progress,
        render=_render_progress,
    ))
    _register(WidgetDefinition(
        type="spinner",
        label="Spinner",
        props_schema=[
            PropDefinition("text", "Text", "text", "In progress..."),
            PropDefinition("show_time", "Show time", "bool", False),
            PropDefinition("width", "Width", "select", "content", options=["content", "stretch", "custom"]),
            PropDefinition("custom_width", "Custom width (px)", "int", 320),
        ],
        defaults={"text": "In progress...", "show_time": False, "width": "content", "custom_width": 320},
        codegen=_codegen_noop,
        render=_render_noop,
    ))
