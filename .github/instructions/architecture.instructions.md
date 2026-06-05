# M1 — Core Architecture Plan

## Scope
- Data model: `Design`, `WidgetInstance`, `WidgetDefinition`
- Registry: central widget registry + helper
- Serialization: JSON export/import with stable ordering
- Tests: round-trip JSON and registry lookup

## Proposed Module Layout
- `designer/models.py` — dataclasses for `Design`, `WidgetInstance`, `WidgetDefinition`
- `designer/registry.py` — registry structure, `register_widget`, `get_widget`, `list_widgets`
- `designer/serialization.py` — `design_to_dict`, `design_from_dict`
- `designer/__init__.py` — export key types/functions
- `tests/test_models.py` — round-trip serialization tests
- `tests/test_registry.py` — registry lookup tests

## Implementation Steps
1. Models
   - `WidgetInstance` fields: `id`, `type`, `props`, `order`
   - `WidgetDefinition` fields: `type`, `label`, `props_schema`, `defaults`, `codegen`
   - `Design` fields: `name`, `widgets`
2. Registry
   - Registry dict keyed by `type`
   - Helpers: `register_widget(defn)`, `get_widget(type)`, `list_widgets()`
3. Serialization
   - `to_dict()`/`from_dict()` for `WidgetInstance` and `Design`
   - Stable ordering by `order` or list position
4. Tests
   - `Design` round-trip: dict -> object -> dict equals original
   - Registry lookup returns correct definition

## Acceptance Checks
- Create a `Design` with 2 widgets, serialize to dict, deserialize, and compare
- Register a widget definition and fetch it by type
- Tests pass for models + registry

## Notes / Assumptions
- Use standard library only (dataclasses, typing, json)
- Serialization uses JSON-ready dicts, not file IO

