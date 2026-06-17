from __future__ import annotations

from collections.abc import Callable

_METRIC_DIRECTIONS = ("up", "down", "neutral")
_NARRATIVE_TONES = ("analytical", "conversational", "executive")


def validate_spec(spec: dict[str, object]) -> None:
    """Raise ValueError if `spec` violates the frontend json-render catalog shape.

    Mirrors frontend/src/widgets/json-render/catalog.ts component-by-component —
    the last check before a payload reaches the React/Lit renderer.
    """
    elements = spec.get("elements")
    if not isinstance(elements, dict):
        msg = f"spec.elements must be a dict, got {elements!r}"
        raise ValueError(msg)
    for element_id, element in elements.items():
        _validate_element(element_id, element)


def _validate_element(element_id: str, element: object) -> None:
    if not isinstance(element, dict):
        msg = f"element {element_id!r} must be a dict, got {element!r}"
        raise ValueError(msg)
    element_type = element.get("type")
    if not isinstance(element_type, str) or element_type not in _VALIDATORS:
        msg = f"element {element_id!r} has unknown type {element_type!r}"
        raise ValueError(msg)
    props = element.get("props")
    if not isinstance(props, dict):
        msg = f"element {element_id!r} props must be a dict, got {props!r}"
        raise ValueError(msg)
    _VALIDATORS[element_type](element_id, props)


def _require_str(element_id: str, props: dict[str, object], key: str) -> None:
    value = props.get(key)
    if not isinstance(value, str):
        msg = f"element {element_id!r} props.{key} must be a str, got {value!r}"
        raise ValueError(msg)


def _require_optional_str(element_id: str, props: dict[str, object], key: str) -> None:
    if props.get(key) is not None:
        _require_str(element_id, props, key)


def _require_chart_data(element_id: str, props: dict[str, object]) -> None:
    data = props.get("data")
    if not isinstance(data, list):
        msg = f"element {element_id!r} props.data must be a list, got {data!r}"
        raise ValueError(msg)
    for point in data:
        valid = (
            isinstance(point, dict)
            and isinstance(point.get("label"), str)
            and isinstance(point.get("value"), (int, float))
            and not isinstance(point.get("value"), bool)
        )
        if not valid:
            msg = (
                f"element {element_id!r} props.data point {point!r}"
                " must be {label: str, value: number}"
            )
            raise ValueError(msg)


def _validate_bar_or_line(element_id: str, props: dict[str, object]) -> None:
    _require_str(element_id, props, "title")
    _require_str(element_id, props, "xAxis")
    _require_str(element_id, props, "yAxis")
    _require_chart_data(element_id, props)
    _require_optional_str(element_id, props, "color")


def _validate_pie(element_id: str, props: dict[str, object]) -> None:
    _require_str(element_id, props, "title")
    _require_chart_data(element_id, props)


def _validate_metric(element_id: str, props: dict[str, object]) -> None:
    _require_str(element_id, props, "label")
    _require_str(element_id, props, "value")
    _require_optional_str(element_id, props, "change")
    direction = props.get("direction")
    if direction is not None and direction not in _METRIC_DIRECTIONS:
        msg = (
            f"element {element_id!r} props.direction"
            f" must be one of {_METRIC_DIRECTIONS}, got {direction!r}"
        )
        raise ValueError(msg)


def _validate_data_table(element_id: str, props: dict[str, object]) -> None:
    _require_optional_str(element_id, props, "title")
    columns = props.get("columns")
    if not isinstance(columns, list):
        msg = f"element {element_id!r} props.columns must be a list, got {columns!r}"
        raise ValueError(msg)
    for column in columns:
        valid = (
            isinstance(column, dict)
            and isinstance(column.get("key"), str)
            and isinstance(column.get("header"), str)
        )
        if not valid:
            msg = (
                f"element {element_id!r} props.columns entry {column!r}"
                " must be {key: str, header: str}"
            )
            raise ValueError(msg)
    rows = props.get("rows")
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        msg = f"element {element_id!r} props.rows must be a list of dicts, got {rows!r}"
        raise ValueError(msg)


def _validate_narrative(element_id: str, props: dict[str, object]) -> None:
    _require_str(element_id, props, "content")
    tone = props.get("tone")
    if tone is not None and tone not in _NARRATIVE_TONES:
        msg = f"element {element_id!r} props.tone must be one of {_NARRATIVE_TONES}, got {tone!r}"
        raise ValueError(msg)


_VALIDATORS: dict[str, Callable[[str, dict[str, object]], None]] = {
    "BarChart": _validate_bar_or_line,
    "LineChart": _validate_bar_or_line,
    "PieChart": _validate_pie,
    "Metric": _validate_metric,
    "DataTable": _validate_data_table,
    "NarrativeText": _validate_narrative,
}
