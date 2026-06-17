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
