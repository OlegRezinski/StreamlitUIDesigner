from __future__ import annotations

import uuid
from datetime import date
from pathlib import Path
from typing import Dict, List

import streamlit as st
from streamlit_tree_select import tree_select

from designer.codegen import generate_streamlit_code
from designer.models import Design, PropDefinition, WidgetInstance
from designer.registry import clear_registry, list_widgets
from designer.widgets import register_default_widgets


MAIN_CONTAINER_ID = "__main__"
ICONS_DIR = Path(__file__).resolve().parent / "Icons"
PALETTE_ICON_BY_TYPE = {
    "button": ICONS_DIR / "icons8-button-50.png",
    "checkbox": ICONS_DIR / "icons8-checkbox-50.png",
    "color_picker": ICONS_DIR / "icons8-color-palette-50.png",
    "container": ICONS_DIR / "icons8-column-50.png",
    "columns_container": ICONS_DIR / "icons8-column-50.png",
    "date_input": ICONS_DIR / "icons8-date-to-50.png",
    "file_uploader": ICONS_DIR / "icons8-upload-50.png",
    "multiselect": ICONS_DIR / "icons8-multiselect-menu-50.png",
    "number_input": ICONS_DIR / "icons8-numbers-input-form-50.png",
    "radio": ICONS_DIR / "icons8-radio-button-50.png",
    "selectbox": ICONS_DIR / "icons8-dropdown-field-50.png",
    "slider": ICONS_DIR / "icons8-slider-50.png",
    "text": ICONS_DIR / "icons8-text-50.png",
    "title": ICONS_DIR / "icons8-text-50.png",
    "text_area": ICONS_DIR / "icons8-text-areae-50.png",
    "text_input": ICONS_DIR / "icons8-text-input-50.png",
    "toggle": ICONS_DIR / "icons8-toggle-button-50.png",
}
MATERIAL_ICON_BY_TYPE = {
    "badge": ":material/bookmark:",
    "button": ":material/buttons_alt:",
    "caption": ":material/short_text:",
    "checkbox": ":material/check_box:",
    "code": ":material/code:",
    "color_picker": ":material/color_lens:",
    "container": ":material/iframe:",
    "columns_container": ":material/view_column:",
    "date_input": ":material/date_range:",
    "file_uploader": ":material/upload:",
    "header": ":material/format_size:",
    "markdown": ":material/markdown:",
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
}

SCROLLABLE_PANE_HEIGHT = 720
PALETTE_FIXED_TOP_REM = 0.0
PAGE_TOP_OFFSET_REM = 9.5


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
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_page_offset() -> None:
    st.container(key="ui1_page_offset")


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
    if "ui1_hierarchy_collapsed" not in st.session_state:
        st.session_state["ui1_hierarchy_collapsed"] = False
    if "ui1_properties_collapsed" not in st.session_state:
        st.session_state["ui1_properties_collapsed"] = False


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


def _move_widget(widgets: List[WidgetInstance], index: int, direction: int) -> None:
    new_index = index + direction
    if new_index < 0 or new_index >= len(widgets):
        return
    widgets[index], widgets[new_index] = widgets[new_index], widgets[index]


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

    if prop.input_type == "text":
        widget.props[prop.name] = st.text_input(prop.label, value=str(value), key=key)
    elif prop.input_type == "multiline":
        widget.props[prop.name] = st.text_area(prop.label, value=str(value), key=key)
    elif prop.input_type == "bool":
        widget.props[prop.name] = st.checkbox(prop.label, value=bool(value), key=key)
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
    parent_id = None
    if target_container_id:
        container = next((w for w in design.widgets if w.id == target_container_id), None)
        if container:
            columns, _ = _sync_columns_children(design, container)
            parent_id = target_column_id or (columns[0].id if columns else None)
    instance = _new_widget_instance(
        definition.type,
        definition.defaults,
        parent_id=parent_id,
    )
    design.widgets.append(instance)
    st.session_state["selected_id"] = instance.id
    st.rerun()


def _render_palette(design: Design) -> None:
    definitions = [
        definition
        for definition in sorted(list_widgets(), key=lambda item: item.label.lower())
        if definition.type != "column"
    ]

    definitions = definitions[:15]
    buttons_per_row = 8
    total_rows = 3
    for row_index in range(total_rows):
        row_columns = st.columns(buttons_per_row)
        row_definitions = definitions[row_index * buttons_per_row:(row_index + 1) * buttons_per_row]
        for col_index in range(buttons_per_row):
            with row_columns[col_index]:
                if col_index >= len(row_definitions):
                    st.empty()
                    continue
                definition = row_definitions[col_index]
                material_icon = MATERIAL_ICON_BY_TYPE.get(definition.type)
                button_label = definition.label
                if material_icon:
                    button_label = f"{material_icon}  {button_label}"
                if st.button(button_label, key=f"ui1_add_{definition.type}", use_container_width=True):
                    _add_palette_widget(design, definition)


def _render_properties(design: Design) -> None:
    st.subheader("Container")
    selected_id = st.session_state.get("selected_id")
    selected = next((w for w in design.widgets if w.id == selected_id), None)
    containers = _get_columns_containers(design)
    container_ids = [widget.id for widget in containers]
    widget_by_id = {widget.id: widget for widget in design.widgets}

    def _container_label(cid: str) -> str:
        parts: list[str] = []
        current = widget_by_id.get(cid)
        while current is not None:
            label = str(current.props.get("label", "Columns")).strip() or "Columns"
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
                if selected_node.type == "columns_container":
                    current_container = selected_node.id
                elif selected_node.type == "column":
                    current_container = selected_node.parent_id or MAIN_CONTAINER_ID
                elif selected_node.parent_id:
                    parent_node = next((w for w in design.widgets if w.id == selected_node.parent_id), None)
                    if parent_node and parent_node.type == "column":
                        current_container = parent_node.parent_id or MAIN_CONTAINER_ID
                    elif parent_node and parent_node.type == "columns_container":
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
        if container_widget:
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
            "Background image",
            value=design.background_image,
            key="main_background_image",
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


def _render_preview(design: Design) -> None:
    st.subheader("Preview")
    if design.background_color or design.background_image:
        css_parts = [".st-key-ui1_preview_pane { "]
        if design.background_color:
            css_parts.append(f"background-color: {design.background_color}; ")
        if design.background_image:
            css_parts.append(f"background-image: url('{design.background_image}'); ")
            css_parts.append("background-size: cover; background-repeat: no-repeat; background-position: center; ")
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
        if widget.type == "column":
            return
        definition.render(widget)

    for widget in design.widgets:
        if widget.parent_id:
            continue
        _render_widget(widget)


def _render_hierarchy(design: Design) -> None:
    children: dict[str, list[WidgetInstance]] = {}
    for widget in design.widgets:
        if widget.parent_id:
            children.setdefault(widget.parent_id, []).append(widget)

    def _label_for(widget: WidgetInstance) -> str:
        definition = next((w for w in list_widgets() if w.type == widget.type), None)
        label = widget.props.get("label", definition.label if definition else widget.type)
        return f"{definition.label if definition else widget.type}: {label}"

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
        elif selected_widget and selected_widget.type == "columns_container":
            if st.session_state.get("target_container_id") != selected_widget.id:
                st.session_state["target_container_id"] = selected_widget.id
                st.session_state["add_to_container"] = selected_widget.id
                st.session_state["suppress_container_pane_sync"] = True
                changed = True
            if st.session_state.get("target_column_id") is not None:
                st.session_state["target_column_id"] = None
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
                elif parent.type == "column":
                    if st.session_state.get("target_container_id") != parent.parent_id:
                        st.session_state["target_container_id"] = parent.parent_id
                        st.session_state["add_to_container"] = parent.parent_id
                        st.session_state["suppress_container_pane_sync"] = True
                        changed = True
                    if st.session_state.get("target_column_id") != parent.id:
                        st.session_state["target_column_id"] = parent.id
                        changed = True
        elif selected_widget and selected_widget.parent_id is None:
            if selected_widget.type != "columns_container":
                if st.session_state.get("target_container_id") is not None:
                    st.session_state["target_container_id"] = None
                    st.session_state["add_to_container"] = MAIN_CONTAINER_ID
                    st.session_state["target_column_id"] = None
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
            _move_widget(design.widgets, selected_index, -1)
            st.rerun()
    with col_down:
        if st.button("⬇️", key=f"down_tree_{selected_widget.id}_{selected_index}", use_container_width=True):
            _move_widget(design.widgets, selected_index, 1)
            st.rerun()
    with col_remove:
        if st.button("➖", key=f"remove_tree_{selected_widget.id}_{selected_index}", use_container_width=True):
            _remove_widget_with_children(design, selected_widget.id)
            if st.session_state.get("selected_id") == selected_widget.id:
                st.session_state["selected_id"] = None
            st.session_state["hierarchy_checked_id"] = None
            st.session_state["hierarchy_checked_prev"] = []
            st.rerun()


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
    st.set_page_config(page_title="Streamlit UI Designer - UI 1", layout="wide")
    _ensure_state()
    _inject_layout_css()
    design = st.session_state["design"]

    with st.container(key="ui1_palette_dock"):
        _render_palette(design)

    _render_page_offset()

    st.title("Streamlit UI Designer - UI 1")
    st.caption("Visual prototype for palette icon buttons.")
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
            column_spec = [2, 5, 1]
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
                with st.container(height=SCROLLABLE_PANE_HEIGHT, border=True):
                    _render_properties(design)

    with tab_code:
        _render_generated_code(st.session_state["design"])


if __name__ == "__main__":
    main()

