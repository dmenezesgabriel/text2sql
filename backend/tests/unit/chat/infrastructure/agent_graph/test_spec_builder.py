from __future__ import annotations

import datetime
import json
from decimal import Decimal

import pytest

from src.chat.infrastructure.agent_graph.spec_builder import (
    SpecBuildError,
    _chart_props,
    _dataset_id,
    _default_title,
    _format_kind,
    _format_number,
    _humanize,
    _number,
    _require_column,
    _table_title,
    _viz_props,
    build_spec,
    fallback_spec,
    json_default,
    narrative_spec,
)
from src.shared.domain.base import ResponseKind

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

    def test_datetime_becomes_iso_string(self) -> None:
        dt = datetime.datetime(2025, 6, 15, 12, 0, 0)
        result = json.loads(json.dumps({"d": dt}, default=json_default))
        assert result["d"] == dt.isoformat()

    def test_decimal_becomes_float(self) -> None:
        result = json.loads(json.dumps({"v": Decimal("1.5")}, default=json_default))
        assert result["v"] == pytest.approx(1.5)

    def test_decimal_zero_becomes_float(self) -> None:
        result = json.loads(json.dumps({"v": Decimal("0")}, default=json_default))
        assert result["v"] == 0.0

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

    def test_chart_empty_label_returns_empty_string(self) -> None:
        state = _state(viz_component="BarChart", label_column="", value_column="revenue")
        assert _default_title(state) == ""  # type: ignore[arg-type]

    def test_chart_empty_value_returns_empty_string(self) -> None:
        state = _state(viz_component="BarChart", label_column="region", value_column="")
        assert _default_title(state) == ""  # type: ignore[arg-type]

    def test_metric_uses_value_col_not_label_col(self) -> None:
        state = _state(viz_component="Metric", label_column="region", value_column="revenue")
        assert _default_title(state) == "Revenue"  # type: ignore[arg-type]


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

    def test_data_items_use_label_key(self) -> None:
        props = _chart_props(_state(), _RESULT)  # type: ignore[arg-type]
        assert props["data"][0]["label"] == "East"  # type: ignore[index]

    def test_data_items_use_value_key(self) -> None:
        props = _chart_props(_state(), _RESULT)  # type: ignore[arg-type]
        assert props["data"][0]["value"] == 100.0  # type: ignore[index]

    def test_has_data_key(self) -> None:
        props = _chart_props(_state(), _RESULT)  # type: ignore[arg-type]
        assert "data" in props

    def test_has_title_key(self) -> None:
        props = _chart_props(_state(), _RESULT)  # type: ignore[arg-type]
        assert "title" in props

    def test_xaxis_key_name(self) -> None:
        props = _chart_props(_state(), _RESULT)  # type: ignore[arg-type]
        assert "xAxis" in props

    def test_yaxis_key_name(self) -> None:
        props = _chart_props(_state(), _RESULT)  # type: ignore[arg-type]
        assert "yAxis" in props


class TestTableTitle:
    def test_two_column_result(self) -> None:
        state = _state()
        assert _table_title(state) == "Revenue by Region"  # type: ignore[arg-type]

    def test_single_column_returns_data_table(self) -> None:
        state = _state(sql_result={"columns": ["name"], "rows": []})
        assert _table_title(state) == "Data Table"  # type: ignore[arg-type]

    def test_no_result_returns_data_table(self) -> None:
        state = _state(sql_result=None)
        assert _table_title(state) == "Data Table"  # type: ignore[arg-type]


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

    def test_root_is_main(self) -> None:
        assert build_spec(_state())["root"] == "main"  # type: ignore[arg-type]

    def test_elements_has_main_key(self) -> None:
        assert "main" in build_spec(_state())["elements"]  # type: ignore[arg-type, operator]

    def test_meta_sql_matches_state(self) -> None:
        spec = build_spec(_state(sql="SELECT revenue FROM sales"))  # type: ignore[arg-type]
        assert spec["meta"]["sql"] == "SELECT revenue FROM sales"  # type: ignore[index]

    def test_meta_sql_is_empty_string_when_not_in_state(self) -> None:
        state = {k: v for k, v in _state().items() if k != "sql"}
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["meta"]["sql"] == ""  # type: ignore[index]

    def test_meta_dataset_id_from_views(self) -> None:
        state = _state(sql="SELECT * FROM ds_abc", dataset_views={"ds_abc": "uuid-999"})
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["meta"]["dataset_id"] == "uuid-999"  # type: ignore[index]

    def test_meta_format_is_chart_for_bar_chart(self) -> None:
        assert build_spec(_state())["meta"]["format"] == "CHART"  # type: ignore[arg-type, index]

    def test_meta_format_is_table_for_data_table(self) -> None:
        state = _state(viz_component="DataTable", label_column="", value_column="")
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["meta"]["format"] == "TABLE"  # type: ignore[index]

    def test_meta_format_is_text_for_narrative(self) -> None:
        state = _state(viz_component="NarrativeText", sql_result=None, narrative="hi")
        assert build_spec(state)["meta"]["format"] == "TEXT"  # type: ignore[arg-type, index]

    def test_meta_title_matches_props_title(self) -> None:
        result = {
            "columns": ["region", "total_revenue"],
            "rows": [{"region": "East", "total_revenue": 100}],
        }
        state = _state(label_column="region", value_column="total_revenue", sql_result=result)
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["meta"]["title"] == "Total Revenue by Region"  # type: ignore[index]

    def test_narrative_no_narrative_defaults_to_no_answer(self) -> None:
        state = _state(viz_component="NarrativeText", sql_result=None, narrative="")
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["elements"]["main"]["props"]["content"] == "No answer."  # type: ignore[index]


class TestNarrativeSpec:
    def test_wraps_text(self) -> None:
        spec = narrative_spec("hello")
        assert spec["elements"]["answer"]["props"]["content"] == "hello"  # type: ignore[index]

    def test_root_key_is_answer(self) -> None:
        assert narrative_spec("hi")["root"] == "answer"

    def test_elements_has_answer_key(self) -> None:
        assert "answer" in narrative_spec("hi")["elements"]  # type: ignore[operator]

    def test_element_type_is_narrative_text(self) -> None:
        assert narrative_spec("hi")["elements"]["answer"]["type"] == "NarrativeText"  # type: ignore[index]

    def test_content_key_in_props(self) -> None:
        assert "content" in narrative_spec("hi")["elements"]["answer"]["props"]  # type: ignore[index]


class TestFallbackSpec:
    def test_falls_back_to_data_table(self) -> None:
        spec = fallback_spec(_state())  # type: ignore[arg-type]
        assert spec["elements"]["main"]["type"] == "DataTable"  # type: ignore[index]

    def test_no_result_returns_narrative(self) -> None:
        spec = fallback_spec(_state(sql_result=None))  # type: ignore[arg-type]
        assert spec["elements"]["answer"]["type"] == "NarrativeText"  # type: ignore[index]

    def test_column_dicts_have_key_and_header(self) -> None:
        spec = fallback_spec(_state())  # type: ignore[arg-type]
        cols = spec["elements"]["main"]["props"]["columns"]  # type: ignore[index]
        assert cols[0]["key"] == "region"
        assert cols[0]["header"] == "region"

    def test_props_has_title_columns_rows(self) -> None:
        spec = fallback_spec(_state())  # type: ignore[arg-type]
        props = spec["elements"]["main"]["props"]  # type: ignore[index]
        assert "title" in props
        assert "columns" in props
        assert "rows" in props

    def test_rows_match_result(self) -> None:
        spec = fallback_spec(_state())  # type: ignore[arg-type]
        assert spec["elements"]["main"]["props"]["rows"] == _RESULT["rows"]  # type: ignore[index]


class TestDatasetId:
    def test_returns_dataset_id_when_view_in_sql(self) -> None:
        state = _state(sql="SELECT * FROM ds_abc", dataset_views={"ds_abc": "uuid-123"})
        assert _dataset_id(state) == "uuid-123"  # type: ignore[arg-type]

    def test_returns_empty_string_when_no_matching_view(self) -> None:
        state = _state(sql="SELECT 1", dataset_views={"ds_xyz": "uuid-456"})
        assert _dataset_id(state) == ""  # type: ignore[arg-type]

    def test_returns_empty_string_when_no_views(self) -> None:
        state = _state(sql="SELECT 1", dataset_views={})
        assert _dataset_id(state) == ""  # type: ignore[arg-type]

    def test_returns_empty_string_when_no_sql(self) -> None:
        state = _state(sql="", dataset_views={"ds_abc": "uuid-123"})
        assert _dataset_id(state) == ""  # type: ignore[arg-type]

    def test_returns_empty_when_dataset_views_key_absent(self) -> None:
        # Kills mutmut_11/13: views=None/no-default would crash on .items()
        state = {k: v for k, v in _state().items() if k != "dataset_views"}
        assert _dataset_id(state) == ""  # type: ignore[arg-type]


class TestFormatKind:
    def test_data_table_returns_table(self) -> None:
        assert _format_kind("DataTable") == ResponseKind.TABLE

    def test_narrative_text_returns_text(self) -> None:
        assert _format_kind("NarrativeText") == ResponseKind.TEXT

    def test_bar_chart_returns_chart(self) -> None:
        assert _format_kind("BarChart") == ResponseKind.CHART

    def test_line_chart_returns_chart(self) -> None:
        assert _format_kind("LineChart") == ResponseKind.CHART

    def test_pie_chart_returns_chart(self) -> None:
        assert _format_kind("PieChart") == ResponseKind.CHART


class TestVizProps:
    def test_data_table_has_title_columns_rows(self) -> None:
        state = _state(viz_component="DataTable")
        props = _viz_props(state, _RESULT)  # type: ignore[arg-type]
        assert "title" in props
        assert "columns" in props
        assert "rows" in props

    def test_data_table_column_dicts_have_key_and_header(self) -> None:
        state = _state(viz_component="DataTable")
        props = _viz_props(state, _RESULT)  # type: ignore[arg-type]
        assert props["columns"][0]["key"] == "region"  # type: ignore[index]
        assert props["columns"][0]["header"] == "region"  # type: ignore[index]

    def test_data_table_rows_match_result(self) -> None:
        state = _state(viz_component="DataTable")
        props = _viz_props(state, _RESULT)  # type: ignore[arg-type]
        assert props["rows"] == _RESULT["rows"]  # type: ignore[index]

    def test_metric_component_returns_label_and_value(self) -> None:
        # Kills mutmut_30/31/32 ("XXMetricXX"/"metric"/"METRIC" string mutations)
        state = _state(viz_component="Metric", value_column="revenue")
        props = _viz_props(state, _RESULT)  # type: ignore[arg-type]
        assert "label" in props
        assert "value" in props

    def test_metric_component_value_is_formatted(self) -> None:
        # Kills mutmut_33/34/35/36 (None state/result passed to _metric_props)
        state = _state(viz_component="Metric", value_column="revenue")
        props = _viz_props(state, _RESULT)  # type: ignore[arg-type]
        assert props["value"] == "100"  # type: ignore[index]

    def test_metric_component_label_is_humanized_column(self) -> None:
        state = _state(viz_component="Metric", value_column="revenue", label_column="region")
        props = _viz_props(state, _RESULT)  # type: ignore[arg-type]
        assert props["label"] == "Revenue"  # type: ignore[index]


class TestBuildSpecFallbackPath:
    """Tests covering build_spec when viz_component is absent or falsy.

    These kill mutmut_9/10/11/12 which mutate the fallback "NarrativeText" string.
    """

    def test_no_viz_component_key_returns_narrative_spec(self) -> None:
        state = {k: v for k, v in _state().items() if k != "viz_component"}
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["elements"]["main"]["type"] == "NarrativeText"  # type: ignore[index]

    def test_empty_viz_component_returns_narrative_spec(self) -> None:
        # Kills mutmut_10/11/12: "XXNarrativeTextXX" / "narrativetext" / "NARRATIVETEXT"
        state = _state(viz_component="")
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["elements"]["main"]["type"] == "NarrativeText"  # type: ignore[index]

    def test_empty_viz_component_does_not_raise(self) -> None:
        state = _state(viz_component="", narrative="hello")
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec is not None

    def test_no_sql_result_error_message_not_xx_wrapped(self) -> None:
        # Kills mutmut_43: "XXNo SQL result available.XX"
        with pytest.raises(SpecBuildError) as exc:
            build_spec(_state(sql_result=None))  # type: ignore[arg-type]
        assert "XX" not in str(exc.value)

    def test_no_sql_result_error_message_lowercase_no(self) -> None:
        with pytest.raises(SpecBuildError) as exc:
            build_spec(_state(sql_result=None))  # type: ignore[arg-type]
        assert str(exc.value).startswith("No ")

    def test_metric_spec_meta_title_is_empty_string(self) -> None:
        # Kills _spec mutmut_28/30/33: props.get("title", None/empty/"XXXX")
        # Metric props don't have "title" key, so default is used
        state = _state(viz_component="Metric", value_column="revenue")
        spec = build_spec(state)  # type: ignore[arg-type]
        assert spec["meta"]["title"] == ""  # type: ignore[index]

    def test_metric_spec_meta_title_is_not_xx(self) -> None:
        state = _state(viz_component="Metric", value_column="revenue")
        spec = build_spec(state)  # type: ignore[arg-type]
        assert "XX" not in spec["meta"]["title"]  # type: ignore[index]


class TestFallbackSpecContent:
    """Kill mutmut_6/7/8/9 (narrative text content) and mutmut_20 (title "XXXX")."""

    def test_no_result_narrative_content_exact(self) -> None:
        # Kills mutmut_6 (None), 7 (XX-wrapped), 8 (lowercase), 9 (uppercase)
        spec = fallback_spec(_state(sql_result=None))  # type: ignore[arg-type]
        content = spec["elements"]["answer"]["props"]["content"]  # type: ignore[index]
        assert content == "The query produced no result."

    def test_no_result_narrative_content_no_xx(self) -> None:
        spec = fallback_spec(_state(sql_result=None))  # type: ignore[arg-type]
        content = spec["elements"]["answer"]["props"]["content"]  # type: ignore[index]
        assert "XX" not in content

    def test_no_result_narrative_not_uppercase(self) -> None:
        spec = fallback_spec(_state(sql_result=None))  # type: ignore[arg-type]
        content = spec["elements"]["answer"]["props"]["content"]  # type: ignore[index]
        assert content[0] == "T"  # starts with capital T, not all-caps

    def test_fallback_title_is_empty_string(self) -> None:
        # Kills mutmut_20: title = "XXXX"
        spec = fallback_spec(_state())  # type: ignore[arg-type]
        assert spec["elements"]["main"]["props"]["title"] == ""  # type: ignore[index]

    def test_fallback_title_not_xx(self) -> None:
        spec = fallback_spec(_state())  # type: ignore[arg-type]
        assert "XX" not in spec["elements"]["main"]["props"]["title"]  # type: ignore[index]


class TestDefaultTitleMissingKeys:
    """Kill mutmut_16 and mutmut_24 (XXXX default for label_col and value_col)."""

    def test_chart_missing_label_col_returns_empty(self) -> None:
        # Kills mutmut_16: label_col = "XXXX" when key absent
        # With "XXXX" and value_col present → returns "Revenue by Xxxx" instead of ""
        state = {
            k: v
            for k, v in _state(viz_component="BarChart", value_column="revenue").items()
            if k != "label_column"
        }
        assert _default_title(state) == ""  # type: ignore[arg-type]

    def test_chart_missing_value_col_returns_empty(self) -> None:
        # Kills mutmut_24: value_col = "XXXX" when key absent
        # With "XXXX" and label_col present → returns "Xxxx by Region" instead of ""
        state = {
            k: v
            for k, v in _state(viz_component="BarChart", label_column="region").items()
            if k != "value_column"
        }
        assert _default_title(state) == ""  # type: ignore[arg-type]


class TestNumberErrorMessages:
    """Kill mutmut_1/2/6/7: msg=None passed to SpecBuildError."""

    def test_boolean_error_message_is_truthy(self) -> None:
        # Kills mutmut_1: msg=None → TypeError on bool False
        with pytest.raises(SpecBuildError) as exc:
            _number(True)
        assert str(exc.value)

    def test_boolean_error_contains_value(self) -> None:
        # Kills mutmut_2: raise SpecBuildError(None)
        with pytest.raises(SpecBuildError) as exc:
            _number(False)
        assert "False" in str(exc.value) or exc.value.args[0] is not None

    def test_non_numeric_error_message_is_truthy(self) -> None:
        # Kills mutmut_6: msg=None
        with pytest.raises(SpecBuildError) as exc:
            _number("abc")
        assert str(exc.value)

    def test_non_numeric_error_contains_value(self) -> None:
        # Kills mutmut_7: raise SpecBuildError(None)
        with pytest.raises(SpecBuildError) as exc:
            _number("notanumber")
        assert "notanumber" in str(exc.value) or exc.value.args[0] is not None


class TestJsonDefaultErrorMessage:
    """Kill mutmut_2/3/4: msg=None or type(None).__name__ instead of actual type name."""

    def test_error_message_is_truthy(self) -> None:
        # Kills mutmut_2/4: msg=None → TypeError(None)
        with pytest.raises(TypeError) as exc:
            json_default(object())
        assert str(exc.value)

    def test_error_message_contains_actual_type_name(self) -> None:
        # Kills mutmut_3: type(None).__name__ = "NoneType" instead of "object"
        class CustomType:
            pass

        with pytest.raises(TypeError) as exc:
            json_default(CustomType())
        assert "CustomType" in str(exc.value)

    def test_error_message_not_none_type(self) -> None:
        with pytest.raises(TypeError) as exc:
            json_default(42j)  # complex number
        assert "NoneType" not in str(exc.value)
