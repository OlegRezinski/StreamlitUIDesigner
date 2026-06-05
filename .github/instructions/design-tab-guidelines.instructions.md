# Design Tab Guidelines

This document defines the behavior of the Design tab: widget hierarchy tree, container pane, and properties pane, and how each panel influences the others.

## Widget Hierarchy Tree

### Core Rules
- On app start, the Main node is checked by default, showing main container properties and allowing adding widgets to the top level.
- In the hierarchy tree, only one checkbox can be checked at a time.
- Selecting a node updates the properties pane to show that node's properties.
- Selecting a node updates the container pane according to the mapping rules below.
- The tree includes a top-level "Main" node representing the main container.
- All created widgets should use Streamlit widgets; when additional styling is needed, apply it via `st.markdown` in both preview and code generation.

### Node Types
- Main (root)
- Columns container
- Column
- Regular widgets (all non-container widgets)

### Selection Mapping (Tree -> Container Pane)
- Main selected:
  - Container pane "Add to container" is set to Main.
  - The Target column selector in the container pane is hidden and its selection is cleared.
- Columns container selected:
  - Container pane "Add to container" is set to that container.
  - The Target column selector in the container pane is hidden and its selection is cleared.
- Column selected:
  - Container pane "Add to container" is set to the parent columns container.
  - Target column is set to the selected column.
- Regular widget selected:
  - If the widget is inside a column:
    - Container pane "Add to container" is set to the parent columns container.
    - Target column is set to the parent column.
  - If the widget is a direct child of Main:
    - Container pane "Add to container" is set to Main.
    - The Target column selector in the container pane is hidden and its selection is cleared.

### Selection Mapping (Tree -> Properties Pane)
- The properties pane always shows the properties of the checked node.
- Main selected: show main container properties.
- Columns container selected: show columns container properties.
- Column selected: show column properties.
- Regular widget selected: show that widget's properties.

## Container Pane

### Purpose
- Controls where new widgets are added (Main or a specific columns container).
- When a columns container is selected, it can also choose a target column for placement.

### Behavior
- "Add to container" options:
  - Main
  - All existing columns containers
- If Main is selected:
  - New widgets are added at the top level (no parent).
  - The Target column selector in the container pane is hidden and its selection is cleared.
- If a columns container is selected:
  - New widgets are added inside that container.
  - When a columns container is selected in the container pane:
    - If the hierarchy selection is a column, hide the Target column selector and clear its selection.
    - If the hierarchy selection is not a column, show the Target column selector.

### Container Pane -> Tree Influence
- When the user changes "Add to container":
  - The hierarchy tree selection is set to the corresponding container, replacing the previously checked node.
  - The tree should expand to reveal the selected container when possible.

### Container Pane -> Properties Pane
- Changing "Add to container" updates the hierarchy selection to that container, which updates the properties pane accordingly.

## Properties Pane

### Behavior
- Shows properties for the currently checked node in the tree.
- If no node is checked, shows a guidance message.

### Properties Pane -> Tree Influence
- Editing properties does not change the checked node in the tree.
- Label edits update the node label in the tree.

### Properties Pane -> Container Pane Influence
- Editing properties does not change the selected container directly.
- For columns container, changing the column count updates column children and may update available target columns.

## Summary of Cross-Panel Influence

- Tree drives both container pane selection and properties pane contents.
- Container pane drives tree selection only when the user changes the "Add to container" dropdown.
- Properties edits do not change which node is checked; they only update labels/values shown in the tree and container pane.
