# Copilot Instructions

## Project Description
A Streamlit app that lets users design a UI visually and generates Streamlit Python code from that design. The designer focuses on a simple, modular architecture so new widgets and features can be added with minimal changes to core logic.

For any code changes (unless explicitly told otherwise), follow `.github\instructions\code-implementation-workflow.instructions.md`.
Use `.github\instructions\architecture.instructions.md` as the default source of truth for implementation details; if a user request conflicts, ask for clarification.
When changing Design tab behavior or UI in `app.py`, follow `.github\instructions\design-tab-guidlines.instructions.md`.

## Goals
- Provide a palette of basic Streamlit widgets and a canvas to compose a UI.
- Allow configuration of widget properties via a properties panel.
- Generate a single Streamlit Python file that reproduces the design.
- Keep the codebase modular and easy to extend (registry-based widgets).

## Non-Goals (Initial Phase)
- Drag-and-drop layout with arbitrary grids.
- Multi-page app generation.
- Advanced theming or custom CSS injection.

## Architecture (High-Level)
- `designer/` package holds core logic (models, registry, codegen, UI panels).
- A design is a structured model (page -> list of widgets -> props).
- Widgets are registered in a registry with metadata, default props, and codegen.
- UI panels:
  - Palette: list of widgets to add.
  - Canvas: ordered list of widgets in the design.
  - Properties: edit selected widget props.

## Development Principles
- Prefer small, composable modules.
- Keep widget-specific logic inside widget definitions.
- Use plain Python dataclasses or lightweight models for the design schema.
- Keep codegen deterministic and easy to test.

## Data Model (Suggested)
- `Design`: name, list of `WidgetInstance`.
- `WidgetInstance`: id, type, props.
- `WidgetDefinition`: type, label, props schema, defaults, codegen fn.

## Code Generation Guidelines
- Use explicit keys for widgets where needed.
- Generate code in a stable order matching canvas order.
- Include minimal imports (`import streamlit as st`).

## Testing Notes
- Unit-test codegen for each widget.
- Add a minimal smoke test that loads a sample design and generates code.

## Conventions
- Use ASCII where possible.
- Prefer short, clear function and variable names.
- Keep Streamlit UI/layout code in `app.py`; keep core logic in `designer/`.
