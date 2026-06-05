# Developer Guide

This guide covers the core architecture and where to implement changes.

## Project Structure
- `app.py`: Streamlit UI for the designer (palette, canvas, properties, preview, code).
- `designer/`: core logic (models, registry, widgets, codegen).
- `tests/`: pytest-based tests.
- `examples/`: sample designs (JSON).

## Core Flow
1. Widgets are defined in `designer/widgets.py` using `WidgetDefinition`.
2. The registry holds widget definitions and is used by the app to render the palette, canvas, and preview.
3. Code generation uses each widget definition's `codegen` function.
4. Preview uses each widget definition's `render` function.

## Where to Change Things
- Add/modify widgets: `designer/widgets.py`.
- Update UI layout: `app.py`.
- Update models/serialization: `designer/models.py`, `designer/serialization.py`.
- Add tests: `tests/`.

Note: layout-style widgets (like Columns) live in `designer/widgets.py` alongside standard inputs.
Widgets can be nested inside Columns via `parent_id` and `column_index` on `WidgetInstance`.

## Running Locally
```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Tests
```powershell
pytest
```
