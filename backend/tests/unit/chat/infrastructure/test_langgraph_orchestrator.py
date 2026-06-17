from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

from src.chat.domain.value_objects import (
    AgentEvent,
    ConversationId,
    ErrorEvent,
    SpecFragmentEvent,
    ThinkingEvent,
    ToolCallEvent,
)
from src.chat.infrastructure.langgraph_orchestrator import (
    LangGraphOrchestrator,
    _dataset_views,
    _schema_context,
    _to_event,
)


class _FakeDatasetId:
    value = uuid4()
    hex = value.hex


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


class _FakeDatasetRepo2:
    def find_all(self) -> object:
        class _Datasets:
            def to_list(self) -> list[object]:
                return [_FakeDataset()]

        return _Datasets()


class _FakeGraph:
    def __init__(self, events: list[dict[str, object]]) -> None:
        self._events = events

    async def astream(
        self,
        initial: object,
        config: object,
        stream_mode: object,
    ) -> AsyncIterator[tuple[str, object]]:
        for event in self._events:
            yield "custom", event


async def _collect(gen: AsyncIterator[AgentEvent]) -> list[AgentEvent]:
    return [e async for e in gen]


class TestToEvent:
    def test_tool_call(self) -> None:
        event = _to_event({"kind": "tool_call", "name": "run_sql", "sql": "SELECT 1"})
        assert isinstance(event, ToolCallEvent)

    def test_spec(self) -> None:
        event = _to_event({"kind": "spec", "payload": {"root": "x", "elements": {}}})
        assert isinstance(event, SpecFragmentEvent)

    def test_unknown_returns_none(self) -> None:
        assert _to_event({"kind": "other"}) is None

    def test_non_dict_returns_none(self) -> None:
        assert _to_event("not a dict") is None


class TestSchemaContext:
    def test_empty_when_no_datasets(self) -> None:
        assert "No datasets registered" in _schema_context([])

    def test_lists_view_and_columns(self) -> None:
        context = _schema_context([_FakeDataset()])  # type: ignore[list-item]
        assert "ds_" in context
        assert "sales" in context


class TestDatasetViews:
    def test_maps_view_name_to_id(self) -> None:
        ds = _FakeDataset()
        views = _dataset_views([ds])  # type: ignore[list-item]
        expected_key = f"ds_{ds._identity._id.value.hex}"
        assert expected_key in views


class TestLangGraphOrchestrator:
    async def test_yields_thinking_event_first(self) -> None:
        spec_payload = {"root": "x", "elements": {}}
        graph = _FakeGraph([{"kind": "spec", "payload": spec_payload}])
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        events = await _collect(
            orchestrator.run(content="hello", conversation_id=ConversationId(uuid4())),
        )
        assert isinstance(events[0], ThinkingEvent)

    async def test_yields_spec_event_from_graph(self) -> None:
        spec_payload = {"root": "x", "elements": {}}
        graph = _FakeGraph([{"kind": "spec", "payload": spec_payload}])
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        events = await _collect(
            orchestrator.run(content="hello", conversation_id=ConversationId(uuid4())),
        )
        assert any(isinstance(e, SpecFragmentEvent) for e in events)

    async def test_fallback_spec_when_none_produced(self) -> None:
        graph = _FakeGraph([])  # no spec emitted
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        events = await _collect(
            orchestrator.run(content="hello", conversation_id=ConversationId(uuid4())),
        )
        assert any(isinstance(e, SpecFragmentEvent) for e in events)

    async def test_error_event_on_graph_exception(self) -> None:
        class _BrokenGraph:
            async def astream(self, *args: object, **kwargs: object) -> AsyncIterator[object]:
                raise RuntimeError("boom")
                yield  # make it an async generator

        orchestrator = LangGraphOrchestrator(graph=_BrokenGraph(), datasets=_FakeDatasetRepo())
        events = await _collect(
            orchestrator.run(content="hello", conversation_id=ConversationId(uuid4())),
        )
        assert any(isinstance(e, ErrorEvent) for e in events)
