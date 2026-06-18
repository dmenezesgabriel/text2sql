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
    _agent_error_message,
    _dataset_views,
    _schema_context,
    _stream_graph,
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
    def __init__(
        self,
        events: list[dict[str, object]],
        state_values: dict[str, object] | None = None,
    ) -> None:
        self._events = events
        self._state_values = state_values or {}

    async def astream(
        self,
        initial: object,
        config: object,
        stream_mode: object,
    ) -> AsyncIterator[tuple[str, object]]:
        for event in self._events:
            yield "custom", event

    async def aget_state(self, config: object) -> object:
        class _Snapshot:
            def __init__(self, values: dict[str, object]) -> None:
                self.values = values

        return _Snapshot(self._state_values)


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

    def test_tool_call_extracts_name_exactly(self) -> None:
        event = _to_event({"kind": "tool_call", "name": "run_sql", "sql": "SELECT 1"})
        assert isinstance(event, ToolCallEvent)
        assert event._tool_name.value == "run_sql"

    def test_tool_call_extracts_sql_exactly(self) -> None:
        event = _to_event({"kind": "tool_call", "name": "run_sql", "sql": "SELECT 42"})
        assert isinstance(event, ToolCallEvent)
        assert event._parameters.value == {"sql": "SELECT 42"}

    def test_tool_call_missing_name_defaults_to_empty_string(self) -> None:
        event = _to_event({"kind": "tool_call", "sql": "SELECT 1"})
        assert isinstance(event, ToolCallEvent)
        assert event._tool_name.value == ""

    def test_tool_call_missing_sql_defaults_to_empty_string_in_parameters(self) -> None:
        event = _to_event({"kind": "tool_call", "name": "run_sql"})
        assert isinstance(event, ToolCallEvent)
        assert event._parameters.value["sql"] == ""

    def test_spec_extracts_payload_exactly(self) -> None:
        payload = {
            "root": "x",
            "elements": {"x": {"type": "NarrativeText", "props": {"content": "hi"}}},
        }
        event = _to_event({"kind": "spec", "payload": payload})
        assert isinstance(event, SpecFragmentEvent)
        assert event._payload == payload


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


class TestGetMessages:
    async def test_returns_empty_when_no_state(self) -> None:
        class _NoStateGraph:
            async def astream(self, *a: object, **k: object) -> AsyncIterator[object]:
                return
                yield

            async def aget_state(self, config: object) -> None:
                return None

        orchestrator = LangGraphOrchestrator(graph=_NoStateGraph(), datasets=_FakeDatasetRepo())
        result = await orchestrator.get_messages(ConversationId(uuid4()))
        assert result == []

    async def test_returns_empty_when_no_messages_in_state(self) -> None:

        graph = _FakeGraph([], state_values={"messages": [], "spec": None})
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        result = await orchestrator.get_messages(ConversationId(uuid4()))
        assert result == []

    async def test_maps_human_message_to_user_role(self) -> None:
        from langchain_core.messages import HumanMessage

        graph = _FakeGraph(
            [],
            state_values={"messages": [HumanMessage(content="Hello")], "spec": None},
        )
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        result = await orchestrator.get_messages(ConversationId(uuid4()))
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"

    async def test_maps_ai_message_to_assistant_role(self) -> None:
        from langchain_core.messages import AIMessage

        graph = _FakeGraph(
            [],
            state_values={"messages": [AIMessage(content="I found data")], "spec": None},
        )
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        result = await orchestrator.get_messages(ConversationId(uuid4()))
        assert result[0]["role"] == "assistant"
        assert result[0]["content"] == "I found data"

    async def test_attaches_spec_to_last_assistant_message(self) -> None:
        from langchain_core.messages import AIMessage, HumanMessage

        spec = {"root": "chart", "elements": {}}
        graph = _FakeGraph(
            [],
            state_values={
                "messages": [
                    HumanMessage(content="Show sales"),
                    AIMessage(content="Here is the chart"),
                ],
                "spec": spec,
            },
        )
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        result = await orchestrator.get_messages(ConversationId(uuid4()))
        last_assistant = next(m for m in reversed(result) if m["role"] == "assistant")
        assert last_assistant["spec"] == spec

    async def test_no_spec_attached_when_state_spec_is_none(self) -> None:
        from langchain_core.messages import HumanMessage

        graph = _FakeGraph(
            [],
            state_values={"messages": [HumanMessage(content="Hi")], "spec": None},
        )
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        result = await orchestrator.get_messages(ConversationId(uuid4()))
        assert "spec" not in result[0]


class _CapturingGraph:
    def __init__(self) -> None:
        self.captured_initial: dict[str, object] | None = None
        self.captured_config: object = None
        self.captured_stream_mode: object = None

    async def astream(
        self,
        initial: dict[str, object],
        config: object,
        stream_mode: object,
    ) -> AsyncIterator[tuple[str, object]]:
        self.captured_initial = initial
        self.captured_config = config
        self.captured_stream_mode = stream_mode
        yield "custom", {"kind": "spec", "payload": {"root": "x", "elements": {}}}


class _CapturingStateGraph:
    def __init__(self, state_values: dict[str, object]) -> None:
        self._state_values = state_values
        self.captured_config: object = None

    async def aget_state(self, config: object) -> object:
        self.captured_config = config

        class _Snap:
            def __init__(self, v: dict[str, object]) -> None:
                self.values = v

        return _Snap(self._state_values)

    async def astream(self, *a: object, **k: object) -> AsyncIterator[object]:
        return
        yield  # type: ignore[misc]


class TestRunInitialState:
    async def test_run_passes_correct_initial_keys_and_values(self) -> None:
        from langchain_core.messages import HumanMessage

        graph = _CapturingGraph()
        orchestrator = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        await _collect(
            orchestrator.run(content="hello world", conversation_id=ConversationId(uuid4())),
        )

        init = graph.captured_initial
        assert init is not None

        assert "messages" in init
        assert len(init["messages"]) == 1  # type: ignore[arg-type]
        assert isinstance(init["messages"][0], HumanMessage)  # type: ignore[index]
        assert str(init["messages"][0].content) == "hello world"  # type: ignore[index]

        assert "schema_context" in init
        assert "dataset_views" in init

        assert "intent" in init
        assert init["intent"] == ""

        assert "clarification_question" in init
        assert init["clarification_question"] == ""

        assert "sql" in init
        assert init["sql"] == ""

        assert "sql_result" in init
        assert init["sql_result"] is None

        assert "sql_error" in init
        assert init["sql_error"] == ""

        assert "sql_retries" in init
        assert init["sql_retries"] == 0

        assert "viz_component" in init
        assert init["viz_component"] == ""

        assert "label_column" in init
        assert init["label_column"] == ""

        assert "value_column" in init
        assert init["value_column"] == ""

        assert "narrative" in init
        assert init["narrative"] == ""

        assert "spec" in init
        assert init["spec"] is None


class TestAgentErrorMessage:
    def test_rate_limit_by_exc_type_name(self) -> None:
        class RateLimitError(Exception):
            pass

        result = _agent_error_message(RateLimitError("quota exceeded"))
        assert result == "Rate limit reached. Please wait a moment and try again."

    def test_rate_limit_by_exc_message_content(self) -> None:
        result = _agent_error_message(Exception("you hit a rate_limit"))
        assert result == "Rate limit reached. Please wait a moment and try again."

    def test_rate_limit_message_exact_text(self) -> None:
        class RateLimitError(Exception):
            pass

        result = _agent_error_message(RateLimitError("too many requests"))
        assert result == "Rate limit reached. Please wait a moment and try again."

    def test_rate_limit_check_is_case_insensitive_for_exc_message(self) -> None:
        # "rate_limit" must be found in str(exc).lower(); mutant uses .upper() which would miss it
        result = _agent_error_message(Exception("rate_limit exceeded"))
        assert result == "Rate limit reached. Please wait a moment and try again."

    def test_rate_limit_not_triggered_by_uppercase_only_message(self) -> None:
        # "RATE_LIMIT" (uppercase) in .lower() → lowercased → "rate_limit" → still matches
        # but mutant changes "rate_limit" constant to "RATE_LIMIT": "RATE_LIMIT" not in lower → generic
        result = _agent_error_message(Exception("rate_limit"))
        assert result == "Rate limit reached. Please wait a moment and try again."

    def test_generic_exc_returns_type_name(self) -> None:
        result = _agent_error_message(ValueError("something broke"))
        assert result == "The agent could not complete the request: ValueError"

    def test_generic_exc_runtime_error(self) -> None:
        result = _agent_error_message(RuntimeError("boom"))
        assert result == "The agent could not complete the request: RuntimeError"


class TestRunConfig:
    async def test_config_key_is_configurable(self) -> None:
        cid = uuid4()
        graph = _CapturingGraph()
        orch = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        await _collect(orch.run("q", ConversationId(cid)))
        assert graph.captured_config is not None
        assert "configurable" in graph.captured_config  # type: ignore[operator]

    async def test_config_thread_id_key_exists(self) -> None:
        cid = uuid4()
        graph = _CapturingGraph()
        orch = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        await _collect(orch.run("q", ConversationId(cid)))
        cfg = graph.captured_config
        assert "thread_id" in cfg["configurable"]  # type: ignore[index]

    async def test_config_thread_id_value_matches_conversation_id(self) -> None:
        cid = uuid4()
        graph = _CapturingGraph()
        orch = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        await _collect(orch.run("q", ConversationId(cid)))
        thread_id = graph.captured_config["configurable"]["thread_id"]  # type: ignore[index]
        assert thread_id == str(cid)

    async def test_stream_mode_is_custom_and_values(self) -> None:
        graph = _CapturingGraph()
        orch = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        await _collect(orch.run("q", ConversationId(uuid4())))
        assert graph.captured_stream_mode == ["custom", "values"]

    async def test_thinking_event_message_exact(self) -> None:
        graph = _CapturingGraph()
        orch = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        events = await _collect(orch.run("q", ConversationId(uuid4())))
        thinking = events[0]
        assert isinstance(thinking, ThinkingEvent)
        assert thinking.message == "Analyzing your question..."


class TestGetMessagesConfig:
    async def test_config_key_is_configurable(self) -> None:
        from langchain_core.messages import HumanMessage

        cid = uuid4()
        graph = _CapturingStateGraph({"messages": [HumanMessage(content="hi")], "spec": None})
        orch = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        await orch.get_messages(ConversationId(cid))
        assert "configurable" in graph.captured_config  # type: ignore[operator]

    async def test_config_thread_id_key_exists(self) -> None:
        from langchain_core.messages import HumanMessage

        cid = uuid4()
        graph = _CapturingStateGraph({"messages": [HumanMessage(content="hi")], "spec": None})
        orch = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        await orch.get_messages(ConversationId(cid))
        assert "thread_id" in graph.captured_config["configurable"]  # type: ignore[index]

    async def test_config_thread_id_value_matches_conversation_id(self) -> None:
        from langchain_core.messages import HumanMessage

        cid = uuid4()
        graph = _CapturingStateGraph({"messages": [HumanMessage(content="hi")], "spec": None})
        orch = LangGraphOrchestrator(graph=graph, datasets=_FakeDatasetRepo())
        await orch.get_messages(ConversationId(cid))
        thread_id = graph.captured_config["configurable"]["thread_id"]  # type: ignore[index]
        assert thread_id == str(cid)


class TestAgentErrorMessageLogging:
    def test_logs_correct_message_name(self) -> None:
        from unittest.mock import patch

        with patch("src.chat.infrastructure.langgraph_orchestrator._log") as mock_log:
            _agent_error_message(ValueError("test"))
        assert mock_log.error.call_args[0][0] == "agent.error"

    def test_logs_exc_type_in_extra(self) -> None:
        from unittest.mock import patch

        with patch("src.chat.infrastructure.langgraph_orchestrator._log") as mock_log:
            _agent_error_message(ValueError("test error"))
        extra = mock_log.error.call_args[1]["extra"]
        assert extra["exc_type"] == "ValueError"

    def test_logs_exc_str_in_extra(self) -> None:
        from unittest.mock import patch

        with patch("src.chat.infrastructure.langgraph_orchestrator._log") as mock_log:
            _agent_error_message(ValueError("test error"))
        extra = mock_log.error.call_args[1]["extra"]
        assert extra["exc"] == "test error"

    def test_logs_with_exc_info_true(self) -> None:
        from unittest.mock import patch

        with patch("src.chat.infrastructure.langgraph_orchestrator._log") as mock_log:
            _agent_error_message(ValueError("test"))
        assert mock_log.error.call_args[1]["exc_info"] is True


class TestBaseMsgToDict:
    def test_human_message_role_is_user(self) -> None:
        from langchain_core.messages import HumanMessage

        from src.chat.infrastructure.langgraph_orchestrator import _base_msg_to_dict

        result = _base_msg_to_dict(HumanMessage(content="hello"))
        assert result["role"] == "user"

    def test_ai_message_role_is_assistant(self) -> None:
        from langchain_core.messages import AIMessage

        from src.chat.infrastructure.langgraph_orchestrator import _base_msg_to_dict

        result = _base_msg_to_dict(AIMessage(content="hi"))
        assert result["role"] == "assistant"

    def test_human_message_content_exact(self) -> None:
        from langchain_core.messages import HumanMessage

        from src.chat.infrastructure.langgraph_orchestrator import _base_msg_to_dict

        result = _base_msg_to_dict(HumanMessage(content="hello world"))
        assert result["content"] == "hello world"

    def test_ai_message_content_exact(self) -> None:
        from langchain_core.messages import AIMessage

        from src.chat.infrastructure.langgraph_orchestrator import _base_msg_to_dict

        result = _base_msg_to_dict(AIMessage(content="the answer"))
        assert result["content"] == "the answer"

    def test_unknown_message_role_is_assistant(self) -> None:
        from src.chat.infrastructure.langgraph_orchestrator import _base_msg_to_dict

        result = _base_msg_to_dict("not a message")
        assert result["role"] == "assistant"

    def test_unknown_message_content_is_empty_string(self) -> None:
        from src.chat.infrastructure.langgraph_orchestrator import _base_msg_to_dict

        result = _base_msg_to_dict("not a message")
        assert result["content"] == ""

    def test_unknown_message_has_role_key_not_xxrolexx(self) -> None:
        from src.chat.infrastructure.langgraph_orchestrator import _base_msg_to_dict

        result = _base_msg_to_dict(object())
        assert "role" in result
        assert "XXroleXX" not in result
        assert "ROLE" not in result

    def test_unknown_message_has_content_key_not_xxcontentxx(self) -> None:
        from src.chat.infrastructure.langgraph_orchestrator import _base_msg_to_dict

        result = _base_msg_to_dict(object())
        assert "content" in result
        assert "XXcontentXX" not in result
        assert "CONTENT" not in result


class TestDatasetViewsValues:
    def test_value_is_uuid_string_not_none(self) -> None:
        ds = _FakeDataset()
        views = _dataset_views([ds])  # type: ignore[list-item]
        key = f"ds_{ds._identity._id.value.hex}"
        assert views[key] == str(ds._identity._id.value)
        assert views[key] != "None"


class TestSchemaContextExact:
    def test_no_datasets_message_exact(self) -> None:
        result = _schema_context([])
        assert result == "No datasets registered yet."

    def test_two_datasets_joined_with_double_newline(self) -> None:
        ds1 = _FakeDataset()
        ds2 = _FakeDataset()
        result = _schema_context([ds1, ds2])  # type: ignore[list-item]
        assert "\n\n" in result
        assert "XX\n\nXX" not in result

    def test_dataset_view_line_prefix(self) -> None:
        ds = _FakeDataset()
        result = _schema_context([ds])  # type: ignore[list-item]
        assert result.startswith("View: ds_")


class TestStreamGraphStreamMode:
    async def test_values_mode_events_skipped(self) -> None:
        from src.chat.infrastructure.langgraph_orchestrator import _stream_graph

        class _MixedGraph:
            async def astream(
                self,
                initial: object,
                config: object,
                stream_mode: object,
            ) -> AsyncIterator[tuple[str, object]]:
                yield "values", {"kind": "spec", "payload": {"root": "x", "elements": {}}}
                yield "custom", {"kind": "spec", "payload": {"root": "x", "elements": {}}}

        events = [e async for e in _stream_graph(_MixedGraph(), {}, {})]
        spec_events = [e for e in events if isinstance(e, SpecFragmentEvent)]
        # Only the "custom" one should pass through → exactly 1 SpecFragmentEvent from graph
        # (plus no fallback since spec was produced)
        assert len(spec_events) == 1

    async def test_stream_mode_list_passed_exactly(self) -> None:
        from src.chat.infrastructure.langgraph_orchestrator import _stream_graph

        captured: list[object] = []

        class _ModeCapture:
            async def astream(
                self,
                initial: object,
                config: object,
                stream_mode: object,
            ) -> AsyncIterator[tuple[str, object]]:
                captured.append(stream_mode)
                yield "custom", {"kind": "spec", "payload": {"root": "x", "elements": {}}}

        await _collect(_stream_graph(_ModeCapture(), {}, {}))  # type: ignore[arg-type]
        assert captured[0] == ["custom", "values"]


class TestStreamGraphPayloads:
    """Kill genuine survivors in _stream_graph by asserting exact payload provenance."""

    _CUSTOM_PAYLOAD: dict[str, object] = {
        "root": "x",
        "elements": {"x": {"type": "NarrativeText", "props": {"content": "custom"}}},
    }

    async def test_custom_chunk_payload_reaches_caller(self) -> None:
        # Kills mutmut_13 (mode != "values" skips custom),
        # mutmut_17/18 (event=None/event=_to_event(None) loses payload),
        # mutmut_19 (if event is not None: continue skips valid events)
        class _CustomGraph:
            async def astream(
                self,
                i: object,
                config: object,
                stream_mode: object,
            ) -> AsyncIterator[tuple[str, object]]:
                yield "custom", {"kind": "spec", "payload": TestStreamGraphPayloads._CUSTOM_PAYLOAD}

        events = [e async for e in _stream_graph(_CustomGraph(), {}, {})]  # type: ignore[arg-type]
        spec_payloads = [e._payload for e in events if isinstance(e, SpecFragmentEvent)]
        assert TestStreamGraphPayloads._CUSTOM_PAYLOAD in spec_payloads

    async def test_values_mode_does_not_break_loop(self) -> None:
        # Kills mutmut_16 (break instead of continue on "values"):
        # if break, "custom" after "values" is never processed → specific_payload absent
        class _ValuesBeforeCustom:
            async def astream(
                self,
                i: object,
                config: object,
                stream_mode: object,
            ) -> AsyncIterator[tuple[str, object]]:
                yield "values", {"some": "state"}
                yield "custom", {"kind": "spec", "payload": TestStreamGraphPayloads._CUSTOM_PAYLOAD}

        events = [e async for e in _stream_graph(_ValuesBeforeCustom(), {}, {})]  # type: ignore[arg-type]
        spec_payloads = [e._payload for e in events if isinstance(e, SpecFragmentEvent)]
        assert TestStreamGraphPayloads._CUSTOM_PAYLOAD in spec_payloads

    async def test_error_event_message_is_not_none(self) -> None:
        # Kills mutmut_23: ErrorEvent(_message=None)
        class _RaisingGraph:
            async def astream(self, *a: object, **k: object) -> AsyncIterator[object]:
                raise RuntimeError("boom")
                yield  # make async generator

        events = [e async for e in _stream_graph(_RaisingGraph(), {}, {})]  # type: ignore[arg-type]
        error_events = [e for e in events if isinstance(e, ErrorEvent)]
        assert len(error_events) == 1
        assert error_events[0]._message is not None

    async def test_error_event_message_contains_exception_type(self) -> None:
        # Kills mutmut_24: ErrorEvent(_message=_agent_error_message(None)) → "NoneType" not "RuntimeError"
        class _RaisingGraph:
            async def astream(self, *a: object, **k: object) -> AsyncIterator[object]:
                raise RuntimeError("failed")
                yield

        events = [e async for e in _stream_graph(_RaisingGraph(), {}, {})]  # type: ignore[arg-type]
        error_events = [e for e in events if isinstance(e, ErrorEvent)]
        assert len(error_events) == 1
        assert "RuntimeError" in error_events[0]._message

    async def test_fallback_spec_content_exact_text(self) -> None:
        # Kills mutmut_28/29/30: fallback text "XXI wasn't...XX" / lowercase / uppercase
        class _EmptyGraph:
            async def astream(self, *a: object, **k: object) -> AsyncIterator[object]:
                return
                yield

        events = [e async for e in _stream_graph(_EmptyGraph(), {}, {})]  # type: ignore[arg-type]
        spec_events = [e for e in events if isinstance(e, SpecFragmentEvent)]
        assert len(spec_events) == 1
        content = spec_events[0]._payload["elements"]["answer"]["props"]["content"]
        assert content == "I wasn't able to produce a result."
