"""Reconstruct a :class:`~designer.models.Design` from generated Streamlit code.

This is the inverse of :func:`designer.codegen.generate_streamlit_code`. It is
used by the designer UI to let users upload a previously downloaded ``app.py``
and have the Preview / Hierarchy / Properties panes render the reconstructed UI.

SECURITY INVARIANT
------------------
This module is *parse-only*. It NEVER executes, imports, compiles-for-exec, or
``eval``s the uploaded source. The only evaluation performed is
``ast.literal_eval`` applied to *individual literal argument nodes* (which itself
refuses to evaluate names, calls, or attributes). Uploaded code is therefore
inert: arbitrary/dangerous statements are simply skipped with a diagnostic.

Reconstruction is best-effort:
- Widget *types*, nesting (``parent_id``), order, and column/tab structure are
  recovered faithfully.
- Props that codegen emits as call arguments are recovered; props that codegen
  omits (defaults) are restored from the widget registry defaults.
- Container labels live in ``# comment`` lines which ``ast`` discards, so
  containers fall back to their default labels.
- Widget ``key=<uuid>`` values are reused as the reconstructed widget id when
  present (improves fidelity); otherwise a fresh ``uuid4`` is minted.
"""

from __future__ import annotations

import ast
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .backgrounds import parse_background_style
from .models import Design, WidgetInstance
from .registry import get_widget, list_widgets

# Hard cap to avoid pathological inputs (characters).
_MAX_SOURCE_CHARS = 1_000_000

# Structural container functions handled explicitly by the walker. Maps the
# ``st.<fn>`` name to the registry widget type.
_CONTAINER_FUNCS: Dict[str, str] = {
    "container": "container",
    "empty": "empty",
    "expander": "expander",
    "form": "form",
    "popover": "popover",
    "status": "status",
    "spinner": "spinner",
}

# Structural widget types that are NOT reconstructed via the generic call path.
_STRUCTURAL_TYPES = {
    "columns_container",
    "column",
    "tabs",
    "tab",
    "container",
    "empty",
    "expander",
    "form",
    "popover",
    "status",
    "spinner",
    "sidebar",
}

# Kwarg-name -> prop-name aliases for the generic widget path.
_KWARG_ALIASES: Dict[str, str] = {
    "value": "value",
    "index": "index",
    "options": "options",
    "default": "default",
    "min_value": "min",
    "max_value": "max",
    "step": "step",
    "disabled": "disabled",
    "type": "type",
    "help": "help",
    "icon": "icon",
    "placeholder": "placeholder",
    "format": "format",
    "delta": "delta",
}


@dataclass
class ImportDiagnostic:
    """A single message produced while importing code."""

    severity: str  # "error" | "warning" | "info"
    message: str
    lineno: Optional[int] = None
    col: Optional[int] = None
    node_summary: str = ""


@dataclass
class ImportResult:
    """Result of :func:`import_design_from_code`."""

    design: Optional[Design]
    diagnostics: List[ImportDiagnostic] = field(default_factory=list)

    @property
    def errors(self) -> List[ImportDiagnostic]:
        return [d for d in self.diagnostics if d.severity == "error"]

    @property
    def warnings(self) -> List[ImportDiagnostic]:
        return [d for d in self.diagnostics if d.severity == "warning"]

    @property
    def infos(self) -> List[ImportDiagnostic]:
        return [d for d in self.diagnostics if d.severity == "info"]

    @property
    def ignored(self) -> List[ImportDiagnostic]:
        """Genuinely skipped non-Streamlit / unsupported top-level statements.

        Distinct from internal ``info`` notes (e.g. style/anchor markdown that
        is part of normal reconstruction).
        """
        return [d for d in self.diagnostics if d.severity == "ignored"]

    @property
    def widget_count(self) -> int:
        return len(self.design.widgets) if self.design is not None else 0

    @property
    def ok(self) -> bool:
        return self.design is not None and not self.errors


_UNRESOLVED = object()


def _literal(node: ast.AST) -> Any:
    """Safely evaluate a literal argument node, or return ``_UNRESOLVED``."""
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, RecursionError, MemoryError):
        return _UNRESOLVED


def _new_id() -> str:
    return str(uuid.uuid4())


def _call_summary(call: ast.Call) -> str:
    """Short readable summary of a call's callee, e.g. ``print(...)``."""
    func = call.func
    if isinstance(func, ast.Attribute):
        base = func.value.id if isinstance(func.value, ast.Name) else "?"
        return f"{base}.{func.attr}(...)"
    if isinstance(func, ast.Name):
        return f"{func.id}(...)"
    return "<call>(...)"


class _Importer:
    def __init__(self, source: str, design_name: str) -> None:
        self.source = source
        self.design = Design(name=design_name)
        self.diagnostics: List[ImportDiagnostic] = []
        self.st_alias = "st"
        self._background_seen = False
        # variable name -> ("columns"|"tabs", container_id, [child_ids])
        self._var_map: Dict[str, Tuple[str, str, List[str]]] = {}
        # st-function name -> widget type for generic (non-structural) widgets.
        self._reverse: Dict[str, str] = {}

    # -- diagnostics helpers -------------------------------------------------
    def _warn(self, message: str, node: Optional[ast.AST] = None, summary: str = "") -> None:
        self.diagnostics.append(
            ImportDiagnostic("warning", message,
                             getattr(node, "lineno", None),
                             getattr(node, "col_offset", None), summary))

    def _info(self, message: str, node: Optional[ast.AST] = None, summary: str = "") -> None:
        self.diagnostics.append(
            ImportDiagnostic("info", message,
                             getattr(node, "lineno", None),
                             getattr(node, "col_offset", None), summary))

    def _ignored(self, message: str, node: Optional[ast.AST] = None, summary: str = "") -> None:
        """Record a genuinely skipped non-Streamlit / unsupported statement."""
        self.diagnostics.append(
            ImportDiagnostic("ignored", message,
                             getattr(node, "lineno", None),
                             getattr(node, "col_offset", None), summary))

    # -- AST predicates ------------------------------------------------------
    def _st_func_name(self, node: ast.AST) -> Optional[str]:
        """Return ``fn`` for a ``st.fn`` Attribute, else None."""
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == self.st_alias:
                return node.attr
        return None

    def _st_call_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Call):
            return self._st_func_name(node.func)
        return None

    # -- import alias detection ---------------------------------------------
    def _scan_imports(self, tree: ast.Module) -> bool:
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "streamlit":
                        self.st_alias = alias.asname or "streamlit"
                        found = True
            elif isinstance(node, ast.ImportFrom):
                if node.module == "streamlit":
                    found = True
        return found

    def _has_st_usage(self, tree: ast.Module) -> bool:
        for node in ast.walk(tree):
            if self._st_func_name(node) is not None:
                return True
        return False

    # -- top-level header handling ------------------------------------------
    def _handle_set_page_config(self, call: ast.Call) -> None:
        for kw in call.keywords:
            if kw.arg == "layout":
                val = _literal(kw.value)
                if val == "wide":
                    self.design.screen_width = "wide"

    def _handle_markdown(self, call: ast.Call, parent_id: Optional[str]) -> bool:
        """Handle ``st.markdown``. Returns True if it was styling (consumed).

        Generated *content* markdown never sets ``unsafe_allow_html=True`` (only
        styling ``<style>`` blocks and anchor ``<div>`` elements do), so any
        unsafe markdown is treated as styling/anchor and consumed. The first
        ``.stApp`` style block is parsed as the page background.
        """
        unsafe = any(
            kw.arg == "unsafe_allow_html" and _literal(kw.value) is True
            for kw in call.keywords
        )
        if not unsafe:
            return False  # genuine markdown content widget
        first = call.args[0] if call.args else None
        text = _literal(first) if first is not None else _UNRESOLVED
        if not self._background_seen and isinstance(text, str) and ".stApp" in text:
            color, image = parse_background_style(text)
            if color:
                self.design.background_color = color
            if image:
                self.design.background_image = image
            self._background_seen = True
        else:
            self._info("Style/anchor markdown skipped (not reconstructed).", call,
                       "st.markdown(..., unsafe_allow_html=True)")
        return True

    # -- generic widget reconstruction --------------------------------------
    def _reverse_map(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        for wd in list_widgets():
            if wd.type in _STRUCTURAL_TYPES:
                continue
            # The streamlit function name equals the widget type for generic
            # widgets in this project (e.g. text_input -> st.text_input).
            mapping[wd.type] = wd.type
        return mapping

    def _call_to_props(self, call: ast.Call, widget_type: str) -> Tuple[Dict[str, Any], Optional[str]]:
        definition = get_widget(widget_type)
        props: Dict[str, Any] = dict(definition.defaults)
        captured_key: Optional[str] = None

        # First positional -> primary text prop (label or text).
        if call.args:
            primary = _literal(call.args[0])
            if primary is not _UNRESOLVED:
                if "label" in props:
                    props["label"] = primary
                elif "text" in props:
                    props["text"] = primary
            else:
                self._warn(f"Non-literal first argument for st.{widget_type}; using default.",
                           call, f"st.{widget_type}(...)")

        for kw in call.keywords:
            if kw.arg is None:
                continue
            if kw.arg == "key":
                key_val = _literal(kw.value)
                if isinstance(key_val, str):
                    captured_key = key_val
                continue
            if kw.arg == "width":
                val = _literal(kw.value)
                if isinstance(val, bool):
                    continue
                if isinstance(val, int):
                    props["width"] = "custom"
                    props["custom_width"] = val
                elif isinstance(val, str):
                    props["width"] = val
                continue
            prop_name = _KWARG_ALIASES.get(kw.arg, kw.arg)
            if prop_name not in props:
                # Some widgets store a boolean "value" under a different prop
                # name (e.g. checkbox uses "checked" but codegen emits value=).
                if kw.arg == "value" and "checked" in props:
                    prop_name = "checked"
                else:
                    continue
            val = _literal(kw.value)
            if val is _UNRESOLVED:
                self._warn(f"Non-literal value for '{kw.arg}' on st.{widget_type}; using default.",
                           call, f"st.{widget_type}(...)")
                continue
            # options/default stored as comma-joined strings in some widgets.
            if isinstance(props.get(prop_name), str) and isinstance(val, (list, tuple)):
                val = ", ".join(str(v) for v in val)
            # label_visibility bool widgets accept 'visible'/'hidden'.
            if prop_name == "label_visibility" and isinstance(props.get(prop_name), bool):
                val = val == "visible"
            props[prop_name] = val
        return props, captured_key

    def _add_widget(self, widget_type: str, props: Dict[str, Any],
                    parent_id: Optional[str], column_index: Optional[int],
                    widget_id: Optional[str] = None) -> WidgetInstance:
        widget = WidgetInstance(
            id=widget_id or _new_id(),
            type=widget_type,
            props=props,
            parent_id=parent_id,
            column_index=column_index,
        )
        self.design.widgets.append(widget)
        return widget

    def _process_call(self, call: ast.Call, parent_id: Optional[str],
                      column_index: Optional[int]) -> None:
        fn = self._st_call_name(call)
        if fn is None:
            self._ignored("Non-Streamlit call ignored.", call, _call_summary(call))
            return
        if fn == "set_page_config":
            self._handle_set_page_config(call)
            return
        if fn == "markdown":
            if self._handle_markdown(call, parent_id):
                return
            # fall through: treat as a markdown content widget
        if fn == "form_submit_button":
            return  # auto-emitted inside forms; drop.
        if fn in ("columns", "tabs"):
            self._warn(f"st.{fn}(...) without assignment is not reconstructed.", call,
                       f"st.{fn}(...)")
            return

        reverse = self._reverse
        widget_type = reverse.get(fn)
        if widget_type is None:
            self._warn(f"Unsupported widget st.{fn}(...) skipped.", call, f"st.{fn}(...)")
            return
        props, key = self._call_to_props(call, widget_type)
        self._add_widget(widget_type, props, parent_id, column_index, widget_id=key)

    # -- columns / tabs assignments -----------------------------------------
    def _handle_columns_assign(self, var_name: str, call: ast.Call,
                               parent_id: Optional[str], column_index: Optional[int]) -> None:
        ratios: List[int] = []
        if call.args:
            arg0 = _literal(call.args[0])
            if isinstance(arg0, int):
                ratios = [1] * max(1, arg0)
            elif isinstance(arg0, (list, tuple)):
                for r in arg0:
                    try:
                        ratios.append(max(1, int(r)))
                    except (TypeError, ValueError):
                        ratios.append(1)
        if not ratios:
            ratios = [1, 1]
        container = self._add_widget(
            "columns_container",
            {"label": "Columns", "background_color": "#FFFFFF", "columns": len(ratios)},
            parent_id, column_index,
        )
        col_ids: List[str] = []
        for idx, ratio in enumerate(ratios):
            col = self._add_widget(
                "column",
                {"label": "Column", "background_color": "#FFFFFF", "ratio": ratio},
                container.id, idx,
            )
            col_ids.append(col.id)
        self._var_map[var_name] = ("columns", container.id, col_ids)

    def _handle_tabs_assign(self, var_name: str, call: ast.Call,
                            parent_id: Optional[str], column_index: Optional[int]) -> None:
        labels: List[str] = []
        if call.args:
            arg0 = _literal(call.args[0])
            if isinstance(arg0, (list, tuple)):
                labels = [str(x) for x in arg0]
        if not labels:
            labels = ["Tab 1", "Tab 2"]
        default = ""
        for kw in call.keywords:
            if kw.arg == "default":
                dv = _literal(kw.value)
                if isinstance(dv, str):
                    default = dv
        container = self._add_widget(
            "tabs",
            {"label": "Tabs", "tabs": len(labels), "width": "stretch",
             "custom_width": 320, "default": default},
            parent_id, column_index,
        )
        tab_ids: List[str] = []
        for label in labels:
            tab = self._add_widget("tab", {"label": label}, container.id, None)
            tab_ids.append(tab.id)
        self._var_map[var_name] = ("tabs", container.id, tab_ids)

    def _handle_assign(self, node: ast.Assign, parent_id: Optional[str],
                       column_index: Optional[int]) -> None:
        value = node.value
        fn = self._st_call_name(value)
        # Single simple target name (e.g. ``cols = ...``).
        target_name = None
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
        if fn == "columns" and target_name:
            self._handle_columns_assign(target_name, value, parent_id, column_index)
            return
        if fn == "tabs" and target_name:
            self._handle_tabs_assign(target_name, value, parent_id, column_index)
            return
        if fn is not None:
            # e.g. ``img = st.camera_input(...)`` -> treat as a widget.
            self._process_call(value, parent_id, column_index)
            return
        # Non-Streamlit assignment: ignore (record only top-level ones).
        if parent_id is None:
            self._ignored("Non-Streamlit assignment ignored.", node, "assignment")

    # -- with-statement handling --------------------------------------------
    def _resolve_subscript(self, node: ast.AST) -> Optional[Tuple[str, str, int]]:
        """For ``var[i]`` return (kind, child_id, index) or None."""
        if not isinstance(node, ast.Subscript) or not isinstance(node.value, ast.Name):
            return None
        var_name = node.value.id
        entry = self._var_map.get(var_name)
        if entry is None:
            return None
        kind, _container_id, child_ids = entry
        # Python 3.9+: slice is the index expression directly.
        idx_node = node.slice
        if isinstance(idx_node, ast.Index):  # pragma: no cover - old Python
            idx_node = idx_node.value  # type: ignore[attr-defined]
        idx = _literal(idx_node)
        if not isinstance(idx, int) or idx < 0 or idx >= len(child_ids):
            return None
        return kind, child_ids[idx], idx

    def _handle_with(self, node: ast.With, parent_id: Optional[str],
                     column_index: Optional[int]) -> None:
        if not node.items:
            return
        ctx = node.items[0].context_expr

        # ``with st.sidebar:`` (Attribute, not a Call)
        fn_attr = self._st_func_name(ctx)
        if fn_attr == "sidebar":
            sidebar = self._add_widget("sidebar", {"label": "Sidebar"}, parent_id, column_index)
            self._walk_body(node.body, sidebar.id, None)
            return

        # ``with cols[i]:`` / ``with tabs_1[i]:``
        resolved = self._resolve_subscript(ctx)
        if resolved is not None:
            kind, child_id, idx = resolved
            new_col_index = idx if kind == "columns" else None
            self._walk_body(node.body, child_id, new_col_index)
            return

        # ``with st.container(...):`` and friends
        fn = self._st_call_name(ctx)
        if fn in _CONTAINER_FUNCS and isinstance(ctx, ast.Call):
            # Styled-text widgets (markdown/title/header/subheader/caption/text/
            # divider/badge) are emitted by codegen as a keyed container wrapping
            # a single inner call, followed by a sibling <style> markdown. User
            # containers never emit a key, so a keyed container wrapping exactly
            # one generic widget call is collapsed back to that inner widget.
            if fn == "container" and self._try_collapse_style_wrapper(node, ctx, parent_id, column_index):
                return
            widget_type = _CONTAINER_FUNCS[fn]
            definition = get_widget(widget_type)
            props = dict(definition.defaults)
            # capture key (only some containers emit it; harmless otherwise)
            captured_key: Optional[str] = None
            for kw in ctx.keywords:
                if kw.arg == "key":
                    kv = _literal(kw.value)
                    if isinstance(kv, str):
                        captured_key = kv
            container = self._add_widget(widget_type, props, parent_id, column_index,
                                         widget_id=captured_key)
            self._walk_body(node.body, container.id, None)
            return

        self._warn("Unsupported 'with' block skipped.", node,
                   ast.dump(ctx)[:60] if ctx else "with ...")

    def _try_collapse_style_wrapper(self, node: ast.With, ctx: ast.Call,
                                    parent_id: Optional[str],
                                    column_index: Optional[int]) -> bool:
        """Collapse a codegen style-wrapper container into its inner widget.

        Returns True (consumed) when ``ctx`` is ``st.container(key=...)`` whose
        body is exactly one ``st.<fn>(...)`` call for a generic widget type.
        """
        has_key = any(kw.arg == "key" for kw in ctx.keywords)
        if not has_key:
            return False
        if len(node.body) != 1:
            return False
        stmt = node.body[0]
        if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
            return False
        inner_fn = self._st_call_name(stmt.value)
        if inner_fn is None or inner_fn in _CONTAINER_FUNCS:
            return False
        widget_type = self._reverse.get(inner_fn)
        if widget_type is None:
            return False
        # Reuse the container key as the reconstructed widget id (stable/unique).
        key_id: Optional[str] = None
        for kw in ctx.keywords:
            if kw.arg == "key":
                kv = _literal(kw.value)
                if isinstance(kv, str):
                    key_id = kv
        props, inner_key = self._call_to_props(stmt.value, widget_type)
        self._add_widget(widget_type, props, parent_id, column_index,
                         widget_id=inner_key or key_id)
        return True

    # -- main walk -----------------------------------------------------------
    def _walk_body(self, body: List[ast.stmt], parent_id: Optional[str],
                   column_index: Optional[int]) -> None:
        for node in body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                self._process_call(node.value, parent_id, column_index)
            elif isinstance(node, ast.Assign):
                self._handle_assign(node, parent_id, column_index)
            elif isinstance(node, ast.With):
                self._handle_with(node, parent_id, column_index)
            elif isinstance(node, ast.Pass):
                continue
            elif isinstance(node, (ast.For, ast.While, ast.If, ast.FunctionDef,
                                   ast.AsyncFunctionDef, ast.ClassDef, ast.Try)):
                self._warn(f"Dynamic construct '{type(node).__name__}' not imported.", node)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                # Module docstring / bare literal -> benign, ignore quietly.
                continue
            else:
                # Other statements (bare expressions, annotations, etc.).
                if parent_id is None:
                    self._ignored("Non-Streamlit statement ignored.", node,
                                  type(node).__name__)

    def run(self) -> ImportResult:
        if len(self.source) > _MAX_SOURCE_CHARS:
            return ImportResult(None, [ImportDiagnostic(
                "error", "File too large to import.")])
        try:
            tree = ast.parse(self.source)
        except SyntaxError as exc:
            return ImportResult(None, [ImportDiagnostic(
                "error", f"Syntax error: {exc.msg}", exc.lineno, exc.offset)])
        except (ValueError, RecursionError, MemoryError) as exc:
            return ImportResult(None, [ImportDiagnostic(
                "error", f"Could not parse file: {exc}")])

        has_import = self._scan_imports(tree)
        has_usage = self._has_st_usage(tree)
        if not has_import and not has_usage:
            return ImportResult(None, [ImportDiagnostic(
                "error", "This does not look like a Streamlit file "
                         "(no 'import streamlit' and no 'st.' calls).")])

        self._reverse = self._reverse_map()
        self._walk_body(tree.body, None, None)
        return ImportResult(self.design, self.diagnostics)


def import_design_from_code(source: str, *, design_name: str = "Imported") -> ImportResult:
    """Parse generated Streamlit code into a :class:`Design` (parse-only).

    Never executes the uploaded source. Returns an :class:`ImportResult` whose
    ``design`` is ``None`` on failure, with diagnostics describing why.
    """
    return _Importer(str(source or ""), design_name).run()
















