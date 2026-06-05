# Container Widget Implementation Guide

A **container widget** is any widget that can hold child widgets in the hierarchy pane
(e.g. `st.empty`, `st.container`, `st.columns`). Follow every section below when
implementing a new one.

---

## 1. Definition in `designer/widgets.py`

### 1.1 Registration

Register the widget with `_codegen_noop` and `_render_noop` — all container logic
lives outside the widget definition (in `codegen.py` and `UI_2.py`):

```python
_register(WidgetDefinition(
    type="<type>",          # e.g. "empty", "expander"
    label="<Label>",
    props_schema=[
        PropDefinition("label", "Label", "text", "<Default label>"),
        # add widget-specific props here
    ],
    defaults={"label": "<Default label>"},
    codegen=_codegen_noop,
    render=_render_noop,
))
```

> **Do not** write a custom `codegen` or `render` function for the container itself —
> those are handled centrally (see sections 2 and 3).

---

## 2. Code Generation — `designer/codegen.py`

Add a branch **before** the generic `definition.codegen(widget)` call inside
`_emit_widget()`:

```python
if widget.type == "<type>":
    label = str(widget.props.get("label", "<Label>")).strip() or "<Label>"
    lines.append(f"{indent}# {label}")
    lines.append(f"{indent}with st.<function>(<args>):")
    nested = children.get(widget.id, [])
    if not nested:
        lines.append(f"{indent}    pass")
    else:
        for child in nested:
            _emit_widget(child, indent + "    ")
    return
```

Rules:
- Always emit a `# <label>` comment before the `with` block.
- Emit `pass` when there are no children (valid Python).
- Recurse into children with increased `indent`.
- Call `return` at the end so the generic path is not executed.

---

## 3. Preview Rendering — `UI_2.py → _render_preview → _render_widget`

Add a branch for the new type **before** `definition.render(widget)`:

```python
if widget.type == "<type>":
    nested = children.get(widget.id, [])
    label = str(widget.props.get("label", "<Label>")).strip() or "<Label>"
    with st.container(border=True, key=f"preview_<type>_{widget.id}"):
        st.caption(f"<icon> st.<function> — {label}")
        if nested:
            for child in nested:
                _render_widget(child)
        else:
            st.markdown(
                "<span style='font-size:11px;color:#aaa;'>"
                "# <placeholder comment>"
                "</span>",
                unsafe_allow_html=True,
            )
    return
```

> **Important:** Never use `with st.<actual_function>():` directly in the preview if
> that function has single-element semantics (like `st.empty`) or side-effects that
> are inappropriate in a designer context. Use `st.container` as the visual wrapper
> and add a caption to identify the widget type.

---

## 4. Hierarchy & Container Pane — `UI_2.py`

### 4.1 Icon

Add the type to `MATERIAL_ICON_BY_TYPE`:

```python
"<type>": ":material/<icon_name>:",
```

### 4.2 Container dropdown (`_get_all_containers`)

`_get_all_containers` already returns all widgets whose type is in
`{"columns_container", "container", "empty"}`. Add the new type to that set:

```python
def _get_all_containers(design: Design) -> list[WidgetInstance]:
    return [widget for widget in design.widgets
            if widget.type in {"columns_container", "container", "empty", "<type>"}]
```

### 4.3 Hierarchy auto-selection (`_render_hierarchy`)

In the hierarchy selection handler, two branches must cover the new type:

**a) New type selected directly:**
```python
elif selected_widget and selected_widget.type in {"container", "empty", "<type>"}:
    # set target_container_id = selected_widget.id
```

**b) Child of new type selected:**
```python
elif parent.type in {"container", "empty", "<type>"}:
    # set target_container_id = parent.id
```

**c) Root-level guard** — prevent resetting the container pane when the new type is
selected at the top level:
```python
if selected_widget.type not in {"columns_container", "container", "empty", "<type>"}:
    # reset to MAIN_CONTAINER_ID
```

### 4.4 `_is_columns_container` is unchanged

This function returns `True` only for `columns_container`.  All other container types
(including new ones) use the **direct-child** path (no "Target column" sub-selector).

---

## 5. Move Up / Down — `_move_widget_block`

`_move_widget_block` already handles any widget that has descendants by moving the
entire block (widget + children) together. **No changes are needed** for new container
types — the function is generic.

However, if the new container type has **auto-managed child widgets** (like `column`
children of `columns_container`), implement a dedicated `_sync_<type>_children`
function and call it from `_render_properties` next to the `_sync_columns_children`
pattern.

---

## 6. Palette

### 6.1 `Elements.txt`

Add the element under the appropriate category:

```
Layouts and containers
    st.<function>
```

### 6.2 `UI_2.py → ELEMENT_ICON_BY_NAME`

Add an entry:

```python
"<type>": ":material/<icon_name>:",
```

> If the palette name (`st.<function>`) maps to a different registry type, add an
> alias to `ELEMENT_TYPE_ALIASES`:
> ```python
> "<palette_name>": "<registry_type>",
> ```

---

## 7. Tests — `tests/test_<type>.py`

Create a test file with at minimum:

| Test | What to assert |
|---|---|
| `test_<type>_registered` | `get_widget("<type>")` is not None, label correct, props present |
| `test_codegen_<type>_no_children` | `"with st.<function>():"` in code, `"pass"` in code |
| `test_codegen_<type>_label_comment` | `"# <custom label>"` in code |
| `test_codegen_<type>_with_child` | child rendered indented inside the block |
| `test_codegen_<type>_no_pass_with_children` | `"pass"` NOT in code when children present |

Standard test setup:

```python
def setup_function() -> None:
    clear_registry()
    register_default_widgets()
```

---

## 8. Regression Checklist — `docs/regression-checklist.md`

Append a section:

```markdown
## <Label>

- [ ] Widget appears in palette under "Layouts and containers".
- [ ] Adding widget shows a bordered preview placeholder in the canvas.
- [ ] Children added inside it are visible in the preview.
- [ ] Selecting the widget in hierarchy sets the Container pane to it.
- [ ] Selecting a child in hierarchy sets the Container pane to the parent <type>.
- [ ] Moving the widget with ⬆️/⬇️ moves the entire block (widget + children).
- [ ] A neighbouring widget moving past it swaps with the whole block.
- [ ] Generated code contains `with st.<function>():` with children indented.
- [ ] Empty block generates `pass` placeholder.
```

---

## Quick Checklist

- [ ] `designer/widgets.py` — registered with `_codegen_noop` / `_render_noop`
- [ ] `designer/codegen.py` — `_emit_widget` branch added
- [ ] `UI_2.py` — `_render_widget` preview branch added
- [ ] `UI_2.py` — `MATERIAL_ICON_BY_TYPE` entry added
- [ ] `UI_2.py` — `_get_all_containers` set updated
- [ ] `UI_2.py` — hierarchy auto-selection branches updated (3 places)
- [ ] `Elements.txt` — element listed
- [ ] `UI_2.py` — `ELEMENT_ICON_BY_NAME` entry added (already present if planned earlier)
- [ ] `tests/test_<type>.py` — test file created, all tests pass
- [ ] `docs/regression-checklist.md` — section appended

