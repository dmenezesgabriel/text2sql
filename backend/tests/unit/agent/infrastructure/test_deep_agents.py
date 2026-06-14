from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.agent.domain.entities import Conversation, Message, MessageBody, MessageIdentity, Messages
from src.agent.domain.value_objects import (
    AgentEvent,
    ErrorEvent,
    MessageContent,
    MessageRole,
    SpecFragmentEvent,
    ToolCallEvent,
    ToolName,
)
from src.agent.infrastructure.deep_agents import (
    DeepAgentsOrchestrator,
    _BuildError,
    _chart_props,
    _default_title,
    _format_kind,
    _format_number,
    _narrative_spec,
    _number,
    _require_column,
    _RunState,
    _schema_context,
    _spec_from_result,
    _to_event,
    _viz_props,
    _VizRequest,
)
from src.shared.domain.base import CreatedAt, EntityId, QueryResult, ResponseKind

_RESULT = QueryResult(
    _columns=("region", "revenue"),
    _rows=({"region": "East", "revenue": 100}, {"region": "West", "revenue": 80}),
)


def _state(result: QueryResult | None = _RESULT, sql: str = "SELECT 1") -> _RunState:
    state = _RunState({"ds_abc": "11111111-1111-1111-1111-111111111111"})
    if result is not None:
        state.record(sql, result)
    return state


def _request(
    component: str,
    title: str = "Sales",
    label_column: str = "region",
    value_column: str = "revenue",
    content: str = "",
) -> _VizRequest:
    return _VizRequest(component, title, label_column, value_column, content)


class TestNumberCoercion:
    def test_accepts_int(self) -> None:
        assert _number(7) == 7.0

    def test_accepts_numeric_string(self) -> None:
        assert _number("3.5") == 3.5

    def test_rejects_boolean(self) -> None:
        with pytest.raises(_BuildError):
            _number(True)

    def test_rejects_non_numeric_string(self) -> None:
        with pytest.raises(_BuildError):
            _number("east")


class TestFormatNumber:
    def test_integers_have_no_decimals(self) -> None:
        assert _format_number(12000.0) == "12,000"

    def test_decimals_keep_two_places(self) -> None:
        assert _format_number(1234.5) == "1,234.50"


class TestRequireColumn:
    def test_passes_when_present(self) -> None:
        _require_column("region", _RESULT)

    def test_raises_with_available_columns(self) -> None:
        with pytest.raises(_BuildError, match="region"):
            _require_column("missing", _RESULT)


class TestChartProps:
    def test_bar_chart_includes_axes_and_data(self) -> None:
        props = _chart_props(_request("BarChart"), _RESULT)
        assert props["xAxis"] == "region"
        assert props["yAxis"] == "revenue"
        assert props["data"] == [
            {"label": "East", "value": 100.0},
            {"label": "West", "value": 80.0},
        ]

    def test_pie_chart_omits_axes(self) -> None:
        props = _chart_props(_request("PieChart"), _RESULT)
        assert "xAxis" not in props
        assert "yAxis" not in props


class TestVizProps:
    def test_data_table_maps_all_columns(self) -> None:
        props = _viz_props(_request("DataTable", title="T"), _RESULT)
        assert props["columns"] == [
            {"key": "region", "header": "region"},
            {"key": "revenue", "header": "revenue"},
        ]
        assert len(props["rows"]) == 2  # type: ignore[arg-type]

    def test_metric_formats_first_row_value(self) -> None:
        props = _viz_props(_request("Metric", title="Total"), _RESULT)
        assert props["value"] == "100"
        assert props["label"] == "Total"


class TestDefaultTitle:
    def test_chart_title_combines_columns(self) -> None:
        assert _default_title("BarChart", "region", "total_revenue") == "Total Revenue by Region"

    def test_metric_title_is_value_column(self) -> None:
        assert _default_title("Metric", "", "row_count") == "Row Count"

    def test_humanizes_camel_case_aliases(self) -> None:
        assert _default_title("BarChart", "SaleYear", "TotalSales") == "Total Sales by Sale Year"


class TestSpecFromResult:
    def test_narrative_needs_no_result(self) -> None:
        request = _request(
            "NarrativeText",
            title="",
            label_column="",
            value_column="",
            content="Hi",
        )
        spec = _spec_from_result(_state(result=None), request)
        assert spec["elements"]["main"]["props"]["content"] == "Hi"  # type: ignore[index]

    def test_unknown_component_raises(self) -> None:
        with pytest.raises(_BuildError, match="Unknown component"):
            _spec_from_result(_state(), _request("ScatterPlot"))

    def test_chart_without_result_raises(self) -> None:
        with pytest.raises(_BuildError, match="run_sql"):
            _spec_from_result(_state(result=None), _request("BarChart"))

    def test_full_chart_spec_has_meta(self) -> None:
        spec = _spec_from_result(_state(), _request("BarChart"))
        assert spec["root"] == "main"
        assert spec["meta"]["sql"] == "SELECT 1"  # type: ignore[index]
        assert spec["meta"]["format"] == "CHART"  # type: ignore[index]


class TestFormatKind:
    def test_table(self) -> None:
        assert _format_kind("DataTable") is ResponseKind.TABLE

    def test_text(self) -> None:
        assert _format_kind("NarrativeText") is ResponseKind.TEXT

    def test_chart_default(self) -> None:
        assert _format_kind("PieChart") is ResponseKind.CHART


class TestToEvent:
    def test_tool_call(self) -> None:
        event = _to_event({"kind": "tool_call", "name": "run_sql", "sql": "SELECT 1"})
        assert isinstance(event, ToolCallEvent)
        assert event._tool_name.value == "run_sql"

    def test_spec(self) -> None:
        event = _to_event({"kind": "spec", "payload": {"root": "x", "elements": {}}})
        assert isinstance(event, SpecFragmentEvent)

    def test_unknown_returns_none(self) -> None:
        assert _to_event({"kind": "other"}) is None


class TestRunState:
    def test_resolves_dataset_id_from_sql(self) -> None:
        state = _RunState({"ds_abc": "the-id"})
        state.record("SELECT * FROM ds_abc", _RESULT)
        assert state.dataset_id() == "the-id"

    def test_returns_empty_when_no_query_recorded(self) -> None:
        assert _RunState({"ds_abc": "the-id"}).dataset_id() == ""


class TestSchemaContext:
    def test_empty_when_no_datasets(self) -> None:
        assert "No datasets registered" in _schema_context([])

    def test_lists_view_and_columns(self) -> None:
        context = _schema_context([_FakeDataset()])  # type: ignore[list-item]
        assert "ds_" in context
        assert "sales" in context
        assert "region VARCHAR" in context


class TestNarrativeSpec:
    def test_wraps_text(self) -> None:
        spec = _narrative_spec("hi")
        assert spec["elements"]["answer"]["props"]["content"] == "hi"  # type: ignore[index]


class TestOrchestratorGuards:
    async def test_errors_when_sql_tool_missing(self) -> None:
        orchestrator = DeepAgentsOrchestrator(model=object(), datasets=_FakeDatasetRepo())
        events = await _collect(orchestrator.run(_message(), _conversation(), _ToolKitWithout()))
        assert any(isinstance(e, ErrorEvent) for e in events)


# ── Fakes ──


class _FakeDatasetId:
    value = UUID(int=0xABC)


class _FakeIdentity:
    _id = _FakeDatasetId()


class _FakeDataset:
    _identity = _FakeIdentity()

    def display_name(self) -> str:
        return "sales"

    def columns_summary(self) -> str:
        return "region VARCHAR, revenue BIGINT"


class _EmptyDatasets:
    def to_list(self) -> list[object]:
        return []


class _FakeDatasetRepo:
    def find_all(self) -> _EmptyDatasets:
        return _EmptyDatasets()


class _ToolKitWithout:
    def find(self, name: ToolName) -> None:
        return None

    def register(self, tool: object) -> None:
        pass

    def all(self) -> list[object]:
        return []


def _conversation() -> Conversation:
    return Conversation(identity=EntityId(uuid4()), history=Messages())


def _message() -> Message:
    return Message(
        identity=MessageIdentity(
            _id=EntityId(uuid4()),
            _role=MessageRole.USER,
            _timestamp=CreatedAt(datetime.now(UTC)),
        ),
        body=MessageBody(_content=MessageContent("hi"), _tool_call=None),
    )


async def _collect(gen: AsyncIterator[AgentEvent]) -> list[AgentEvent]:
    return [event async for event in gen]
