from __future__ import annotations

import uuid
from datetime import date
from pathlib import Path
from typing import Dict, List

import streamlit as st
from streamlit.errors import StreamlitAPIException
from streamlit.string_util import validate_icon_or_emoji
from streamlit_tree_select import tree_select

from designer.backgrounds import css_url_value
from designer.codegen import generate_streamlit_code
from designer.code_import import import_design_from_code
from designer.models import Design, PropDefinition, WidgetInstance
from designer.registry import clear_registry, list_widgets
from designer.widgets import register_default_widgets, reset_preview_keys


MAIN_CONTAINER_ID = "__main__"
ELEMENTS_FILE = Path(__file__).resolve().parent / "Elements.txt"
MATERIAL_ICON_BY_TYPE = {
    "badge": ":material/bookmark:",
    "button": ":material/buttons_alt:",
    "caption": ":material/short_text:",
    "checkbox": ":material/check_box:",
    "code": ":material/code:",
    "color_picker": ":material/color_lens:",
    "container": ":material/iframe:",
    "columns_container": ":material/view_column:",
    "empty": ":material/crop_5_4:",
    "expander": ":material/expand_content:",
    "form": ":material/assignment:",
    "popover": ":material/open_in_new:",
    "date_input": ":material/date_range:",
    "download_button": ":material/download:",
    "file_uploader": ":material/upload:",
    "header": ":material/format_size:",
    "markdown": ":material/markdown:",
    "metric": ":material/monitoring:",
    "multiselect": ":material/checklist:",
    "number_input": ":material/filter_9_plus:",
    "radio": ":material/radio_button_checked:",
    "selectbox": ":material/arrow_drop_down_circle:",
    "slider": ":material/linear_scale:",
    "subheader": ":material/subtitles:",
    "text": ":material/text_fields:",
    "title": ":material/text_fields:",
    "text_area": ":material/subject:",
    "text_input": ":material/edit:",
    "toggle": ":material/toggle_on:",
    "audio_input": ":material/mic:",
    "camera_input": ":material/photo_camera:",
    "sidebar": ":material/side_navigation:",
    "tabs": ":material/tab:",
    "tab": ":material/tab:",
    "status": ":material/info:",
    "spinner": ":material/progress_activity:",
}
ELEMENT_TYPE_ALIASES = {
    "columns": "columns_container",
}
CATEGORY_ICON_BY_TITLE = {
    "Text elements": ":material/text_fields:",
    "Data elements": ":material/table_view:",
    "Chart elements": ":material/insert_chart:",
    "Input elements": ":material/touch_app:",
    "Media elements": ":material/photo_library:",
    "Layouts and containers": ":material/dashboard_customize:",
    "Chat elements": ":material/chat:",
    "OTHER": ":material/more_horiz:",
}
ELEMENT_ICON_BY_NAME = {
    "title": ":material/text_fields:",
    "header": ":material/format_size:",
    "subheader": ":material/subtitles:",
    "markdown": ":material/markdown:",
    "badge": ":material/bookmark:",
    "caption": ":material/short_text:",
    "code": ":material/code:",
    "divider": ":material/horizontal_rule:",
    "echo": ":material/record_voice_over:",
    "latex": ":material/functions:",
    "help": ":material/help:",
    "html": ":material/html:",
    "dataframe": ":material/table:",
    "data_editor": ":material/edit_note:",
    "table": ":material/table_rows:",
    "metric": ":material/monitoring:",
    "json": ":material/data_object:",
    "area_chart": ":material/area_chart:",
    "bar_chart": ":material/bar_chart:",
    "line_chart": ":material/show_chart:",
    "map": ":material/map:",
    "scatter_chart": ":material/scatter_plot:",
    "graphviz_chart": ":material/account_tree:",
    "pyplot": ":material/ssid_chart:",
    "vega_lite_chart": ":material/insights:",
    "download_button": ":material/download:",
    "link_button": ":material/link:",
    "page_link": ":material/open_in_new:",
    "feedback": ":material/rate_review:",
    "pills": ":material/pill:",
    "segmented_control": ":material/tune:",
    "select_slider": ":material/sliders:",
    "datetime_input": ":material/event:",
    "time_input": ":material/schedule:",
    "chat_input": ":material/forum:",
    "audio_input": ":material/mic:",
    "camera_input": ":material/photo_camera:",

    "audio": ":material/audio_file:",
    "image": ":material/image:",
    "logo": ":material/branding_watermark:",
    "pdf": ":material/picture_as_pdf:",
    "video": ":material/video_library:",
    "dialog": ":material/web_asset:",
    "empty": ":material/crop_5_4:",
    "expander": ":material/expand_content:",
    "form": ":material/list_alt:",
    "popover": ":material/open_in_new_down:",
    "sidebar": ":material/left_panel_open:",
    "tabs": ":material/tab:",
    "chat_message": ":material/chat_bubble:",
    "status": ":material/info:",
    "write_stream": ":material/stream:",
    "progress": ":material/progress_activity:",
    "spinner": ":material/progress_activity:",
}

SCROLLABLE_PANE_HEIGHT = 720
PALETTE_FIXED_TOP_REM = 0.0
PAGE_TOP_OFFSET_REM = 5.25
PREVIEW_SIDEBAR_EXPANDED_RATIO = [3, 7]
PREVIEW_SIDEBAR_COLLAPSED_RATIO = [0.6, 9.4]


def _inject_layout_css() -> None:
    st.markdown(
        f"""
        <style>
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        .block-container {{
            padding-top: 0 !important;
        }}

        .st-key-ui1_palette_dock {{
            position: fixed;
            top: {PALETTE_FIXED_TOP_REM}rem;
            left: 0;
            right: 0;
            z-index: 999;
            background: var(--background-color, white);
            padding: 0.75rem 1rem 0.75rem 1rem;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
        }}

        .st-key-ui1_palette_dock [data-testid="stHorizontalBlock"] {{
            row-gap: 0.5rem;
        }}

        .st-key-ui1_page_offset {{
            height: {PAGE_TOP_OFFSET_REM}rem;
        }}

        /* Keep properties pane width visually stable when vertical scrollbar appears. */
        .st-key-ui1_properties_pane [data-testid="stVerticalBlockBorderWrapper"] {{
            scrollbar-gutter: stable;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_page_offset() -> None:
    st.container(key="ui1_page_offset")


def _load_palette_groups() -> list[tuple[str, list[str]]]:
    groups: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_items: list[str] = []

    for raw_line in ELEMENTS_FILE.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if not raw_line[:1].isspace() and not stripped.startswith("st."):
            if current_title is not None:
                groups.append((current_title, current_items))
            current_title = stripped.rstrip(":")
            current_items = []
            continue
        if stripped.startswith("st.") and current_title is not None:
            current_items.append(stripped)

    if current_title is not None:
        groups.append((current_title, current_items))

    return groups


def _normalize_palette_element_name(element_name: str) -> str:
    normalized = element_name.strip()
    if normalized.startswith("st."):
        normalized = normalized[3:]
    return normalized.lower().replace(" ", "_")


def _category_icon(title: str) -> str:
    return _safe_icon(CATEGORY_ICON_BY_TITLE.get(title), ":material/widgets:")


def _safe_icon(icon: str | None, fallback: str | None = None) -> str | None:
    if not icon:
        return fallback
    try:
        validate_icon_or_emoji(icon)
        return icon
    except StreamlitAPIException:
        return fallback


def _element_icon(element_name: str, title: str) -> str:
    normalized = _normalize_palette_element_name(element_name)
    widget_type = ELEMENT_TYPE_ALIASES.get(normalized, normalized)
    return _safe_icon(
        MATERIAL_ICON_BY_TYPE.get(widget_type)
        or ELEMENT_ICON_BY_NAME.get(normalized)
        or _category_icon(title),
        _category_icon(title),
    ) or ":material/widgets:"


def _resolve_palette_definition(definitions_by_type: dict[str, object], element_name: str):
    normalized = _normalize_palette_element_name(element_name)
    widget_type = ELEMENT_TYPE_ALIASES.get(normalized, normalized)
    definition = definitions_by_type.get(widget_type)
    if definition is None:
        definition = definitions_by_type.get(widget_type.lower())
    if definition is None:
        definition = definitions_by_type.get(normalized)
    return widget_type, definition


def _ensure_state() -> None:
    clear_registry()
    register_default_widgets()
    if "design" not in st.session_state:
        st.session_state["design"] = Design(name="Untitled")
    if "selected_id" not in st.session_state:
        st.session_state["selected_id"] = MAIN_CONTAINER_ID
    if "hierarchy_checked_id" not in st.session_state:
        st.session_state["hierarchy_checked_id"] = MAIN_CONTAINER_ID
    if "hierarchy_checked_prev" not in st.session_state:
        st.session_state["hierarchy_checked_prev"] = [MAIN_CONTAINER_ID]
    if "widget_counters" not in st.session_state:
        st.session_state["widget_counters"] = {}
    if "target_container_id" not in st.session_state:
        st.session_state["target_container_id"] = None
    if "target_column_id" not in st.session_state:
        st.session_state["target_column_id"] = None
    if "target_tab_id" not in st.session_state:
        st.session_state["target_tab_id"] = None
    if "ui1_hierarchy_collapsed" not in st.session_state:
        st.session_state["ui1_hierarchy_collapsed"] = False
    if "ui1_properties_collapsed" not in st.session_state:
        st.session_state["ui1_properties_collapsed"] = False
    if "ui2_preview_sidebar_collapsed" not in st.session_state:
        st.session_state["ui2_preview_sidebar_collapsed"] = False


def _new_widget_instance(
    widget_type: str,
    defaults: Dict[str, object],
    parent_id: str | None = None,
    column_index: int | None = None,
) -> WidgetInstance:
    widget_id = str(uuid.uuid4())
    props = dict(defaults)
    counters = st.session_state.setdefault("widget_counters", {})
    next_index = counters.get(widget_type, 0) + 1
    counters[widget_type] = next_index
    if "label" in props:
        base_label = str(props.get("label", widget_type)).strip()
        props["label"] = f"{base_label} {next_index}"
    return WidgetInstance(
        id=widget_id,
        type=widget_type,
        props=props,
        parent_id=parent_id,
        column_index=column_index,
    )


def _collect_descendant_ids(design: Design, root_id: str) -> set[str]:
    descendants: set[str] = set()
    queue: list[str] = [root_id]
    while queue:
        current_id = queue.pop(0)
        for widget in design.widgets:
            if widget.parent_id == current_id and widget.id not in descendants:
                descendants.add(widget.id)
                queue.append(widget.id)
    return descendants


def _move_widget(widgets: List[WidgetInstance], index: int, direction: int) -> None:
    new_index = index + direction
    if new_index < 0 or new_index >= len(widgets):
        return
    widgets[index], widgets[new_index] = widgets[new_index], widgets[index]

def _move_widget_block(design: Design, widget: WidgetInstance, direction: int) -> None:
    """Move a widget and all its descendants as a block up or down among siblings."""
    widgets = design.widgets
    parent_id = widget.parent_id

    # Collect siblings (widgets with the same parent, excluding descendants of widget)
    descendant_ids = _collect_descendant_ids(design, widget.id)

    # Build ordered list of sibling blocks at the same level
    # A "sibling block" is: the sibling widget + all its descendants, in list order
    def _block_indices(root_idx: int) -> list[int]:
        """Return all indices belonging to root and its descendants (in order)."""
        root = widgets[root_idx]
        desc_ids = _collect_descendant_ids(design, root.id)
        result = [root_idx]
        for i, w in enumerate(widgets):
            if w.id in desc_ids:
                result.append(i)
        return sorted(result)

    # Find all top-level indices for siblings (same parent_id, not a descendant of widget)
    sibling_roots: list[int] = [
        i for i, w in enumerate(widgets)
        if w.parent_id == parent_id and w.id != widget.id and w.id not in descendant_ids
    ]

    # Find the block of the selected widget
    widget_block = [i for i, w in enumerate(widgets)
                    if w.id == widget.id or w.id in descendant_ids]
    widget_block.sort()

    if not widget_block:
        return

    widget_start = widget_block[0]
    widget_end = widget_block[-1]

    if direction == -1:
        # Find the sibling root that comes just before our block
        prev_siblings = [i for i in sibling_roots if i < widget_start]
        if not prev_siblings:
            return
        swap_root_idx = max(prev_siblings)
        swap_block = _block_indices(swap_root_idx)
        swap_start = swap_block[0]
        swap_end = swap_block[-1]
        # Extract both blocks, swap their positions
        before = [w for i, w in enumerate(widgets) if i < swap_start]
        swap_blk = [widgets[i] for i in swap_block]
        between = [w for i, w in enumerate(widgets) if swap_end < i < widget_start]
        widget_blk = [widgets[i] for i in widget_block]
        after = [w for i, w in enumerate(widgets) if i > widget_end]
        design.widgets[:] = before + widget_blk + between + swap_blk + after
    else:
        # Find the sibling root that comes just after our block
        next_siblings = [i for i in sibling_roots if i > widget_end]
        if not next_siblings:
            return
        swap_root_idx = min(next_siblings)
        swap_block = _block_indices(swap_root_idx)
        swap_start = swap_block[0]
        swap_end = swap_block[-1]
        before = [w for i, w in enumerate(widgets) if i < widget_start]
        widget_blk = [widgets[i] for i in widget_block]
        between = [w for i, w in enumerate(widgets) if widget_end < i < swap_start]
        swap_blk = [widgets[i] for i in swap_block]
        after = [w for i, w in enumerate(widgets) if i > swap_end]
        design.widgets[:] = before + swap_blk + between + widget_blk + after


def _normalize_column_labels(count: int, labels: list) -> list[str]:
    if count < 1:
        count = 1
    cleaned = [str(label).strip() for label in labels if str(label).strip()]
    result = cleaned[:count]
    while len(result) < count:
        result.append(f"Column {len(result) + 1}")
    return result


def _move_column(container: WidgetInstance, design: Design, column_index: int, direction: int) -> bool:
    count = int(container.props.get("count", 2))
    if count < 1:
        count = 1
    new_index = column_index + direction
    if new_index < 0 or new_index >= count:
        return False
    labels = container.props.get("labels", [])
    if not isinstance(labels, list):
        labels = []
    normalized = _normalize_column_labels(count, labels)
    normalized[column_index], normalized[new_index] = normalized[new_index], normalized[column_index]
    container.props["labels"] = normalized
    for widget in design.widgets:
        if widget.parent_id != container.id:
            continue
        if widget.column_index == column_index:
            widget.column_index = new_index
        elif widget.column_index == new_index:
            widget.column_index = column_index
    return True


def _parse_column_ref(value: str) -> tuple[str, int] | None:
    if "::col::" not in value:
        return None
    container_id, raw_index = value.split("::col::", 1)
    try:
        return container_id, int(raw_index)
    except ValueError:
        return None


def _render_prop_input(widget: WidgetInstance, prop: PropDefinition) -> None:
    key = f"prop_{widget.id}_{prop.name}"
    value = widget.props.get(prop.name, prop.default)
    original = value

    if prop.name in {"custom_width", "custom_height"}:
        mode_name = "width" if prop.name == "custom_width" else "height"
        disabled = widget.props.get(mode_name, "stretch" if mode_name == "width" else "auto") != "custom"
        current_value = max(1, _safe_int(value, 1))
        widget.props[prop.name] = int(st.number_input(prop.label, value=current_value, step=1, min_value=1, key=key, disabled=disabled))
    elif prop.name == "custom_sort" and widget.type == "bar_chart":
        disabled = str(widget.props.get("sort", "true")).strip().lower() != "custom"
        widget.props[prop.name] = st.text_input(prop.label, value=str(value), key=key, disabled=disabled)
    elif prop.name == "custom_expanded" and widget.type == "json":
        disabled = widget.props.get("expanded", "true") != "custom"
        current_value = max(0, _safe_int(value, 0))
        widget.props[prop.name] = int(st.number_input(prop.label, value=current_value, step=1, min_value=0, key=key, disabled=disabled))
    elif prop.input_type == "text":
        widget.props[prop.name] = st.text_input(prop.label, value=str(value), key=key)
    elif prop.input_type == "multiline":
        widget.props[prop.name] = st.text_area(prop.label, value=str(value), key=key)
    elif prop.input_type == "bool":
        widget.props[prop.name] = st.checkbox(prop.label, value=bool(value), key=key)
    elif prop.input_type == "bool_select":
        selected = st.selectbox(
            prop.label,
            ["False", "True"],
            index=1 if bool(value) else 0,
            key=key,
        )
        widget.props[prop.name] = selected == "True"
    elif prop.input_type == "number":
        widget.props[prop.name] = st.number_input(prop.label, value=float(value), key=key)
    elif prop.input_type == "int":
        widget.props[prop.name] = int(st.number_input(prop.label, value=int(value), step=1, key=key))
    elif prop.input_type == "options":
        text_value = ", ".join(value) if isinstance(value, list) else str(value)
        raw = st.text_input(prop.label, value=text_value, key=key)
        widget.props[prop.name] = [item.strip() for item in raw.split(",") if item.strip()]
    elif prop.input_type == "select":
        options = prop.options or []
        selected = value if value in options else (options[0] if options else "")
        widget.props[prop.name] = st.selectbox(
            prop.label,
            options,
            index=options.index(selected) if selected in options else 0,
            key=key,
        )
    elif prop.input_type == "date":
        text_value = st.text_input(prop.label, value=str(value), key=key)
        widget.props[prop.name] = text_value
        if text_value:
            try:
                date.fromisoformat(text_value)
            except ValueError:
                st.warning("Invalid date format. Use YYYY-MM-DD.")
    elif prop.input_type == "color":
        color_value = str(value).strip()
        if not color_value:
            fallback = str(prop.default).strip() if prop.default is not None else ""
            color_value = fallback or "#000000"
        widget.props[prop.name] = st.color_picker(prop.label, value=color_value, key=key)
    else:
        widget.props[prop.name] = st.text_input(prop.label, value=str(value), key=key)

    if widget.props.get(prop.name) != original:
        st.rerun()


def _get_columns_containers(design: Design) -> list[WidgetInstance]:
    return [widget for widget in design.widgets if widget.type == "columns_container"]


def _get_all_containers(design: Design) -> list[WidgetInstance]:
    """Return all widgets that can hold children (columns_container, container, empty, expander)."""
    return [widget for widget in design.widgets if widget.type in {"columns_container", "container", "empty", "expander", "form", "popover", "sidebar", "spinner", "status", "tabs"}]


def _is_columns_container(widget: WidgetInstance) -> bool:
    return widget.type == "columns_container"


def _is_tabs_container(widget: WidgetInstance) -> bool:
    return widget.type == "tabs"


def _normalize_tab_labels_ui(count: int, labels: list) -> list[str]:
    if count < 1:
        count = 1
    cleaned = [str(label).strip() for label in labels if str(label).strip()]
    result = cleaned[:count]
    while len(result) < count:
        result.append(f"Tab {len(result) + 1}")
    return result


def _sync_tabs_children(design: Design, container: WidgetInstance) -> tuple[list[WidgetInstance], bool]:
    desired = int(container.props.get("tabs", 2))
    desired = max(1, desired)
    tabs = [
        widget
        for widget in design.widgets
        if widget.parent_id == container.id and widget.type == "tab"
    ]
    changed = False

    if len(tabs) < desired:
        changed = True
        for i in range(len(tabs), desired):
            new_tab = _new_widget_instance("tab", {"label": f"Tab {i + 1}"}, parent_id=container.id)
            try:
                insert_at = max(
                    (idx for idx, widget in enumerate(design.widgets) if widget.parent_id == container.id and widget.type == "tab"),
                    default=design.widgets.index(container),
                )
            except ValueError:
                insert_at = len(design.widgets) - 1
            design.widgets.insert(insert_at + 1, new_tab)
            tabs.append(new_tab)
    elif len(tabs) > desired:
        changed = True
        for tab in tabs[desired:]:
            _remove_widget_with_children(design, tab.id)
        tabs = tabs[:desired]

    # Normalize labels
    for i, tab in enumerate(tabs):
        label = str(tab.props.get("label", "")).strip()
        if not label:
            tab.props["label"] = f"Tab {i + 1}"
            changed = True

    # Validate default prop
    tab_labels = [str(t.props.get("label", "")).strip() for t in tabs]
    default = str(container.props.get("default", "")).strip()
    if default and default not in tab_labels:
        container.props["default"] = ""
        changed = True

    return tabs, changed


def _sync_columns_children(design: Design, container: WidgetInstance) -> tuple[list[WidgetInstance], bool]:
    desired = int(container.props.get("columns", 0))
    desired = max(0, desired)
    columns = [
        widget
        for widget in design.widgets
        if widget.parent_id == container.id and widget.type == "column"
    ]
    changed = False

    if desired == 0:
        if columns:
            changed = True
        for column in columns:
            _remove_widget_with_children(design, column.id)
        return [], changed

    if len(columns) < desired:
        changed = True
        for _ in range(desired - len(columns)):
            new_column = _new_widget_instance("column", {"label": "Column"}, parent_id=container.id)
            insert_at = max(
                (idx for idx, widget in enumerate(design.widgets) if widget.parent_id == container.id and widget.type == "column"),
                default=design.widgets.index(container),
            )
            design.widgets.insert(insert_at + 1, new_column)
            columns.append(new_column)
    elif len(columns) > desired:
        changed = True
        for column in columns[desired:]:
            _remove_widget_with_children(design, column.id)
        columns = columns[:desired]

    return columns, changed


def _add_palette_widget(design: Design, definition) -> None:
    target_container_id = st.session_state.get("target_container_id")
    target_column_id = st.session_state.get("target_column_id")
    target_tab_id = st.session_state.get("target_tab_id")
    parent_id = None
    if target_container_id:
        container = next((w for w in design.widgets if w.id == target_container_id), None)
        if container:
            if _is_columns_container(container):
                columns, _ = _sync_columns_children(design, container)
                parent_id = target_column_id or (columns[0].id if columns else None)
            elif _is_tabs_container(container):
                tabs, _ = _sync_tabs_children(design, container)
                parent_id = target_tab_id or (tabs[0].id if tabs else None)
            else:
                # container / empty: child goes directly into the container
                parent_id = container.id
    instance = _new_widget_instance(
        definition.type,
        definition.defaults,
        parent_id=parent_id,
    )
    design.widgets.append(instance)
    # Auto-create tab children when a tabs widget is added
    if instance.type == "tabs":
        _sync_tabs_children(design, instance)
    st.session_state["selected_id"] = instance.id
    st.rerun()


def _render_palette(design: Design) -> None:
    definitions_by_type = {
        definition.type.lower(): definition
        for definition in list_widgets()
        if definition.type not in {"column", "tab"}
    }
    palette_groups = _load_palette_groups()
    popover_columns = st.columns(len(palette_groups)) if palette_groups else []

    for column, (title, element_names) in zip(popover_columns, palette_groups):
        with column:
            with st.popover(
                title,
                icon=_category_icon(title),
                use_container_width=True,
                width="stretch",
            ):
                for element_name in element_names:
                    normalized = _normalize_palette_element_name(element_name)
                    widget_type, definition = _resolve_palette_definition(definitions_by_type, element_name)
                    is_supported = definition is not None
                    help_text = None
                    if not is_supported:
                        help_text = "Planned element: not implemented in the current widget registry yet."
                    elif widget_type != normalized:
                        help_text = f"Adds the implemented '{definition.label}' widget."
                    if st.button(
                        element_name,
                        key=f"ui2_add_{title}_{normalized}",
                        icon=_element_icon(element_name, title),
                        use_container_width=True,
                        disabled=not is_supported,
                        help=help_text,
                    ):
                        _add_palette_widget(design, definition)


def _render_properties(design: Design) -> None:
    st.subheader("Container")
    selected_id = st.session_state.get("selected_id")
    selected = next((w for w in design.widgets if w.id == selected_id), None)
    containers = _get_all_containers(design)
    container_ids = [widget.id for widget in containers]
    widget_by_id = {widget.id: widget for widget in design.widgets}

    def _container_label(cid: str) -> str:
        parts: list[str] = []
        current = widget_by_id.get(cid)
        while current is not None:
            label = str(current.props.get("label", current.type.capitalize())).strip() or current.type.capitalize()
            parts.append(label)
            if not current.parent_id:
                break
            current = widget_by_id.get(current.parent_id)
        return " / ".join(reversed(parts))

    container_options = [MAIN_CONTAINER_ID] + container_ids
    current_container = st.session_state.get("add_to_container")
    derived_from_hierarchy = False
    if current_container is None:
        derived_from_hierarchy = True
        hierarchy_id = st.session_state.get("hierarchy_checked_id")
        if hierarchy_id == MAIN_CONTAINER_ID:
            current_container = MAIN_CONTAINER_ID
        else:
            selected_node = next((w for w in design.widgets if w.id == hierarchy_id), None)
            if selected_node:
                if selected_node.type in {"columns_container", "container", "empty", "expander", "form", "popover", "sidebar", "spinner", "status", "tabs"}:
                    current_container = selected_node.id
                elif selected_node.type == "column":
                    current_container = selected_node.parent_id or MAIN_CONTAINER_ID
                elif selected_node.type == "tab":
                    current_container = selected_node.parent_id or MAIN_CONTAINER_ID
                elif selected_node.parent_id:
                    parent_node = next((w for w in design.widgets if w.id == selected_node.parent_id), None)
                    if parent_node and parent_node.type == "column":
                        current_container = parent_node.parent_id or MAIN_CONTAINER_ID
                    elif parent_node and parent_node.type == "tab":
                        # child of a tab → parent is the tabs widget
                        current_container = parent_node.parent_id or MAIN_CONTAINER_ID
                    elif parent_node and parent_node.type in {"columns_container", "container", "empty", "expander", "form", "popover", "sidebar", "spinner", "tabs"}:
                        current_container = parent_node.id
            if current_container is None:
                current_container = MAIN_CONTAINER_ID
    if current_container not in container_options:
        current_container = MAIN_CONTAINER_ID
        st.session_state["add_to_container"] = MAIN_CONTAINER_ID

    selected_container_raw = st.selectbox(
        "Add to container",
        options=container_options,
        index=container_options.index(current_container),
        format_func=lambda cid: "Main" if cid == MAIN_CONTAINER_ID else f"{_container_label(cid)} ({cid[:8]})",
        key="add_to_container",
    )

    suppress_sync = st.session_state.pop("suppress_container_pane_sync", False)
    previous_selection = st.session_state.get("container_pane_prev")
    if (
        not suppress_sync
        and not derived_from_hierarchy
        and previous_selection is not None
        and selected_container_raw != previous_selection
    ):
        target_tree_id = selected_container_raw
        if st.session_state.get("hierarchy_checked_id") != target_tree_id:
            st.session_state["hierarchy_checked_id"] = target_tree_id
            st.session_state["hierarchy_checked_prev"] = [target_tree_id]
            st.session_state["hierarchy_tree_version"] = st.session_state.get("hierarchy_tree_version", 0) + 1
            st.rerun()
    st.session_state["container_pane_prev"] = selected_container_raw

    selected_container_id = None if selected_container_raw == MAIN_CONTAINER_ID else selected_container_raw

    st.session_state["target_container_id"] = selected_container_id
    if selected_container_id is None:
        st.session_state["target_column_id"] = None
    else:
        container_widget = next((w for w in containers if w.id == selected_container_id), None)
        if container_widget and _is_columns_container(container_widget):
            columns, changed = _sync_columns_children(design, container_widget)
            if changed:
                st.rerun()
            column_ids = [column.id for column in columns]
            current_column = st.session_state.get("target_column_id")
            show_target_column = not (selected and selected.type in {"column", "columns_container"})
            if show_target_column:
                if column_ids:
                    if current_column not in column_ids:
                        st.session_state["target_column_id"] = column_ids[0]
                    st.selectbox(
                        "Target column",
                        column_ids,
                        format_func=lambda cid: next(
                            (col.props.get("label", "Column") for col in columns if col.id == cid),
                            "Column",
                        ),
                        key="target_column_id",
                    )
                else:
                    st.session_state["target_column_id"] = None
            elif current_column not in column_ids:
                st.session_state["target_column_id"] = None
            st.session_state["target_tab_id"] = None
        elif container_widget and _is_tabs_container(container_widget):
            tabs, changed = _sync_tabs_children(design, container_widget)
            if changed:
                st.rerun()
            tab_ids = [tab.id for tab in tabs]
            current_tab = st.session_state.get("target_tab_id")
            show_target_tab = not (selected and selected.type in {"tab", "tabs"})
            if show_target_tab:
                if tab_ids:
                    if current_tab not in tab_ids:
                        st.session_state["target_tab_id"] = tab_ids[0]
                    st.selectbox(
                        "Target tab",
                        tab_ids,
                        format_func=lambda cid: next(
                            (t.props.get("label", "Tab") for t in tabs if t.id == cid),
                            "Tab",
                        ),
                        key="target_tab_id",
                    )
                else:
                    st.session_state["target_tab_id"] = None
            elif current_tab not in tab_ids:
                st.session_state["target_tab_id"] = None
            st.session_state["target_column_id"] = None
        else:
            # container / empty / sidebar / etc: direct child, no sub-selection
            st.session_state["target_column_id"] = None
            st.session_state["target_tab_id"] = None

    st.subheader("Properties")

    if selected_id == MAIN_CONTAINER_ID:
        screen_width = st.selectbox(
            "Screen width",
            ["regular", "wide"],
            index=0 if design.screen_width == "regular" else 1,
            key="main_screen_width",
        )
        background_color = st.color_picker(
            "Background color",
            value=design.background_color or "#FFFFFF",
            key="main_background_color",
        )
        background_image = st.text_input(
            "Background image (URL)",
            value=design.background_image,
            key="main_background_image",
            help="Paste an HTTP/HTTPS URL for the background image.",
        )
        changed = (
            screen_width != design.screen_width
            or background_color != design.background_color
            or background_image != design.background_image
        )
        design.screen_width = screen_width
        design.background_color = background_color
        design.background_image = background_image
        if changed:
            st.rerun()
        return

    if not selected:
        st.info("Select a widget to edit its properties.")
        return

    definition = next((w for w in list_widgets() if w.type == selected.type), None)
    if not definition:
        st.warning("Unknown widget type.")
        return

    for prop in definition.props_schema:
        if prop.name not in selected.props:
            selected.props[prop.name] = prop.default
        _render_prop_input(selected, prop)


def _render_generated_code(design: Design) -> None:
    st.subheader("Generated Code")
    code = generate_streamlit_code(design)
    st.code(code, language="python")
    st.download_button(
        "Download app.py",
        data=code,
        file_name="app.py",
        mime="text/x-python",
    )


def _apply_imported_design(imported: Design) -> None:
    """Commit an imported design into session state and reset selection safely."""
    st.session_state["design"] = imported
    # Reset selection to Main (per design-tab guidelines) and clear targets.
    st.session_state["selected_id"] = MAIN_CONTAINER_ID
    st.session_state["hierarchy_checked_id"] = MAIN_CONTAINER_ID
    st.session_state["hierarchy_checked_prev"] = [MAIN_CONTAINER_ID]
    st.session_state["target_container_id"] = None
    st.session_state["target_column_id"] = None
    st.session_state["target_tab_id"] = None
    st.session_state["widget_counters"] = {}
    st.session_state.pop("pending_import", None)


def _render_code_import() -> None:
    with st.expander("Load from code", expanded=False):
        st.caption(
            "Upload a previously generated app.py to rebuild the design in the "
            "Preview. The file is parsed only - it is never executed."
        )
        uploaded = st.file_uploader("Upload app.py", type=["py"], key="code_import_uploader")
        if uploaded is not None:
            raw = uploaded.getvalue()
            try:
                source = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                st.error("Could not decode file - expected UTF-8 encoded Python source.")
                return

            result = import_design_from_code(source)

            for diag in result.errors:
                location = f" (line {diag.lineno})" if diag.lineno else ""
                st.error(f"{diag.message}{location}")
            for diag in result.warnings:
                location = f" (line {diag.lineno})" if diag.lineno else ""
                st.warning(f"{diag.message}{location}")

            if not result.ok or result.design is None:
                st.info("Current design was left unchanged.")
                return

            widget_count = result.widget_count
            warning_count = len(result.warnings)
            ignored = result.ignored
            summary = f"Reconstructed {widget_count} element(s) from the uploaded file."
            if warning_count:
                summary += f" {warning_count} item(s) could not be imported (see warnings above)."
            st.success(summary)

            if ignored:
                st.info(f"Ignored {len(ignored)} non-Streamlit statement(s).")
                with st.expander(f"Show {len(ignored)} ignored statement(s)", expanded=False):
                    for diag in ignored:
                        location = f"line {diag.lineno}: " if diag.lineno else ""
                        detail = f" ({diag.node_summary})" if diag.node_summary else ""
                        st.write(f"- {location}{diag.message}{detail}")

            st.warning("Replacing will discard your current design.")
            if st.button("Replace current design", key="code_import_confirm"):
                _apply_imported_design(result.design)
                st.rerun()



def _render_preview(design: Design) -> None:
    reset_preview_keys()
    st.markdown(
        f"""
        <style>
        /* Shared split region below the "Preview" subheader */
        .st-key-ui2_preview_split_region,
        .st-key-ui2_preview_split_region > div {{
            height: {SCROLLABLE_PANE_HEIGHT}px;
            overflow: hidden;
        }}

        .st-key-ui2_preview_split_region [data-testid="stHorizontalBlock"] {{
            align-items: stretch;
            height: 100%;
        }}

        .st-key-ui2_preview_split_region [data-testid="column"] > div {{
            height: 100%;
            overflow: hidden;
        }}

        /* Sidebar panel: same height as the preview pane (SCROLLABLE_PANE_HEIGHT) */
        /* height is enforced via st.container(height=) in Python; CSS handles only visuals */
        .st-key-ui2_preview_sidebar_shell {{
            background: var(--secondary-background-color, #F0F2F6);
            border-top: 1px solid rgba(49, 51, 63, 0.2);
            border-left: 1px solid rgba(49, 51, 63, 0.2);
            border-bottom: 1px solid rgba(49, 51, 63, 0.2);
            border-right: 2px solid rgba(49, 51, 63, 0.25);
            border-radius: 0.4rem 0 0 0.4rem;
            padding: 0.5rem 0.65rem 0.75rem 0.65rem;
            height: 100%;
            overflow-y: auto;
            overflow-x: hidden;
            overscroll-behavior: contain;
        }}

        .st-key-ui2_preview_sidebar_collapsed {{
            background: var(--secondary-background-color, #F0F2F6);
            border-top: 1px solid rgba(49, 51, 63, 0.2);
            border-left: 1px solid rgba(49, 51, 63, 0.2);
            border-bottom: 1px solid rgba(49, 51, 63, 0.2);
            border-right: 2px solid rgba(49, 51, 63, 0.25);
            border-radius: 0.4rem 0 0 0.4rem;
            padding: 0.5rem 0.35rem;
            height: 100%;
            overflow: hidden;
        }}

        .st-key-ui2_preview_sidebar_main {{
            height: 100%;
            overflow-y: auto;
            overflow-x: hidden;
            overscroll-behavior: contain;
        }}

        .st-key-ui2_preview_sidebar_shell [data-testid="stButton"] button,
        .st-key-ui2_preview_sidebar_collapsed [data-testid="stButton"] button {{
            min-width: 2.2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    preview_background_image = css_url_value(design.background_image)
    if design.background_color or preview_background_image:
        css_parts = [".st-key-ui1_preview_pane { "]
        if design.background_color:
            css_parts.append(f"background-color: {design.background_color}; ")
        if preview_background_image:
            css_parts.append(f'background-image: url("{preview_background_image}"); ')
            css_parts.append("background-size: cover; background-position: center; background-repeat: no-repeat; ")
        css_parts.append("padding: 0.75rem; ")
        css_parts.append("}")
        st.markdown(f"<style>{''.join(css_parts)}</style>", unsafe_allow_html=True)

    if not design.widgets:
        st.info("Add widgets to see the preview.")
        return

    children: dict[str, list[WidgetInstance]] = {}
    for widget in design.widgets:
        if widget.parent_id:
            children.setdefault(widget.parent_id, []).append(widget)

    def _render_widget(widget: WidgetInstance) -> None:
        definition = next((w for w in list_widgets() if w.type == widget.type), None)
        if not definition:
            st.warning(f"Unknown widget type: {widget.type}")
            return
        if widget.type == "columns_container":
            columns = [child for child in children.get(widget.id, []) if child.type == "column"]
            desired = int(widget.props.get("columns", len(columns) or 0))
            desired = max(0, desired)
            if desired == 0:
                return
            if not columns:
                columns = [WidgetInstance(id="", type="column") for _ in range(desired)]
            ratios = [max(1, _safe_int(col.props.get("ratio", 1), 1)) for col in columns]
            background_color = str(widget.props.get("background_color", "")).strip()

            if background_color:
                anchor = f"cols-{widget.id}"
                st.markdown(f"<div id=\"{anchor}\"></div>", unsafe_allow_html=True)
                css = [
                    f"#{anchor} + div [data-testid=\\\"column\\\"] "
                    f"{{ background-color: {background_color}; padding: 0.5rem; border-radius: 0.25rem; }}"
                ]
                for idx, col in enumerate(columns, start=1):
                    col_bg = str(col.props.get("background_color", "")).strip()
                    if col_bg:
                        css.append(
                            f"#{anchor} + div [data-testid=\\\"column\\\"]:nth-of-type({idx}) "
                            f"{{ background-color: {col_bg}; }}"
                        )
                st.markdown(f"<style>{''.join(css)}</style>", unsafe_allow_html=True)

            cols = st.columns(ratios)
            for idx, col in enumerate(columns):
                with cols[idx]:
                    for child in children.get(col.id, []):
                        _render_widget(child)
            return
        if widget.type == "container":
            nested = children.get(widget.id, [])
            label = str(widget.props.get("label", "Container")).strip() or "Container"
            # Build st.container kwargs from actual props
            _ckw: dict = {}
            _border_raw = str(widget.props.get("border", "None"))
            if _border_raw == "True":
                _ckw["border"] = True
            elif _border_raw == "False":
                _ckw["border"] = False
            _width_mode = widget.props.get("width", "stretch")
            if _width_mode == "custom":
                try:
                    _ckw["width"] = max(1, int(widget.props.get("custom_width", 300)))
                except (TypeError, ValueError):
                    _ckw["width"] = 300
            else:
                _ckw["width"] = _width_mode
            _height_mode = widget.props.get("height", "content")
            if _height_mode == "custom":
                try:
                    _ckw["height"] = max(1, int(widget.props.get("custom_height", 300)))
                except (TypeError, ValueError):
                    _ckw["height"] = 300
            else:
                _ckw["height"] = _height_mode
            if bool(widget.props.get("horizontal", False)):
                _ckw["horizontal"] = True
            _h_align = widget.props.get("horizontal_alignment", "left")
            if _h_align != "left":
                _ckw["horizontal_alignment"] = _h_align
            _v_align = widget.props.get("vertical_alignment", "top")
            if _v_align != "top":
                _ckw["vertical_alignment"] = _v_align
            _gap = widget.props.get("gap", "small")
            if _gap != "small":
                _ckw["gap"] = None if _gap == "None" else _gap
            _bg = str(widget.props.get("background_color", "#FFFFFF")).strip()
            _ckw["key"] = f"preview_container_{widget.id}"
            with st.container(**_ckw):
                st.caption(f"st.container ��� {label}")
                if _bg and _bg != "#FFFFFF":
                    st.markdown(
                        f"<style>.st-key-preview_container_{widget.id} "
                        f"{{ background-color: {_bg}; padding: 0.5rem; border-radius: 0.25rem; }}</style>",
                        unsafe_allow_html=True,
                    )
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown(
                        "<span style='font-size:11px;color:#aaa;'>Add child widgets here</span>",
                        unsafe_allow_html=True,
                    )
            return
        if widget.type == "column":
            return
        if widget.type == "empty":
            nested = children.get(widget.id, [])
            label = str(widget.props.get("label", "Empty")).strip() or "Empty"
            # st.empty() only holds one element; use a bordered container in preview
            # to show all children, with a header indicating this is an Empty widget.
            with st.container(border=True, key=f"preview_empty_{widget.id}"):
                st.caption(f"st.empty — {label}")
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown(
                        "<span style='font-size:11px;color:#aaa;'>"
                        "# Add elements here; each will replace the previous one"
                        "</span>",
                        unsafe_allow_html=True,
                    )
            return
        if widget.type == "expander":
            nested = children.get(widget.id, [])
            label = str(widget.props.get("label", "Expander")).strip() or "Expander"
            icon_raw = str(widget.props.get("icon", "")).strip() or None
            with st.expander(label, expanded=True, icon=icon_raw):
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown("<span style='color:grey;font-size:0.85em'>Add child widgets here</span>", unsafe_allow_html=True)
            return
        if widget.type == "form":
            nested = children.get(widget.id, [])
            label = str(widget.props.get("label", "Form")).strip() or "Form"
            with st.container(border=True, key=f"preview_form_{widget.id}"):
                st.caption(f"st.form — {label}")
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown("<span style='color:grey;font-size:0.85em'>Add child widgets here</span>", unsafe_allow_html=True)
                st.button("Submit", key=f"preview_form_submit_{widget.id}", disabled=True)
            return
        if widget.type == "popover":
            nested = children.get(widget.id, [])
            label = str(widget.props.get("label", "Popover")).strip() or "Popover"
            btn_type = widget.props.get("type", "secondary")
            icon_raw = str(widget.props.get("icon", "")).strip() or None
            disabled = widget.props.get("disabled", False)
            width_mode = widget.props.get("width", "content")
            if width_mode == "custom":
                width_val = max(1, int(widget.props.get("custom_width", 300)))
            else:
                width_val = width_mode
            with st.popover(label, type=btn_type, icon=icon_raw, disabled=disabled, width=width_val):
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown("<span style='color:grey;font-size:0.85em'>Add child widgets here</span>", unsafe_allow_html=True)
            return
        if widget.type == "status":
            nested = children.get(widget.id, [])
            label = str(widget.props.get("label", "Status")).strip() or "Status"
            expanded = widget.props.get("expanded", False)
            state = widget.props.get("state", "running")
            with st.status(label, expanded=expanded, state=state):
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown("<span style='color:grey;font-size:0.85em'>Add child widgets here</span>", unsafe_allow_html=True)
            return
        if widget.type == "spinner":
            nested = children.get(widget.id, [])
            text = str(widget.props.get("text", "In progress...")).strip() or "In progress..."
            with st.container(border=True, key=f"preview_spinner_{widget.id}"):
                st.caption(f"st.spinner — {text}")
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown("<span style='color:grey;font-size:0.85em'>Add child widgets here</span>", unsafe_allow_html=True)
            return
        if widget.type == "sidebar":
            nested = children.get(widget.id, [])
            label = str(widget.props.get("label", "Sidebar")).strip() or "Sidebar"
            with st.container(border=True, key=f"preview_sidebar_{widget.id}"):
                st.caption(f"st.sidebar — {label}")
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown("<span style='color:grey;font-size:0.85em'>Add child widgets here</span>", unsafe_allow_html=True)
            return
        if widget.type == "tabs":
            tab_widgets = [child for child in children.get(widget.id, []) if child.type == "tab"]
            desired = max(1, int(widget.props.get("tabs", len(tab_widgets) or 2)))
            tab_labels_raw = [str(t.props.get("label", "")).strip() for t in tab_widgets]
            while len(tab_labels_raw) < desired:
                tab_labels_raw.append(f"Tab {len(tab_labels_raw) + 1}")
            tab_labels = tab_labels_raw[:desired]
            width_mode = widget.props.get("width", "stretch")
            if width_mode == "custom":
                try:
                    width_val: str | int = max(1, int(widget.props.get("custom_width", 320)))
                except (TypeError, ValueError):
                    width_val = "stretch"
            else:
                width_val = "stretch"
            default_raw = str(widget.props.get("default", "")).strip()
            default_val = default_raw if default_raw in tab_labels else None
            label = str(widget.props.get("label", "Tabs")).strip() or "Tabs"
            st.caption(f"st.tabs — {label}")
            try:
                rendered_tabs = st.tabs(tab_labels, width=width_val, default=default_val)
            except Exception:
                rendered_tabs = st.tabs(tab_labels)
            for i, tab_ctx in enumerate(rendered_tabs):
                with tab_ctx:
                    if i < len(tab_widgets):
                        tab_children = children.get(tab_widgets[i].id, [])
                        if tab_children:
                            for child in tab_children:
                                _render_widget(child)
                        else:
                            st.markdown("<span style='color:grey'>Add child widgets here</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color:grey'>Add child widgets here</span>", unsafe_allow_html=True)
            return
        if widget.type == "tab":
            return
        definition.render(widget)

    root_widgets = [widget for widget in design.widgets if not widget.parent_id]
    sidebar_widgets = [widget for widget in root_widgets if widget.type == "sidebar"]
    main_widgets = [widget for widget in root_widgets if widget.type != "sidebar"]

    def _render_sidebar_preview() -> None:
        collapsed = bool(st.session_state.get("ui2_preview_sidebar_collapsed", False))
        container_key = "ui2_preview_sidebar_collapsed" if collapsed else "ui2_preview_sidebar_shell"
        with st.container(height=SCROLLABLE_PANE_HEIGHT, key=container_key):
            header_cols = st.columns([6, 1], vertical_alignment="top")
            with header_cols[1]:
                toggle_label = "▶" if collapsed else "◀"
                toggle_help = "Expand sidebar preview" if collapsed else "Collapse sidebar preview"
                if st.button(toggle_label, key="ui2_preview_sidebar_toggle", help=toggle_help, use_container_width=True):
                    st.session_state["ui2_preview_sidebar_collapsed"] = not collapsed
                    st.rerun()
            if collapsed:
                return
            for index, widget in enumerate(sidebar_widgets):
                nested = children.get(widget.id, [])
                label = str(widget.props.get("label", "Sidebar")).strip() or "Sidebar"
                st.caption(f"st.sidebar — {label}")
                if nested:
                    for child in nested:
                        _render_widget(child)
                else:
                    st.markdown("<span style='color:grey;font-size:0.85em'>Add child widgets here</span>", unsafe_allow_html=True)
                if index < len(sidebar_widgets) - 1:
                    st.divider()

    def _render_main_preview() -> None:
        with st.container(height=SCROLLABLE_PANE_HEIGHT, key="ui2_preview_sidebar_main"):
            if main_widgets:
                for widget in main_widgets:
                    _render_widget(widget)
            elif sidebar_widgets:
                st.markdown(
                    "<span style='font-size:11px;color:#aaa;'>No main-page widgets to preview</span>",
                    unsafe_allow_html=True,
                )

    if sidebar_widgets:
        collapsed = bool(st.session_state.get("ui2_preview_sidebar_collapsed", False))
        column_ratio = PREVIEW_SIDEBAR_COLLAPSED_RATIO if collapsed else PREVIEW_SIDEBAR_EXPANDED_RATIO
        with st.container(key="ui2_preview_split_region"):
            sidebar_col, main_col = st.columns(column_ratio, gap="small")
            with sidebar_col:
                _render_sidebar_preview()
            with main_col:
                _render_main_preview()
        return

    for widget in root_widgets:
        _render_widget(widget)


def _render_hierarchy(design: Design) -> None:
    children: dict[str, list[WidgetInstance]] = {}
    for widget in design.widgets:
        if widget.parent_id:
            children.setdefault(widget.parent_id, []).append(widget)

    def _label_for(widget: WidgetInstance) -> str:
        definition = next((w for w in list_widgets() if w.type == widget.type), None)
        display_value = (
            widget.props.get("label")
            or widget.props.get("text")
            or (definition.label if definition else widget.type)
        )
        return f"{definition.label if definition else widget.type}: {display_value}"

    def _build_node(widget: WidgetInstance) -> dict:
        node = {"label": _label_for(widget), "value": widget.id}
        if widget.id in children:
            node["children"] = [_build_node(child) for child in children.get(widget.id, [])]
        return node

    tree_nodes = [{
        "label": "Main",
        "value": MAIN_CONTAINER_ID,
        "children": [_build_node(widget) for widget in design.widgets if not widget.parent_id],
    }]

    def _collect_values(nodes: list[dict]) -> list[str]:
        values: list[str] = []
        for node in nodes:
            value = node.get("value")
            if value:
                values.append(value)
            children_nodes = node.get("children") or []
            if children_nodes:
                values.extend(_collect_values(children_nodes))
        return values

    if "hierarchy_checked_id" not in st.session_state:
        st.session_state["hierarchy_checked_id"] = None
    if "hierarchy_checked_prev" not in st.session_state:
        st.session_state["hierarchy_checked_prev"] = []
    if "hierarchy_tree_version" not in st.session_state:
        st.session_state["hierarchy_tree_version"] = 0
    if "selected_column_ref" not in st.session_state:
        st.session_state["selected_column_ref"] = None

    checked_id = st.session_state.get("hierarchy_checked_id")
    checked = [checked_id] if checked_id else None
    tree_key = f"hierarchy_tree_{st.session_state['hierarchy_tree_version']}"
    expanded = _collect_values(tree_nodes)
    selection = tree_select(
        tree_nodes,
        no_cascade=True,
        check_model="single",
        checked=checked,
        only_leaf_checkboxes=False,
        expanded=expanded,
        key=tree_key,
    )
    selected_ids = []
    if isinstance(selection, dict):
        selected_ids = selection.get("checked") or selection.get("selected") or []
    if not selected_ids:
        fallback_id = st.session_state.get("hierarchy_checked_id")
        if fallback_id:
            selected_ids = [fallback_id]

    prev_checked = st.session_state.get("hierarchy_checked_prev") or []
    if selected_ids:
        st.session_state["hierarchy_restore_pending"] = False
        force_rerun = False
        if len(selected_ids) > 1:
            newest = next((item for item in selected_ids if item not in prev_checked), None)
            if newest is None:
                newest = selected_ids[-1]
            selected_ids = [newest]
            st.session_state["hierarchy_tree_version"] += 1
            force_rerun = True
        selected_id = selected_ids[0]
        selected_widget = next((w for w in design.widgets if w.id == selected_id), None)
        changed = False
        if st.session_state.get("selected_id") != selected_id:
            st.session_state["selected_id"] = selected_id
            changed = True
        if st.session_state.get("hierarchy_checked_id") != selected_id:
            st.session_state["hierarchy_checked_id"] = selected_id
            changed = True
        if selected_id == MAIN_CONTAINER_ID:
            if st.session_state.get("target_container_id") is not None:
                st.session_state["target_container_id"] = None
                st.session_state["add_to_container"] = MAIN_CONTAINER_ID
                st.session_state["target_column_id"] = None
                st.session_state["target_tab_id"] = None
                st.session_state["suppress_container_pane_sync"] = True
                changed = True
        elif selected_widget and selected_widget.type == "column":
            parent = next((w for w in design.widgets if w.id == selected_widget.parent_id), None)
            if parent and parent.type == "columns_container":
                sibling_count = sum(1 for w in design.widgets if w.parent_id == parent.id and w.type == "column")
                current_count = int(parent.props.get("columns", 0))
                if sibling_count > current_count:
                    parent.props["columns"] = sibling_count
                    changed = True
            if st.session_state.get("target_container_id") != selected_widget.parent_id:
                st.session_state["target_container_id"] = selected_widget.parent_id
                st.session_state["add_to_container"] = selected_widget.parent_id
                st.session_state["suppress_container_pane_sync"] = True
                changed = True
            if st.session_state.get("target_column_id") != selected_widget.id:
                st.session_state["target_column_id"] = selected_widget.id
                changed = True
            if st.session_state.get("target_tab_id") is not None:
                st.session_state["target_tab_id"] = None
                changed = True
        elif selected_widget and selected_widget.type == "columns_container":
            if st.session_state.get("target_container_id") != selected_widget.id:
                st.session_state["target_container_id"] = selected_widget.id
                st.session_state["add_to_container"] = selected_widget.id
                st.session_state["suppress_container_pane_sync"] = True
                changed = True
            if st.session_state.get("target_column_id") is not None:
                st.session_state["target_column_id"] = None
                changed = True
            if st.session_state.get("target_tab_id") is not None:
                st.session_state["target_tab_id"] = None
                changed = True
        elif selected_widget and selected_widget.type == "tab":
            # Selecting a tab row: set container to parent tabs widget, target tab to this tab
            tabs_widget = next((w for w in design.widgets if w.id == selected_widget.parent_id), None)
            if tabs_widget:
                if st.session_state.get("target_container_id") != tabs_widget.id:
                    st.session_state["target_container_id"] = tabs_widget.id
                    st.session_state["add_to_container"] = tabs_widget.id
                    st.session_state["suppress_container_pane_sync"] = True
                    changed = True
                if st.session_state.get("target_tab_id") != selected_widget.id:
                    st.session_state["target_tab_id"] = selected_widget.id
                    changed = True
            if st.session_state.get("target_column_id") is not None:
                st.session_state["target_column_id"] = None
                changed = True
        elif selected_widget and selected_widget.type == "tabs":
            if st.session_state.get("target_container_id") != selected_widget.id:
                st.session_state["target_container_id"] = selected_widget.id
                st.session_state["add_to_container"] = selected_widget.id
                st.session_state["suppress_container_pane_sync"] = True
                changed = True
            # Auto-select first tab if none selected
            first_tab = next((w for w in design.widgets if w.parent_id == selected_widget.id and w.type == "tab"), None)
            if first_tab and st.session_state.get("target_tab_id") not in [
                w.id for w in design.widgets if w.parent_id == selected_widget.id and w.type == "tab"
            ]:
                st.session_state["target_tab_id"] = first_tab.id
                changed = True
            if st.session_state.get("target_column_id") is not None:
                st.session_state["target_column_id"] = None
                changed = True
        elif selected_widget and selected_widget.type in {"container", "empty", "expander", "form", "popover", "sidebar", "spinner", "status"}:
            if st.session_state.get("target_container_id") != selected_widget.id:
                st.session_state["target_container_id"] = selected_widget.id
                st.session_state["add_to_container"] = selected_widget.id
                st.session_state["suppress_container_pane_sync"] = True
                changed = True
            if st.session_state.get("target_column_id") is not None:
                st.session_state["target_column_id"] = None
                changed = True
            if st.session_state.get("target_tab_id") is not None:
                st.session_state["target_tab_id"] = None
                changed = True
        elif selected_widget and selected_widget.parent_id:
            parent = next((w for w in design.widgets if w.id == selected_widget.parent_id), None)
            if parent:
                if parent.type == "columns_container":
                    if st.session_state.get("target_container_id") != parent.id:
                        st.session_state["target_container_id"] = parent.id
                        st.session_state["add_to_container"] = parent.id
                        st.session_state["suppress_container_pane_sync"] = True
                        changed = True
                    if st.session_state.get("target_column_id") is not None:
                        st.session_state["target_column_id"] = None
                        changed = True
                    if st.session_state.get("target_tab_id") is not None:
                        st.session_state["target_tab_id"] = None
                        changed = True
                elif parent.type == "tab":
                    # Widget inside a tab: set container to grandparent tabs widget, target tab to parent tab
                    tabs_widget = next((w for w in design.widgets if w.id == parent.parent_id), None)
                    if tabs_widget:
                        if st.session_state.get("target_container_id") != tabs_widget.id:
                            st.session_state["target_container_id"] = tabs_widget.id
                            st.session_state["add_to_container"] = tabs_widget.id
                            st.session_state["suppress_container_pane_sync"] = True
                            changed = True
                        if st.session_state.get("target_tab_id") != parent.id:
                            st.session_state["target_tab_id"] = parent.id
                            changed = True
                    if st.session_state.get("target_column_id") is not None:
                        st.session_state["target_column_id"] = None
                        changed = True
                elif parent.type in {"container", "empty", "expander", "form", "popover", "sidebar", "spinner", "status"}:
                    if st.session_state.get("target_container_id") != parent.id:
                        st.session_state["target_container_id"] = parent.id
                        st.session_state["add_to_container"] = parent.id
                        st.session_state["suppress_container_pane_sync"] = True
                        changed = True
                    if st.session_state.get("target_column_id") is not None:
                        st.session_state["target_column_id"] = None
                        changed = True
                    if st.session_state.get("target_tab_id") is not None:
                        st.session_state["target_tab_id"] = None
                        changed = True
                elif parent.type == "column":
                    if st.session_state.get("target_container_id") != parent.parent_id:
                        st.session_state["target_container_id"] = parent.parent_id
                        st.session_state["add_to_container"] = parent.parent_id
                        st.session_state["suppress_container_pane_sync"] = True
                        changed = True
                    if st.session_state.get("target_column_id") != parent.id:
                        st.session_state["target_column_id"] = parent.id
                        changed = True
                    if st.session_state.get("target_tab_id") is not None:
                        st.session_state["target_tab_id"] = None
                        changed = True
        elif selected_widget and selected_widget.parent_id is None:
            if selected_widget.type not in {"columns_container", "container", "empty", "expander", "form", "popover", "sidebar", "spinner", "status", "tabs"}:
                if st.session_state.get("target_container_id") is not None:
                    st.session_state["target_container_id"] = None
                    st.session_state["add_to_container"] = MAIN_CONTAINER_ID
                    st.session_state["target_column_id"] = None
                    st.session_state["target_tab_id"] = None
                    st.session_state["suppress_container_pane_sync"] = True
                    changed = True
        st.session_state["hierarchy_checked_prev"] = [selected_id]
        if force_rerun:
            st.rerun()
    else:
        checked_id = st.session_state.get("hierarchy_checked_id")
        if checked_id and not st.session_state.get("hierarchy_restore_pending", False):
            st.session_state["hierarchy_restore_pending"] = True
            st.session_state["hierarchy_tree_version"] += 1
            st.rerun()
        st.session_state["hierarchy_restore_pending"] = False

    selected_id = st.session_state.get("selected_id")
    selected_widget = next((w for w in design.widgets if w.id == selected_id), None)
    if not selected_widget:
        st.info("Select a widget to move or remove it.")
        return

    selected_index = design.widgets.index(selected_widget)
    col_up, col_down, col_remove = st.columns([1, 1, 1])
    with col_up:
        if st.button("⬆️", key=f"up_tree_{selected_widget.id}_{selected_index}", use_container_width=True):
            _move_widget_block(design, selected_widget, -1)
            st.rerun()
    with col_down:
        if st.button("⬇️", key=f"down_tree_{selected_widget.id}_{selected_index}", use_container_width=True):
            _move_widget_block(design, selected_widget, 1)
            st.rerun()
    with col_remove:
        if st.button("➖", key=f"remove_tree_{selected_widget.id}_{selected_index}", use_container_width=True):
            _remove_widget_with_children(design, selected_widget.id)
            if st.session_state.get("selected_id") == selected_widget.id:
                st.session_state["selected_id"] = None
            st.session_state["hierarchy_checked_id"] = None
            st.session_state["hierarchy_checked_prev"] = []
            st.rerun()




def _remove_widget_with_children(design: Design, widget_id: str) -> None:
    remove_ids = {widget_id}
    remove_ids.update(_collect_descendant_ids(design, widget_id))
    design.widgets[:] = [widget for widget in design.widgets if widget.id not in remove_ids]


def _remove_column_with_children(container: WidgetInstance, design: Design, column_index: int) -> bool:
    count = int(container.props.get("count", 2))
    if count <= 1 or column_index < 0 or column_index >= count:
        return False

    labels = container.props.get("labels", [])
    if not isinstance(labels, list):
        labels = []
    normalized = _normalize_column_labels(count, labels)
    normalized.pop(column_index)
    container.props["labels"] = normalized
    container.props["count"] = count - 1

    direct_child_ids = [
        widget.id
        for widget in design.widgets
        if widget.parent_id == container.id and widget.column_index == column_index
    ]

    remove_ids: set[str] = set(direct_child_ids)
    for child_id in direct_child_ids:
        remove_ids.update(_collect_descendant_ids(design, child_id))

    for widget in design.widgets:
        if widget.parent_id == container.id and widget.column_index is not None and widget.column_index > column_index:
            widget.column_index -= 1

    design.widgets[:] = [widget for widget in design.widgets if widget.id not in remove_ids]
    return True


def _safe_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main() -> None:
    st.set_page_config(page_title="Streamlit UI Designer", layout="wide")
    _ensure_state()
    _inject_layout_css()
    design = st.session_state["design"]

    with st.container(key="ui1_palette_dock"):
        _render_palette(design)

    _render_page_offset()

    st.title(" ")
    tab_design, tab_code = st.tabs(["Design", "Generated Code"])

    with tab_design:
        st.divider()
        hierarchy_collapsed = st.session_state.get("ui1_hierarchy_collapsed", False)
        properties_collapsed = st.session_state.get("ui1_properties_collapsed", False)
        if hierarchy_collapsed and properties_collapsed:
            column_spec = [0.45, 7.1, 0.45]
        elif hierarchy_collapsed:
            column_spec = [0.45, 6.55, 1]
        elif properties_collapsed:
            column_spec = [2, 5.55, 0.45]
        else:
            column_spec = [1.2, 4, 1.2]
        col_hierarchy, col_preview, col_props = st.columns(column_spec)
        with col_hierarchy:
            if hierarchy_collapsed:
                with st.container(height=SCROLLABLE_PANE_HEIGHT, border=True):
                    if st.button("▶️", key="ui1_expand_hierarchy"):
                        st.session_state["ui1_hierarchy_collapsed"] = False
                        st.rerun()
            else:
                header_left, header_right = st.columns([5, 1])
                with header_left:
                    st.subheader("Hierarchy")
                with header_right:
                    st.write("")
                    if st.button("◀️", key="ui1_collapse_hierarchy", use_container_width=True):
                        st.session_state["ui1_hierarchy_collapsed"] = True
                        st.rerun()
                with st.container(height=SCROLLABLE_PANE_HEIGHT, border=True):
                    _render_hierarchy(design)
        with col_preview:
            st.subheader("Preview")
            with st.container(height=SCROLLABLE_PANE_HEIGHT, border=True, key="ui1_preview_pane"):
                _render_preview(design)
        with col_props:
            if properties_collapsed:
                with st.container(height=SCROLLABLE_PANE_HEIGHT, border=True):
                    if st.button("◀️", key="ui1_expand_properties"):
                        st.session_state["ui1_properties_collapsed"] = False
                        st.rerun()
            else:
                header_left, header_right = st.columns([2, 3])
                with header_left:
                    if st.button("▶️", key="ui1_collapse_properties", use_container_width=True):
                        st.session_state["ui1_properties_collapsed"] = True
                        st.rerun()
                with header_right:
                    st.write("")
                with st.container(height=SCROLLABLE_PANE_HEIGHT, border=True, key="ui1_properties_pane"):
                    _render_properties(design)

    with tab_code:
        _render_code_import()
        _render_generated_code(st.session_state["design"])


if __name__ == "__main__":
    main()