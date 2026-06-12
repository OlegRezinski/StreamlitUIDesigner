from __future__ import annotations

from typing import List

from .backgrounds import background_style_html
from .models import Design
from .registry import get_widget


def _normalize_column_labels(count: int, labels: List[str]) -> List[str]:
    if count < 1:
        count = 1
    cleaned = [label.strip() for label in labels if label.strip()]
    result = cleaned[:count]
    while len(result) < count:
        result.append(f"Column {len(result) + 1}")
    return result


def _normalize_tab_labels(count: int, labels: List[str]) -> List[str]:
    if count < 1:
        count = 1
    cleaned = [label.strip() for label in labels if label.strip()]
    result = cleaned[:count]
    while len(result) < count:
        result.append(f"Tab {len(result) + 1}")
    return result


def _build_children_map(design: Design) -> dict[str, list]:
    children: dict[str, list] = {}
    for widget in design.widgets:
        if not widget.parent_id:
            continue
        children.setdefault(widget.parent_id, []).append(widget)
    return children



def generate_streamlit_code(design: Design) -> str:
    lines: List[str] = ["import streamlit as st"]

    uses_date = any(widget.type == "date_input" for widget in design.widgets)
    if uses_date:
        lines.append("from datetime import date")

    screen_width = getattr(design, "screen_width", "regular")
    if screen_width == "wide":
        lines.append("st.set_page_config(layout=\"wide\")")

    background_color = getattr(design, "background_color", "")
    background_image_raw = getattr(design, "background_image", "")
    style_html = background_style_html(".stApp", background_color, background_image_raw)
    if style_html:
        lines.append(f"st.markdown({style_html!r}, unsafe_allow_html=True)")

    lines.append("")
    children = _build_children_map(design)
    column_counter = {"value": 0}
    tabs_counter = {"value": 0}

    def _emit_widget(widget, indent: str) -> None:
        if widget.type == "container":
            label = str(widget.props.get("label", "Container")).strip() or "Container"
            lines.append(f"{indent}# {label}")

            args = []

            border_raw = str(widget.props.get("border", "None"))
            if border_raw == "True":
                args.append("border=True")
            elif border_raw == "False":
                args.append("border=False")

            width_mode = widget.props.get("width", "stretch")
            if width_mode == "custom":
                try:
                    w = max(1, int(widget.props.get("custom_width", 300)))
                except (TypeError, ValueError):
                    w = 300
                args.append(f"width={w}")
            else:
                args.append(f"width={width_mode!r}")

            height_mode = widget.props.get("height", "content")
            if height_mode == "custom":
                try:
                    h = max(1, int(widget.props.get("custom_height", 300)))
                except (TypeError, ValueError):
                    h = 300
                args.append(f"height={h}")
            else:
                args.append(f"height={height_mode!r}")

            if bool(widget.props.get("horizontal", False)):
                args.append("horizontal=True")

            h_align = widget.props.get("horizontal_alignment", "left")
            if h_align != "left":
                args.append(f"horizontal_alignment={h_align!r}")

            v_align = widget.props.get("vertical_alignment", "top")
            if v_align != "top":
                args.append(f"vertical_alignment={v_align!r}")

            gap = widget.props.get("gap", "small")
            if gap != "small":
                args.append("gap=None" if gap == "None" else f"gap={gap!r}")

            background_color = str(widget.props.get("background_color", "#FFFFFF")).strip()

            lines.append(f"{indent}with st.container({', '.join(args)}):")

            if background_color and background_color != "#FFFFFF":
                anchor = f"container-{widget.id}"
                lines.append(f"{indent}    st.markdown('<div id=\"{anchor}\"></div>', unsafe_allow_html=True)")
                lines.append(
                    f"{indent}    st.markdown('<style>#{anchor} + div {{ background-color: {background_color}; padding: 0.5rem; border-radius: 0.25rem; }}</style>', unsafe_allow_html=True)"
                )

            nested = children.get(widget.id, [])
            if not nested:
                lines.append(f"{indent}    pass")
            else:
                for child in nested:
                    _emit_widget(child, indent + "    ")
            return
        if widget.type == "empty":
            label = str(widget.props.get("label", "Empty")).strip() or "Empty"
            lines.append(f"{indent}# {label}")
            lines.append(f"{indent}with st.empty():")
            nested = children.get(widget.id, [])
            if not nested:
                lines.append(f"{indent}    # Add elements here; each will replace the previous one")
            else:
                for child in nested:
                    _emit_widget(child, indent + "    ")
            return
        if widget.type == "columns_container":
            columns = [
                child for child in children.get(widget.id, []) if child.type == "column"
            ]
            desired = int(widget.props.get("columns", len(columns) or 0))
            desired = max(0, desired)
            if desired == 0:
                return
            if not columns:
                columns = [None] * desired

            cols_name = "cols" if column_counter["value"] == 0 else f"cols_{column_counter['value'] + 1}"
            column_counter["value"] += 1
            lines.append(f"{indent}# {widget.props.get('label', 'Columns')}")

            background_color = str(widget.props.get("background_color", "")).strip()
            if background_color:
                anchor = f"cols-{widget.id}"
                lines.append(f"{indent}st.markdown('<div id=\"{anchor}\"></div>', unsafe_allow_html=True)")
                css_parts = [
                    f"#{anchor} + div [data-testid=\"column\"] {{ "
                    f"background-color: {background_color}; padding: 0.5rem; border-radius: 0.25rem; }}"
                ]
                for idx, col in enumerate(columns, start=1):
                    if not col:
                        continue
                    col_bg = str(col.props.get("background_color", "")).strip()
                    if col_bg:
                        css_parts.append(
                            f"#{anchor} + div [data-testid=\"column\"]:nth-of-type({idx}) {{ "
                            f"background-color: {col_bg}; }}"
                        )
                lines.append(
                    f"{indent}st.markdown('<style>{''.join(css_parts)}</style>', unsafe_allow_html=True)"
                )

            ratios = [max(1, int(col.props.get("ratio", 1))) if col else 1 for col in columns]
            lines.append(f"{indent}{cols_name} = st.columns({ratios!r})")

            for idx, col in enumerate(columns):
                if not col:
                    continue
                nested = children.get(col.id, [])
                if not nested:
                    continue
                lines.append(f"{indent}with {cols_name}[{idx}]:")
                for child in nested:
                    _emit_widget(child, indent + "    ")
            return
        if widget.type == "column":
            return
        if widget.type == "expander":
            label = str(widget.props.get("label", "Expander")).strip() or "Expander"
            lines.append(f"{indent}# {label}")
            args = [repr(label)]
            expanded = widget.props.get("expanded", False)
            if expanded:
                args.append("expanded=True")
            icon_raw = str(widget.props.get("icon", "")).strip()
            if icon_raw:
                args.append(f"icon={icon_raw!r}")
            width_mode = widget.props.get("width", "stretch")
            if width_mode == "custom":
                args.append(f"width={max(1, int(widget.props.get('custom_width', 400)))}")
            else:
                args.append(f"width={width_mode!r}")
            on_change = widget.props.get("on_change", "ignore")
            if on_change != "ignore":
                args.append("on_change=st.rerun")
                key_raw = str(widget.props.get("key", "")).strip()
                if not key_raw:
                    key_raw = f"expander_{widget.id[:8]}"
                args.append(f"key={key_raw!r}")
            lines.append(f"{indent}with st.expander({', '.join(args)}):")
            nested = children.get(widget.id, [])
            if not nested:
                lines.append(f"{indent}    pass")
            else:
                for child in nested:
                    _emit_widget(child, indent + "    ")
            return
        if widget.type == "form":
            label = str(widget.props.get("label", "Form")).strip() or "Form"
            lines.append(f"{indent}# {label}")
            key_raw = str(widget.props.get("key", "")).strip()
            if not key_raw:
                key_raw = f"form_{widget.id[:8]}"
            args = [repr(key_raw)]
            clear_on_submit = widget.props.get("clear_on_submit", False)
            if clear_on_submit:
                args.append("clear_on_submit=True")
            enter_to_submit = widget.props.get("enter_to_submit", True)
            if not enter_to_submit:
                args.append("enter_to_submit=False")
            border = widget.props.get("border", True)
            if not border:
                args.append("border=False")
            width_mode = widget.props.get("width", "stretch")
            if width_mode == "custom":
                args.append(f"width={max(1, int(widget.props.get('custom_width', 300)))}")
            else:
                args.append(f"width={width_mode!r}")
            height_mode = widget.props.get("height", "content")
            if height_mode == "custom":
                args.append(f"height={max(1, int(widget.props.get('custom_height', 300)))}")
            else:
                args.append(f"height={height_mode!r}")
            lines.append(f"{indent}with st.form({', '.join(args)}):")
            nested = children.get(widget.id, [])
            if not nested:
                lines.append(f"{indent}    st.form_submit_button('Submit')")
            else:
                for child in nested:
                    _emit_widget(child, indent + "    ")
                lines.append(f"{indent}    st.form_submit_button('Submit')")
            return

        if widget.type == "popover":
            label = str(widget.props.get("label", "Popover")).strip() or "Popover"
            lines.append(f"{indent}# {label}")
            args = [repr(label)]
            btn_type = widget.props.get("type", "secondary")
            if btn_type != "secondary":
                args.append(f"type={btn_type!r}")
            help_raw = str(widget.props.get("help", "")).strip()
            if help_raw:
                args.append(f"help={help_raw!r}")
            icon_raw = str(widget.props.get("icon", "")).strip()
            if icon_raw:
                args.append(f"icon={icon_raw!r}")
            disabled = widget.props.get("disabled", False)
            if disabled:
                args.append("disabled=True")
            width_mode = widget.props.get("width", "content")
            if width_mode == "custom":
                args.append(f"width={max(1, int(widget.props.get('custom_width', 300)))}")
            else:
                args.append(f"width={width_mode!r}")
            on_change = widget.props.get("on_change", "ignore")
            if on_change != "ignore":
                args.append("on_change=st.rerun")
                key_raw = str(widget.props.get("key", "")).strip()
                if not key_raw:
                    key_raw = f"popover_{widget.id[:8]}"
                args.append(f"key={key_raw!r}")
            lines.append(f"{indent}with st.popover({', '.join(args)}):")
            nested = children.get(widget.id, [])
            if not nested:
                lines.append(f"{indent}    pass")
            else:
                for child in nested:
                    _emit_widget(child, indent + "    ")
            return

        if widget.type == "status":
            label = str(widget.props.get("label", "Status")).strip() or "Status"
            lines.append(f"{indent}# {label}")
            args = [repr(label)]
            expanded = widget.props.get("expanded", False)
            if expanded:
                args.append("expanded=True")
            state = widget.props.get("state", "running")
            if state != "running":
                args.append(f"state={state!r}")
            width_mode = widget.props.get("width", "stretch")
            if width_mode == "custom":
                args.append(f"width={max(1, int(widget.props.get('custom_width', 320)))}")
            else:
                args.append(f"width={width_mode!r}")
            lines.append(f"{indent}with st.status({', '.join(args)}):")
            nested = children.get(widget.id, [])
            if not nested:
                lines.append(f"{indent}    pass")
            else:
                for child in nested:
                    _emit_widget(child, indent + "    ")
            return

        if widget.type == "spinner":
            text = str(widget.props.get("text", "In progress...")).strip() or "In progress..."
            lines.append(f"{indent}# Spinner")
            args = [repr(text)]
            show_time = widget.props.get("show_time", False)
            if show_time:
                args.append("show_time=True")
            width_mode = widget.props.get("width", "content")
            if width_mode == "custom":
                try:
                    w = max(1, int(widget.props.get("custom_width", 320)))
                except (TypeError, ValueError):
                    w = 320
                args.append(f"width={w}")
            elif width_mode != "content":
                args.append(f"width={width_mode!r}")
            lines.append(f"{indent}with st.spinner({', '.join(args)}):")
            nested = children.get(widget.id, [])
            if not nested:
                lines.append(f"{indent}    pass")
            else:
                for child in nested:
                    _emit_widget(child, indent + "    ")
            return

        if widget.type == "sidebar":
            label = str(widget.props.get("label", "Sidebar")).strip() or "Sidebar"
            lines.append(f"{indent}# {label}")
            lines.append(f"{indent}with st.sidebar:")
            nested = children.get(widget.id, [])
            if not nested:
                lines.append(f"{indent}    pass")
            else:
                for child in nested:
                    _emit_widget(child, indent + "    ")
            return

        if widget.type == "tabs":
            label = str(widget.props.get("label", "Tabs")).strip() or "Tabs"
            lines.append(f"{indent}# {label}")
            tab_widgets = [child for child in children.get(widget.id, []) if child.type == "tab"]
            desired = max(1, int(widget.props.get("tabs", len(tab_widgets) or 2)))
            tab_labels_raw = [str(t.props.get("label", "")).strip() for t in tab_widgets]
            tab_labels = _normalize_tab_labels(desired, tab_labels_raw)

            tabs_name = "tabs_1" if tabs_counter["value"] == 0 else f"tabs_{tabs_counter['value'] + 1}"
            tabs_counter["value"] += 1

            width_mode = widget.props.get("width", "stretch")
            if width_mode == "custom":
                try:
                    width_val: str | int = max(1, int(widget.props.get("custom_width", 320)))
                except (TypeError, ValueError):
                    width_val = "stretch"
            else:
                width_val = "stretch"

            default_raw = str(widget.props.get("default", "")).strip()
            if default_raw and default_raw in tab_labels:
                default_part = f", default={default_raw!r}"
            else:
                default_part = ""

            if isinstance(width_val, int):
                lines.append(f"{indent}{tabs_name} = st.tabs({tab_labels!r}, width={width_val}{default_part})")
            else:
                lines.append(f"{indent}{tabs_name} = st.tabs({tab_labels!r}, width={width_val!r}{default_part})")

            for i, tab_widget in enumerate(tab_widgets[:desired]):
                tab_children = children.get(tab_widget.id, [])
                lines.append(f"{indent}with {tabs_name}[{i}]:")
                if not tab_children:
                    lines.append(f"{indent}    pass")
                else:
                    for child in tab_children:
                        _emit_widget(child, indent + "    ")
            # Handle tabs without matching tab_widgets
            for i in range(len(tab_widgets), desired):
                lines.append(f"{indent}with {tabs_name}[{i}]:")
                lines.append(f"{indent}    pass")
            return

        if widget.type == "tab":
            return

        definition = get_widget(widget.type)
        widget_lines = definition.codegen(widget)
        for line in widget_lines:
            lines.append(f"{indent}{line}")

    for widget in design.widgets:
        if widget.parent_id:
            continue
        _emit_widget(widget, "")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

