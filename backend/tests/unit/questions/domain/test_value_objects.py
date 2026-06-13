from __future__ import annotations

import pytest

from src.questions.domain.value_objects import QuestionTitle, SqlQuery, VizDecision, VizSpec
from src.shared.domain.base import ResponseKind


class TestQuestionTitle:
    def test_valid_title(self) -> None:
        title = QuestionTitle("Sales by Region")
        assert title.value == "Sales by Region"

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValueError):
            QuestionTitle("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError):
            QuestionTitle("   ")


class TestSqlQuery:
    def test_is_select_true(self) -> None:
        assert SqlQuery("SELECT 1").is_select()
        assert SqlQuery("select * from t").is_select()

    def test_is_select_false(self) -> None:
        assert not SqlQuery("DROP TABLE t").is_select()
        assert not SqlQuery("INSERT INTO t VALUES (1)").is_select()


class TestVizSpec:
    def test_fields_stored(self) -> None:
        spec = VizSpec(_component="BarChart", _props={"x": "col"}, _children=())
        assert spec._component == "BarChart"
        assert spec._props == {"x": "col"}


class TestVizDecision:
    def test_fields_stored(self) -> None:
        spec = VizSpec(_component="Table", _props={}, _children=())
        decision = VizDecision(_format=ResponseKind.TABLE, _spec=spec)
        assert decision._format == ResponseKind.TABLE
        assert decision._spec == spec
