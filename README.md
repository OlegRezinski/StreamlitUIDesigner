# Streamlit UI Designer

A Streamlit app that lets you assemble a UI with basic widgets and generates Streamlit Python code from the design.

## Features (M2 + M3)
- Palette, canvas, and properties panels for basic widget composition.
- Generated code panel with download button.
- Place widgets inside Columns containers.

## New Widgets (M5)
- Toggle
- Multiselect
- Color picker
- Columns container
- Column
- Text

## Documentation
- Developer guide: `docs/developer-guide.md`
- Adding widgets: `docs/adding-widgets.md`
- Regression checklist: `docs/regression-checklist.md`
- Example design: `examples/sample_design.json`

## Quick Start
- Install dependencies:
  ```powershell
  pip install -r requirements.txt
  ```
- Run the designer:
  ```powershell
  streamlit run app.py
  ```

## Tests
- Run tests:
  ```powershell
  pytest
  ```

## Project Structure
- `app.py`: Streamlit designer UI.
- `designer/`: core models, registry, codegen, and widget definitions.
- `tests/`: basic tests for core logic.
