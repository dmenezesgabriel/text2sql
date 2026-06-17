from __future__ import annotations

import datetime
import json
from decimal import Decimal

import pytest

from src.chat.infrastructure.agent_graph.spec_builder import (
    SpecBuildError,
    _chart_props,
    _default_title,
    _format_number,
    _humanize,
    _number,
    _require_column,
    build_spec,
    fallback_spec,
    json_default,
    narrative_spec,
)

_RESULT = {
    "columns": ["region", "revenue"],
    "rows": [{"region": "East", "revenue": 100}, {"region": "West", "revenue": 80}],
}


def _state(**overrides: object) -> dict[str, object]:
    defaults: dict[str, object] = {
        "viz_component": "BarChart",
        "label_column": "region",
        "value_column": "revenue",
        "narrative": "",
        "sql": "SELECT 1",
        "sql_result": _RESULT,
        "dataset_views": {"ds_abc": "id-123"},
    }
    return {**defaults, **overrides}


class TestJsonDefault:
    def test_date_becomes_iso_string(self) -> None:
        result = json.loads(json.dumps({"d": datetime.date(2025, 1, 1)}, default=json_default))
        assert result["d"] == "2025-01-01"

    def test_decimal_becomes_float(self) -> None:
        result = json.loads(json.dumps({"v": Decimal("1.5")}, default=json_default))
        assert result["v"] == pytest.approx(1.5)

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(TypeError):
            json.dumps({"x": object()}, default=json_default)


class TestNumberCoercion:
    def test_accepts_int(self) -> None:
        assert _number(7) == 7.0

    def test_accepts_numeric_string(self) -> None:
        assert _number("3.5") == 3.5

    def test_rejects_boolean(self) -> None:
        with pytest.raises(SpecBuildError):
            _number(True)

    def test_rejects_non_numeric_string(self) -> None:
        with pytest.raises(SpecBuildError):
            _number("east")


class TestFormatNumber:
    def test_integer(self) -> None:
        assert _format_number(12000.0) == "12,000"

    def test_decimal(self) -> None:
        assert _format_number(1234.5) == "1,234.50"


class TestRequireColumn:
    def test_passes_when_present(self) -> None:
        _require_column("region", _RESULT)

    def test_raises_when_missing(self) -> None:
        with pytest.raises(SpecBuildError, match="region"):
            _require_column("missing", _RESULT)


class TestHumanize:
    def test_snake_case(self) -> None:
        assert _humanize("total_revenue") == "Total Revenue"

    def test_camel_case(self) -> None:
        assert _humanize("totalRevenue") == "Total Revenue"


class TestDefaultTitle:
    def test_chart_title(self) -> None:
        state = _state(label_column="region", value_column="total_revenue")
        assert _default_title(state) == "Total Revenue by Region"  # type: ignore[arg-type]

    def test_metric_title(self) -> None:
        state = _state(viz_component="Metric", value_column="row_count")
        assert _default_title(state) == "Row Count"  # type: ignore[arg-type]

    def test_data_table_title_from_columns(self) -> None:
        state = _state(viz_component="DataTable", label_column="", value_column="")
        assert _default_title(state) == "Revenue by Region"  # type: ignore[arg-type]

    def test_data_table_title_fallback_one_column(self) -> None:
        state = _state(viz_component="DataTable", sql_result={"columns": ["name"], "rows": []})
        assert _default_title(state) == "Data Table"  # type: ignore[arg-type]


class TestChartProps:
    def test_bar_chart_includes_axes(self) -> None:
        props = _chart_props(_state(), _RESULT)  # type: ignore[arg-type]
        assert props["xAxis"] == "region"
        assert props["yAxis"] == "revenue"
        assert props["data"] == [
            {"label": "East", "value": 100.0},
            {"label": "West", "value": 80.0},
        ]

    def test_pie_chart_omits_axes(self) -> None:
        props = _chart_props(_state(viz_component="PieChart"), _RESULT)  # type: ignore[arg-type]
        assert "xAxis" not in props
        assert "yAxis" not in props


class TestBuildSpec:
    def test_bar_chart_has_meta(self) -> None:
        spec = build_spec(_state())  # type: ignore[arg-type]
        assert spec["root"] == "main"
        assert spec["meta"]["format"] == "CHART"  # type: ignore[index]

    def test_narrative_needs_no_result(self) -> None:
        state = _state(viz_component="NarrativeText", sql_result=None, narrative="hi")
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["elements"]["main"]["props"]["content"] == "hi"  # type: ignore[index]

    def test_unknown_component_raises(self) -> None:
        with pytest.raises(SpecBuildError, match="Unknown"):
            build_spec(_state(viz_component="ScatterPlot"))  # type: ignore[arg-type]

    def test_chart_without_result_raises(self) -> None:
        with pytest.raises(SpecBuildError, match="No SQL result"):
            build_spec(_state(sql_result=None))  # type: ignore[arg-type]


class TestNarrativeSpec:
    def test_wraps_text(self) -> None:
        spec = narrative_spec("hello")
        assert spec["elements"]["answer"]["props"]["content"] == "hello"  # type: ignore[index]


class TestFallbackSpec:
    def test_falls_back_to_data_table(self) -> None:
        spec = fallback_spec(_state())  # type: ignore[arg-type]
        assert spec["elements"]["main"]["type"] == "DataTable"  # type: ignore[index]

    def test_no_result_returns_narrative(self) -> None:
        spec = fallback_spec(_state(sql_result=None))  # type: ignore[arg-type]
        assert spec["elements"]["answer"]["type"] == "NarrativeText"  # type: ignore[index]
