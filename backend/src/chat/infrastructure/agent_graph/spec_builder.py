from __future__ import annotations

import datetime
import json
import re
from decimal import Decimal
from typing import Any

from src.chat.infrastructure.agent_graph.agent_state import AgentState
from src.shared.domain.base import ResponseKind

_CHART_COMPONENTS = ("BarChart", "LineChart", "PieChart")
_VALID_COMPONENTS = (*_CHART_COMPONENTS, "DataTable", "Metric", "NarrativeText")


class SpecBuildError(Exception):
    """Raised when a visualization cannot be built from the current result."""


def build_spec(state: AgentState) -> dict[str, Any]:
    """Build a json-render spec from the current graph state.

    Example: build_spec(state) → {"root": "main", "elements": {...}, "meta": {...}}
    """
    component = state.get("viz_component", "") or "NarrativeText"
    if component not in _VALID_COMPONENTS:
        msg = f"Unknown component {component!r}. Valid: {list(_VALID_COMPONENTS)}."
        raise SpecBuildError(msg)
    if component == "NarrativeText":
        props: dict[str, Any] = {"content": state.get("narrative") or "No answer."}
        return _spec(state, component, props)
    result = state.get("sql_result")
    if result is None:
        msg = "No SQL result available."
        raise SpecBuildError(msg)
    return _spec(state, component, _viz_props(state, result))


def fallback_spec(state: AgentState) -> dict[str, Any]:
    """Build a DataTable spec from whatever SQL result is available."""
    result = state.get("sql_result")
    if result is None:
        return narrative_spec("The query produced no result.")
    columns = [{"key": c, "header": c} for c in result["columns"]]
    props: dict[str, Any] = {"title": "", "columns": columns, "rows": result["rows"]}
    return _spec(state, "DataTable", props)


def narrative_spec(text: str) -> dict[str, Any]:
    return {
        "root": "answer",
        "elements": {"answer": {"type": "NarrativeText", "props": {"content": text}}},
    }


def _viz_props(state: AgentState, result: dict[str, Any]) -> dict[str, Any]:
    component = state.get("viz_component", "")
    if component == "DataTable":
        columns = [{"key": c, "header": c} for c in result["columns"]]
        return {"title": _default_title(state), "columns": columns, "rows": result["rows"]}
    if component == "Metric":
        return _metric_props(state, result)
    return _chart_props(state, result)


def _metric_props(state: AgentState, result: dict[str, Any]) -> dict[str, Any]:
    col = state.get("value_column", "")
    _require_column(col, result)
    first_row = result["rows"][0] if result["rows"] else {}
    value = _number(first_row.get(col, 0))
    return {"label": _default_title(state) or col, "value": _format_number(value)}


def _chart_props(state: AgentState, result: dict[str, Any]) -> dict[str, Any]:
    label_col = state.get("label_column", "")
    value_col = state.get("value_column", "")
    _require_column(label_col, result)
    _require_column(value_col, result)
    data = [{"label": str(r[label_col]), "value": _number(r[value_col])} for r in result["rows"]]
    props: dict[str, Any] = {"title": _default_title(state), "data": data}
    if state.get("viz_component") != "PieChart":
        props["xAxis"] = label_col
        props["yAxis"] = value_col
    return props


def _require_column(column: str, result: dict[str, Any]) -> None:
    if column in result["columns"]:
        return
    msg = f"Column {column!r} not in result. Available: {result['columns']}."
    raise SpecBuildError(msg)


def _number(value: object) -> float:
    if isinstance(value, bool):
        msg = f"Expected a numeric value, got boolean {value!r}."
        raise SpecBuildError(msg)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError as exc:
        msg = f"Value {value!r} is not numeric; pick a numeric value_column."
        raise SpecBuildError(msg) from exc


def _format_number(value: float) -> str:
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.2f}"


def _table_title(state: AgentState) -> str:
    result = state.get("sql_result") or {}
    cols: list[str] = result.get("columns", [])
    return f"{_humanize(cols[1])} by {_humanize(cols[0])}" if len(cols) >= 2 else "Data Table"


def _default_title(state: AgentState) -> str:
    component = state.get("viz_component", "")
    label_col = state.get("label_column", "")
    value_col = state.get("value_column", "")
    if component == "Metric":
        return _humanize(value_col)
    if component in _CHART_COMPONENTS and label_col and value_col:
        return f"{_humanize(value_col)} by {_humanize(label_col)}"
    return _table_title(state) if component == "DataTable" else ""


def _humanize(column: str) -> str:
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", column).replace("_", " ")
    return " ".join(spaced.split()).title()


def _spec(state: AgentState, component: str, props: dict[str, Any]) -> dict[str, Any]:
    sql = state.get("sql", "")
    dataset_id = _dataset_id(state)
    return {
        "root": "main",
        "elements": {"main": {"type": component, "props": props}},
        "meta": {
            "title": props.get("title", ""),
            "sql": sql,
            "dataset_id": dataset_id,
            "format": _format_kind(component).name,
        },
    }


def _dataset_id(state: AgentState) -> str:
    sql = state.get("sql", "")
    views = state.get("dataset_views", {})
    return next((dataset_id for view, dataset_id in views.items() if view in sql), "")


def _format_kind(component: str) -> ResponseKind:
    if component == "DataTable":
        return ResponseKind.TABLE
    if component == "NarrativeText":
        return ResponseKind.TEXT
    return ResponseKind.CHART


def json_default(obj: object) -> object:
    """Serialize DuckDB native types that json.dumps can't handle by default."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    msg = f"Object of type {type(obj).__name__} is not JSON serializable"
    raise TypeError(msg)


def result_summary(result: dict[str, Any]) -> str:
    """Human-readable summary of a SQL result for prompt context."""
    columns = result.get("columns", [])
    rows = result.get("rows", [])
    return f"Columns: {columns}\nRow count: {len(rows)}\nFirst row: {rows[0] if rows else 'none'}"


def rows_as_json(result: dict[str, Any], limit: int = 50) -> str:
    return json.dumps(
        {"columns": result["columns"], "rows": result["rows"][:limit]},
        default=json_default,
    )
