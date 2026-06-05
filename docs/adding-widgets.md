# Adding a Widget

This project uses a registry pattern. Each widget has a definition with properties, codegen, and preview rendering.

## Steps
1. Open `designer/widgets.py`.
2. Add a codegen function that returns a list of code lines.
3. Add a render function that draws the widget in Preview.
4. Register the widget in `register_default_widgets()` with `WidgetDefinition`:
   - `type`: unique id (snake_case)
   - `label`: human-readable name
   - `props_schema`: list of `PropDefinition`
   - `defaults`: default prop values
   - `codegen`: your codegen function
   - `render`: your render function

## Example
```python
# codegen
def _codegen_example(widget: WidgetInstance) -> list[str]:
    label = widget.props.get("label", "Example")
    return [f"st.text_input({label!r}, key={widget.id!r})"]

# render
def _render_example(widget: WidgetInstance) -> None:
    label = widget.props.get("label", "Example")
    st.text_input(label, key=widget.id)

# register
_register(
    WidgetDefinition(
        type="example",
        label="Example",
        props_schema=[PropDefinition("label", "Label", "text", "Example")],
        defaults={"label": "Example"},
        codegen=_codegen_example,
        render=_render_example,
    )
)
```

## Notes
- Keep `type` unique and stable.
- Use `widget.id` as the Streamlit key for determinism.
- Keep options lists non-empty via `_ensure_options`.
- Container-style widgets can accept children via `parent_id` and `column_index` on `WidgetInstance`.
