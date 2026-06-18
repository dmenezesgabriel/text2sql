from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from src.chat.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.chat.domain.value_objects import (
    AgentEvent,
    ConversationId,
    ErrorEvent,
    Parameters,
    SpecFragmentEvent,
    ThinkingEvent,
    ToolCallEvent,
    ToolName,
)
from src.chat.infrastructure.agent_graph.spec_builder import narrative_spec
from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.datasets.domain.entities import Dataset

_log = logging.getLogger(__name__)


class LangGraphOrchestrator(IAgentOrchestrator):
    def __init__(self, graph: Any, datasets: IDatasetRepository) -> None:
        self._graph = graph
        self._datasets = datasets

    async def run(
        self,
        content: str,
        conversation_id: ConversationId,
    ) -> AsyncIterator[AgentEvent]:
        datasets = self._datasets.find_all().to_list()
        initial: dict[str, Any] = {
            "messages": [HumanMessage(content=content)],
            "schema_context": _schema_context(datasets),
            "dataset_views": _dataset_views(datasets),
            "intent": "",
            "clarification_question": "",
            "sql": "",
            "sql_result": None,
            "sql_error": "",
            "sql_retries": 0,
            "viz_component": "",
            "label_column": "",
            "value_column": "",
            "narrative": "",
            "spec": None,
        }
        config = {"configurable": {"thread_id": str(conversation_id.value)}}
        yield ThinkingEvent("Analyzing your question...")
        async for event in _stream_graph(self._graph, initial, config):
            yield event

    async def get_messages(
        self,
        conversation_id: ConversationId,
    ) -> list[dict[str, object]]:
        config = {"configurable": {"thread_id": str(conversation_id.value)}}
        state = await self._graph.aget_state(config)
        if state is None or not state.values.get("messages"):
            return []
        messages = [_base_msg_to_dict(m) for m in state.values["messages"]]
        spec = state.values.get("spec")
        if spec:
            for msg in reversed(messages):
                if msg["role"] == "assistant":
                    msg["spec"] = spec
                    break
        return messages


def _base_msg_to_dict(msg: Any) -> dict[str, object]:
    if isinstance(msg, HumanMessage):
        return {"role": "user", "content": str(msg.content)}
    if isinstance(msg, AIMessage):
        return {"role": "assistant", "content": str(msg.content)}
    return {"role": "assistant", "content": ""}


def _dataset_views(datasets: list[Dataset]) -> dict[str, str]:
    return {f"ds_{d._identity._id.value.hex}": str(d._identity._id.value) for d in datasets}


def _schema_context(datasets: list[Dataset]) -> str:
    lines = [
        f"View: ds_{d._identity._id.value.hex}  (dataset: {d.display_name()})\n"
        f"Columns: {d.columns_summary()}"
        for d in datasets
    ]
    return "\n\n".join(lines) if lines else "No datasets registered yet."


async def _stream_graph(
    graph: Any,
    initial: dict[str, Any],
    config: dict[str, Any],
) -> AsyncIterator[AgentEvent]:
    produced_spec = False
    try:
        async for mode, chunk in graph.astream(
            initial,
            config=config,
            stream_mode=["custom", "values"],
        ):
            if mode == "values":
                continue
            event = _to_event(chunk)
            if event is None:
                continue
            produced_spec = produced_spec or isinstance(event, SpecFragmentEvent)
            yield event
    except Exception as exc:
        yield ErrorEvent(_message=_agent_error_message(exc))
        return
    if not produced_spec:
        yield SpecFragmentEvent(_payload=narrative_spec("I wasn't able to produce a result."))


def _agent_error_message(exc: Exception) -> str:
    exc_type = type(exc).__name__
    _log.error("agent.error", extra={"exc_type": exc_type, "exc": str(exc)}, exc_info=True)
    if "RateLimitError" in exc_type or "rate_limit" in str(exc).lower():
        return "Rate limit reached. Please wait a moment and try again."
    return f"The agent could not complete the request: {exc_type}"


def _to_event(chunk: object) -> AgentEvent | None:
    if not isinstance(chunk, dict):
        return None
    return _event_for_kind(chunk)


def _event_for_kind(chunk: dict[str, object]) -> AgentEvent | None:
    kind = chunk.get("kind")
    if kind == "tool_call":
        return ToolCallEvent(
            _tool_name=ToolName(str(chunk.get("name", ""))),
            _parameters=Parameters({"sql": chunk.get("sql", "")}),
        )
    if kind == "spec":
        payload = chunk.get("payload", {})
        return SpecFragmentEvent(_payload=payload if isinstance(payload, dict) else {})
    return None
