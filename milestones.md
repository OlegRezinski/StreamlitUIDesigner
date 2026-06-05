# M0 — Scope & Acceptance

- Scope:
  - Single-page designer app with a palette, canvas, and properties panel
  - Store design in session state and allow export to JSON
  - Generate a single Streamlit Python file from the design
  - Initial widget set:
    - Text input
    - Text area
    - Button
    - Checkbox
    - Selectbox
    - Radio
    - Slider
    - Number input
    - Date input
    - File uploader
    - Columns
- Acceptance criteria:
  - Add, configure, and reorder widgets from the initial set
  - Generated code runs without manual edits and matches the canvas layout
  - Design can be exported to JSON and reloaded

# M1 — Core Architecture

- Data model:
  - Define `Design` (name, widgets list, optional layout metadata)
  - Define `WidgetInstance` (id, type, props, order)
  - Define `WidgetDefinition` (type, label, props schema, defaults, codegen)
- Registry:
  - Central widget registry with lookup by `type`
  - Add a small helper for registering widgets in one place
- Serialization:
  - JSON export/import for `Design` and `WidgetInstance`
  - Ensure stable ordering in serialized data
- Acceptance criteria:
  - Can create a `Design` in code, serialize to JSON, and load it back
  - Registry resolves widget definitions by `type`
  - Models are unit-tested for round-trip JSON behavior

# M2 — Minimal Designer UI

- Layout:
  - Palette panel (left): list of available widgets with “Add” actions
  - Canvas panel (center): ordered list of placed widgets
  - Properties panel (right): edit selected widget props
- UX behaviors:
  - Add widgets to canvas
  - Select a widget to edit its props
  - Reorder widgets (move up/down)
  - Remove widget from canvas
- State handling:
  - Keep `Design` in session state
  - Keep current selection in session state
- Acceptance criteria:
  - Build a design with at least 3 widgets and reorder them
  - Properties edits update the design state and codegen output

# M3 — Code Generation v1

- Codegen:
  - Generate a single `.py` file with `import streamlit as st`
  - Emit widgets in canvas order
  - Include widget labels and basic props
  - Add explicit keys when needed
- Output UX:
  - “Generated code” panel (read-only) with syntax highlighting
  - Download button for the generated `.py` file
- Acceptance criteria:
  - Generated code runs without manual edits
  - The output UI matches the canvas order and widget props

# M4 — Preview Mode

- Preview:
  - Preview tab that renders the design directly in the designer app
  - Use the same `Design` model to render widgets
- Consistency:
  - Preview output matches generated code behavior
- Acceptance criteria:
  - Switching between Design and Preview keeps state consistent
  - Preview reflects latest property changes

# M5 — Extensibility & Documentation

- Extensibility:
  - Add 2–3 new widgets using the registry pattern
  - Document how to add a new widget in the registry
- Docs:
  - Add minimal developer guide and architecture notes
  - Provide a small example JSON design file
- Acceptance criteria:
  - A new widget can be added without changing core logic
  - Documentation is sufficient for another developer to add a widget

# M6 — Polish & Stability

- Validation:
  - Basic input validation for required props
  - Provide defaults and graceful error messages
- QA:
  - Smoke test that loads a sample design and generates code
  - Regression checklist for codegen and preview
- Acceptance criteria:
  - No crashes on invalid user input
  - Sample design renders in preview and generates valid code
