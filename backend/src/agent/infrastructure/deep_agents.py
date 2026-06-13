from __future__ import annotations

import json
from collections.abc import AsyncIterator

from src.agent.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.agent.application.ports.i_language_model_provider import ILanguageModelProvider
from src.agent.application.ports.i_tool_kit import IToolKit
from src.agent.domain.entities import Conversation, Message
from src.agent.domain.value_objects import (
    AgentEvent,
    ErrorEvent,
    LLMToolCall,
    MessageRole,
    Parameters,
    SpecFragmentEvent,
    ThinkingEvent,
    ToolCallEvent,
    ToolName,
)
from src.datasets.application.ports.i_dataset_repository import IDatasetRepository

AGENT_TOOLS: list[dict[str, object]] = [
    {
        "type": "function",
        "function": {
            "name": "generate_sql",
            "description": (
                "Execute a DuckDB SQL query against available dataset views. "
                "Use the exact view names provided in the schema context."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "Valid DuckDB SQL query"},
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of what this SQL computes",
                    },
                },
                "required": ["sql", "reasoning"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_visualization",
            "description": (
                "Build a json-render spec from query results. "
                "Call this after generate_sql returns data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "spec": {
                        "type": "object",
                        "description": (
                            "json-render Spec. Must have 'root' (string key into 'elements') "
                            "and 'elements' (dict mapping key to {type, props}). "
                            'Example: {"root":"c","elements":{"c":{"type":"BarChart","props":{}}}}'
                        ),
                    },
                },
                "required": ["spec"],
            },
        },
    },
]

_SYSTEM_TEMPLATE = """\
You are a BI analyst assistant. Answer questions by querying data with DuckDB SQL.

## Available Views
{schemas}

## Instructions
1. Call generate_sql with a valid DuckDB SQL query using the view names above.
2. After seeing the query result, call build_visualization with a json-render spec.
3. Spec format: {{"root":"key","elements":{{"key":{{"type":"ComponentName","props":{{}}}}}}}}

## Component Props Reference
- BarChart: {{"title": str, "xAxis": str, "yAxis": str, "data": [{{"label": str, "value": num}}]}}
- LineChart: {{"title": str, "xAxis": str, "yAxis": str, "data": [{{"label": str, "value": num}}]}}
- DataTable: {{"title"?: str, "columns": [{{"key": str, "header": str}}], "rows": [record]}}
- Metric: {{"label": str, "value": str, "change": str (opt), "direction": up|down|neutral (opt)}}
- NarrativeText: {{"content": str, "tone": analytical|conversational|executive (opt)}}
"""


class DeepAgentsOrchestrator(IAgentOrchestrator):
    def __init__(self, llm: ILanguageModelProvider, datasets: IDatasetRepository) -> None:
        self._llm = llm
        self._datasets = datasets

    async def run(
        self,
        message: Message,
        conversation: Conversation,
        toolkit: IToolKit,
    ) -> AsyncIterator[AgentEvent]:
        system_content = _SYSTEM_TEMPLATE.format(schemas=self._build_schema_context())
        system_msg: dict[str, object] = {"role": "system", "content": system_content}
        history: list[dict[str, object]] = [
            {"role": m._identity._role.name.lower(), "content": m._body._content.value}
            for m in conversation._history.to_list()
            if not m.is_from(MessageRole.SYSTEM)
        ]
        messages: list[dict[str, object]] = [system_msg] + history

        yield ThinkingEvent("Analyzing your question...")

        for _ in range(4):
            response = await self._llm.call_with_tools(messages, AGENT_TOOLS)

            if not response.has_tool_calls():
                text = response._text or "I could not answer that question."
                yield SpecFragmentEvent(_payload=_narrative_spec(text))
                return

            messages.append(_assistant_turn(response._tool_calls))

            for tool_call in response._tool_calls:
                if tool_call._name == "generate_sql":
                    async for event in self._handle_sql(tool_call, messages, toolkit):
                        yield event
                    continue
                if tool_call._name == "build_visualization":
                    spec = tool_call._arguments.get("spec", {})
                    yield SpecFragmentEvent(_payload=spec if isinstance(spec, dict) else {})
                    return

        yield ErrorEvent(
            _message="Agent could not produce a visualization within the allowed steps.",
        )

    def _build_schema_context(self) -> str:
        lines = []
        for ds in self._datasets.find_all().to_list():
            view = f"ds_{ds._identity._id.value.hex}"
            lines.append(
                f"View: {view}  (dataset: {ds.display_name()})\nColumns: {ds.columns_summary()}",
            )
        return "\n\n".join(lines) if lines else "No datasets registered yet."

    async def _handle_sql(
        self,
        tool_call: LLMToolCall,
        messages: list[dict[str, object]],
        toolkit: IToolKit,
    ) -> AsyncIterator[AgentEvent]:
        yield ThinkingEvent("Executing SQL...")
        yield ToolCallEvent(
            _tool_name=ToolName("generate_sql"),
            _parameters=Parameters(tool_call._arguments),
        )
        sql = tool_call._arguments.get("sql", "")
        try:
            sql_tool = toolkit.find(ToolName("sql_generator"))
            if sql_tool is None:
                msg = "sql_generator tool not registered in toolkit"
                raise ValueError(msg)
            result = await sql_tool.execute(Parameters({"sql": sql}))
            content = json.dumps(
                {
                    "columns": list(result._columns),
                    "rows": list(result._rows)[:50],
                    "row_count": result.row_count(),
                },
            )
        except Exception as exc:
            content = f"SQL error: {exc}"
        messages.append({"role": "tool", "tool_call_id": tool_call._id, "content": content})


def _assistant_turn(tool_calls: tuple[LLMToolCall, ...]) -> dict[str, object]:
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": tc._id,
                "type": "function",
                "function": {"name": tc._name, "arguments": json.dumps(tc._arguments)},
            }
            for tc in tool_calls
        ],
    }


def _narrative_spec(text: str) -> dict[str, object]:
    return {
        "root": "answer",
        "elements": {"answer": {"type": "NarrativeText", "props": {"content": text}}},
    }
