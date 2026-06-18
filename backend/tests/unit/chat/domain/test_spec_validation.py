from __future__ import annotations

import pytest

from src.chat.domain.spec_validation import validate_spec


class TestValidSpecsPassWithoutRaising:
    def test_bar_chart_valid(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "BarChart",
                        "props": {
                            "title": "Sales",
                            "xAxis": "region",
                            "yAxis": "revenue",
                            "data": [{"label": "East", "value": 100.0}],
                        },
                    },
                },
            },
        )

    def test_line_chart_with_optional_color(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "LineChart",
                        "props": {
                            "title": "Trend",
                            "xAxis": "month",
                            "yAxis": "sales",
                            "data": [{"label": "Jan", "value": 500.0}],
                            "color": "#ff0000",
                        },
                    },
                },
            },
        )

    def test_pie_chart_valid(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "PieChart",
                        "props": {
                            "title": "Share",
                            "data": [{"label": "A", "value": 1.0}, {"label": "B", "value": 2.0}],
                        },
                    },
                },
            },
        )

    def test_metric_with_optional_fields(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "Metric",
                        "props": {
                            "label": "Revenue",
                            "value": "10,000",
                            "change": "+5%",
                            "direction": "up",
                        },
                    },
                },
            },
        )

    def test_metric_minimal(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "Metric",
                        "props": {"label": "Revenue", "value": "10,000"},
                    },
                },
            },
        )

    def test_data_table_valid(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "DataTable",
                        "props": {
                            "columns": [{"key": "region", "header": "Region"}],
                            "rows": [{"region": "East"}],
                        },
                    },
                },
            },
        )

    def test_data_table_with_optional_title_and_format(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "DataTable",
                        "props": {
                            "title": "My Table",
                            "columns": [{"key": "amt", "header": "Amount", "format": "currency"}],
                            "rows": [],
                        },
                    },
                },
            },
        )

    def test_narrative_text_valid(self) -> None:
        validate_spec(
            {
                "root": "answer",
                "elements": {
                    "answer": {
                        "type": "NarrativeText",
                        "props": {"content": "Here is the summary."},
                    },
                },
            },
        )

    def test_narrative_text_with_tone(self) -> None:
        validate_spec(
            {
                "root": "answer",
                "elements": {
                    "answer": {
                        "type": "NarrativeText",
                        "props": {"content": "Summary.", "tone": "executive"},
                    },
                },
            },
        )

    def test_empty_elements_dict_is_valid(self) -> None:
        validate_spec({"root": "main", "elements": {}})


class TestInvalidSpecsRaiseValueError:
    def test_elements_not_a_dict_raises(self) -> None:
        with pytest.raises(ValueError, match="elements"):
            validate_spec({"root": "main", "elements": "bad"})

    def test_unknown_component_type_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown type"):
            validate_spec(
                {"root": "main", "elements": {"e": {"type": "ScatterPlot", "props": {}}}},
            )

    def test_missing_type_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown type"):
            validate_spec({"root": "main", "elements": {"e": {"props": {}}}})

    def test_bar_chart_missing_title_raises(self) -> None:
        with pytest.raises(ValueError, match="title"):
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "BarChart",
                            "props": {
                                "xAxis": "region",
                                "yAxis": "revenue",
                                "data": [{"label": "East", "value": 100.0}],
                            },
                        },
                    },
                },
            )

    def test_bar_chart_data_point_missing_value_raises(self) -> None:
        with pytest.raises(ValueError, match="data point"):
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "BarChart",
                            "props": {
                                "title": "T",
                                "xAxis": "r",
                                "yAxis": "v",
                                "data": [{"label": "East"}],
                            },
                        },
                    },
                },
            )

    def test_bar_chart_data_not_a_list_raises(self) -> None:
        with pytest.raises(ValueError, match="data"):
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "BarChart",
                            "props": {
                                "title": "T",
                                "xAxis": "r",
                                "yAxis": "v",
                                "data": "not-a-list",
                            },
                        },
                    },
                },
            )

    def test_metric_invalid_direction_enum_raises(self) -> None:
        with pytest.raises(ValueError, match="direction"):
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "Metric",
                            "props": {"label": "Rev", "value": "100", "direction": "sideways"},
                        },
                    },
                },
            )

    def test_narrative_invalid_tone_enum_raises(self) -> None:
        with pytest.raises(ValueError, match="tone"):
            validate_spec(
                {
                    "root": "answer",
                    "elements": {
                        "answer": {
                            "type": "NarrativeText",
                            "props": {"content": "hi", "tone": "angry"},
                        },
                    },
                },
            )

    def test_data_table_columns_entry_missing_key_raises(self) -> None:
        with pytest.raises(ValueError, match="columns entry"):
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "DataTable",
                            "props": {
                                "columns": [{"header": "Region"}],
                                "rows": [],
                            },
                        },
                    },
                },
            )

    def test_data_table_rows_not_list_raises(self) -> None:
        with pytest.raises(ValueError, match="rows"):
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "DataTable",
                            "props": {
                                "columns": [{"key": "r", "header": "R"}],
                                "rows": "bad",
                            },
                        },
                    },
                },
            )

    def test_props_not_a_dict_raises(self) -> None:
        with pytest.raises(ValueError, match="props"):
            validate_spec(
                {"root": "main", "elements": {"main": {"type": "NarrativeText", "props": "bad"}}},
            )


class TestElementIdInErrorMessages:
    """Kills mutants that pass None instead of element_id to internal validators."""

    def test_non_dict_element_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec({"root": "my_tile", "elements": {"my_tile": "not_a_dict"}})
        assert "my_tile" in str(exc.value)

    def test_unknown_type_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {"root": "tile_x", "elements": {"tile_x": {"type": "ScatterPlot", "props": {}}}},
            )
        assert "tile_x" in str(exc.value)

    def test_bar_chart_missing_title_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "chart_el",
                    "elements": {
                        "chart_el": {
                            "type": "BarChart",
                            "props": {"xAxis": "x", "yAxis": "y", "data": []},
                        },
                    },
                },
            )
        assert "chart_el" in str(exc.value)

    def test_pie_missing_title_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "pie_el",
                    "elements": {
                        "pie_el": {
                            "type": "PieChart",
                            "props": {"data": [{"label": "A", "value": 1.0}]},
                        },
                    },
                },
            )
        assert "pie_el" in str(exc.value)

    def test_metric_missing_label_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "metric_el",
                    "elements": {
                        "metric_el": {"type": "Metric", "props": {"value": "100"}},
                    },
                },
            )
        assert "metric_el" in str(exc.value)

    def test_metric_missing_value_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "metric_el",
                    "elements": {
                        "metric_el": {"type": "Metric", "props": {"label": "Revenue"}},
                    },
                },
            )
        assert "metric_el" in str(exc.value)

    def test_narrative_missing_content_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "narr_el",
                    "elements": {"narr_el": {"type": "NarrativeText", "props": {}}},
                },
            )
        assert "narr_el" in str(exc.value)

    def test_data_table_non_list_columns_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "tbl_el",
                    "elements": {
                        "tbl_el": {
                            "type": "DataTable",
                            "props": {"columns": "not_a_list", "rows": []},
                        },
                    },
                },
            )
        assert "tbl_el" in str(exc.value)

    def test_data_table_non_list_rows_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "tbl_el",
                    "elements": {
                        "tbl_el": {
                            "type": "DataTable",
                            "props": {"columns": [], "rows": "not_a_list"},
                        },
                    },
                },
            )
        assert "tbl_el" in str(exc.value)

    def test_data_table_rows_list_of_non_dicts_error_contains_element_id(self) -> None:
        # Kills mutant: `not isinstance(rows, list) and not all(...)` vs `or`
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "tbl_el",
                    "elements": {
                        "tbl_el": {
                            "type": "DataTable",
                            "props": {"columns": [], "rows": [1, 2, 3]},
                        },
                    },
                },
            )
        assert "tbl_el" in str(exc.value)


class TestOptionalKeyValidation:
    """Kills mutants that use wrong key names (XXcolorXX, CHANGE, etc.) in _require_optional_str."""

    def test_color_key_validated_as_string_in_bar_chart(self) -> None:
        # "color" recognized — passes if string, fails if non-string
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "BarChart",
                            "props": {
                                "title": "T",
                                "xAxis": "x",
                                "yAxis": "y",
                                "data": [],
                                "color": 123,
                            },
                        },
                    },
                },
            )
        assert "color" in str(exc.value)

    def test_color_key_valid_when_string(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "LineChart",
                        "props": {
                            "title": "T",
                            "xAxis": "x",
                            "yAxis": "y",
                            "data": [{"label": "A", "value": 1.0}],
                            "color": "#00ff00",
                        },
                    },
                },
            },
        )

    def test_change_key_validated_as_string_in_metric(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "Metric",
                            "props": {"label": "L", "value": "100", "change": 5},
                        },
                    },
                },
            )
        assert "change" in str(exc.value)

    def test_change_key_valid_when_string(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "Metric",
                        "props": {"label": "L", "value": "100", "change": "+5%"},
                    },
                },
            },
        )

    def test_data_table_title_validated_as_string_when_present(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "DataTable",
                            "props": {
                                "title": 123,
                                "columns": [{"key": "a", "header": "A"}],
                                "rows": [{"a": 1}],
                            },
                        },
                    },
                },
            )
        assert "title" in str(exc.value)

    def test_data_table_title_valid_when_string(self) -> None:
        validate_spec(
            {
                "root": "main",
                "elements": {
                    "main": {
                        "type": "DataTable",
                        "props": {
                            "title": "My Table",
                            "columns": [{"key": "a", "header": "A"}],
                            "rows": [{"a": 1}],
                        },
                    },
                },
            },
        )


class TestElementIdInValidatorCalls:
    """Kills mutants that pass None instead of element_id to sub-validators."""

    def test_bar_chart_missing_xaxis_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "BarChart",
                            "props": {"title": "T", "xAxis": 0, "yAxis": "y", "data": []},
                        },
                    },
                },
            )
        assert "'e'" in str(exc.value)

    def test_bar_chart_missing_yaxis_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "BarChart",
                            "props": {"title": "T", "xAxis": "x", "yAxis": 0, "data": []},
                        },
                    },
                },
            )
        assert "'e'" in str(exc.value)

    def test_bar_chart_invalid_data_point_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "BarChart",
                            "props": {
                                "title": "T",
                                "xAxis": "x",
                                "yAxis": "y",
                                "data": [{"bad": 1}],
                            },
                        },
                    },
                },
            )
        assert "'e'" in str(exc.value)

    def test_pie_invalid_data_point_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "PieChart",
                            "props": {"title": "T", "data": [{"bad": 1}]},
                        },
                    },
                },
            )
        assert "'e'" in str(exc.value)

    def test_bar_chart_invalid_color_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "BarChart",
                            "props": {
                                "title": "T",
                                "xAxis": "x",
                                "yAxis": "y",
                                "data": [],
                                "color": 123,
                            },
                        },
                    },
                },
            )
        assert "'e'" in str(exc.value)

    def test_metric_invalid_change_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "Metric",
                            "props": {"label": "L", "value": "100", "change": 5},
                        },
                    },
                },
            )
        assert "'e'" in str(exc.value)

    def test_data_table_non_str_title_error_contains_element_id(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "DataTable",
                            "props": {"title": 999, "columns": [], "rows": []},
                        },
                    },
                },
            )
        assert "'e'" in str(exc.value)


class TestErrorMessageText:
    """Kills mutants that change error message strings to uppercase/XX-wrapped variants."""

    def test_chart_data_point_error_mentions_label_and_value(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "BarChart",
                            "props": {
                                "title": "T",
                                "xAxis": "x",
                                "yAxis": "y",
                                "data": [{"wrong_key": 1}],
                            },
                        },
                    },
                },
            )
        msg = str(exc.value)
        assert "label" in msg.lower()
        assert "value" in msg.lower()

    def test_chart_data_point_error_lowercase_must_be(self) -> None:
        # Kills mutmut_16: " MUST BE {LABEL...}" — uppercase doesn't match
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "BarChart",
                            "props": {
                                "title": "T",
                                "xAxis": "x",
                                "yAxis": "y",
                                "data": [{"wrong": 1}],
                            },
                        },
                    },
                },
            )
        assert " must be " in str(exc.value)

    def test_chart_data_point_error_no_xx_markers(self) -> None:
        # Kills mutmut_15: "XX must be {label...}XX" — XX not in legitimate message
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "BarChart",
                            "props": {
                                "title": "T",
                                "xAxis": "x",
                                "yAxis": "y",
                                "data": [{"wrong": 1}],
                            },
                        },
                    },
                },
            )
        assert "XX" not in str(exc.value)

    def test_data_table_column_error_lowercase_must_be(self) -> None:
        # Kills mutmut_22: " MUST BE {KEY: STR...}" — uppercase doesn't match
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "DataTable",
                            "props": {"columns": [{"wrong": "x"}], "rows": []},
                        },
                    },
                },
            )
        assert " must be " in str(exc.value)

    def test_data_table_column_error_no_xx_markers(self) -> None:
        # Kills mutmut_21: "XX must be {key...}XX"
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "e",
                    "elements": {
                        "e": {
                            "type": "DataTable",
                            "props": {"columns": [{"wrong": "x"}], "rows": []},
                        },
                    },
                },
            )
        assert "XX" not in str(exc.value)

    def test_data_table_column_error_mentions_key_and_header(self) -> None:
        with pytest.raises(ValueError) as exc:
            validate_spec(
                {
                    "root": "main",
                    "elements": {
                        "main": {
                            "type": "DataTable",
                            "props": {
                                "columns": [{"wrong": "x"}],
                                "rows": [],
                            },
                        },
                    },
                },
            )
        msg = str(exc.value)
        assert "key" in msg.lower()
        assert "header" in msg.lower()
