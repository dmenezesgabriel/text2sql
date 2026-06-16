from __future__ import annotations

import datetime
import json
import logging
import re
from collections.abc import AsyncIterator, Callable, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from langchain_core.language_models import BaseChatModel
from langgraph.config import get_stream_writer
from langgraph.prebuilt import create_react_agent

from src.chat.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.chat.application.ports.i_tool_executor import IToolExecutor
from src.chat.application.ports.i_tool_kit import IToolKit
from src.chat.domain.entities import Conversation, Message
from src.chat.domain.value_objects import (
    AgentEvent,
    ErrorEvent,
    MessageRole,
    Parameters,
    SpecFragmentEvent,
    ThinkingEvent,
    ToolCallEvent,
    ToolName,
)
from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.datasets.domain.entities import Dataset
from src.shared.domain.base import QueryResult, ResponseKind

_log = logging.getLogger(__name__)

_CHART_COMPONENTS = ("BarChart", "LineChart", "PieChart")
_VALID_COMPONENTS = (*_CHART_COMPONENTS, "DataTable", "Metric", "NarrativeText")
_SAMPLE_ROW_LIMIT = 50
_MAX_SQL_RETRIES = 3

_SYSTEM_TEMPLATE = """\
You are a senior BI analyst. Answer the user's question about their data by \
querying it with DuckDB SQL and choosing the clearest visualization.

## Available views (DuckDB)
{schemas}

## Workflow
1. If the question is too vague (no clear metric or dataset), call \
`request_clarification` with one short question — do NOT run SQL.
2. Call `run_sql` with a single DuckDB SELECT against the views above. Aggregate \
in SQL (GROUP BY, SUM, AVG, COUNT) so the result is already chart-ready. Keep \
chart results small (roughly 25 rows or fewer); add ORDER BY and LIMIT.
3. Inspect the returned columns and rows, then present the answer with exactly \
one of `build_visualization` or `write_narrative`.

## SQL repair
If `run_sql` returns an error, fix the SQL based on the repair hint and retry. \
After {max_retries} failed attempts call `request_clarification` explaining \
what you cannot determine.

## Choosing a visualization
- BarChart: compare a numeric measure across categories.
- LineChart: a measure over an ordered/time dimension.
- PieChart: parts of a whole (few categories).
- Metric: a single headline number (one row, one measure).
- DataTable: detailed or multi-column results.
- write_narrative: a text explanation when no data viz fits.

## How presentation works
You do NOT pass any data. The backend fills the chart from your actual SQL \
result. For charts pass `label_column` (the category/time column) and \
`value_column` (the numeric measure). For Metric pass `value_column`. Use the \
EXACT column names from the run_sql result, including any AS aliases. If a \
column name is rejected, re-read the result columns and call the tool again \
with a correct name.
"""


@dataclass(frozen=True)
class _VizRequest:
    """A presentation choice the model makes; the backend supplies the data."""

    component: str
    title: str
    label_column: str
    value_column: str
    content: str


@dataclass(frozen=True)
class _LastQuery:
    sql: str
    result: QueryResult


@dataclass
class _ExecutionScratch:
    """Bundles mutable per-request SQL execution state."""

    _last: _LastQuery | None = None
    _sql_failures: int = 0


class _RunState:
    """Per-request scratch shared between the agent tools."""

    def __init__(self, dataset_views: dict[str, str]) -> None:
        self._dataset_views = dataset_views
        self._scratch = _ExecutionScratch()

    def record(self, sql: str, result: QueryResult) -> None:
        self._scratch._last = _LastQuery(sql, result)

    def record_failure(self) -> int:
        self._scratch._sql_failures += 1
        return self._scratch._sql_failures

    def latest(self) -> _LastQuery | None:
        return self._scratch._last

    def dataset_id(self) -> str:
        sql = self._scratch._last.sql if self._scratch._last else ""
        for view, dataset_id in self._dataset_views.items():
            if view in sql:
                return dataset_id
        return ""


class _BuildError(Exception):
    """Raised when a visualization cannot be built from the current result."""


class LangGraphOrchestrator(IAgentOrchestrator):
    def __init__(self, model: BaseChatModel, datasets: IDatasetRepository) -> None:
        self._model = model
        self._datasets = datasets

    async def run(
        self,
        message: Message,
        conversation: Conversation,
        toolkit: IToolKit,
    ) -> AsyncIterator[AgentEvent]:
        sql_tool = toolkit.find(ToolName("sql_generator"))
        if sql_tool is None:
            yield ErrorEvent(_message="sql_generator tool not registered in toolkit")
            return

        datasets = self._datasets.find_all().to_list()
        state = _RunState(
            {f"ds_{d._identity._id.value.hex}": str(d._identity._id.value) for d in datasets},
        )
        agent = create_react_agent(
            self._model,
            tools=_build_tools(sql_tool, state),
            prompt=_SYSTEM_TEMPLATE.format(
                schemas=_schema_context(datasets),
                max_retries=_MAX_SQL_RETRIES,
            ),
        )

        yield ThinkingEvent("Analyzing your question...")
        async for event in _stream_agent(agent, _history(conversation)):
            yield event


def _agent_error_message(exc: Exception) -> str:
    exc_type = type(exc).__name__
    _log.error("agent.error", extra={"exc_type": exc_type, "exc": str(exc)}, exc_info=True)
    if "RateLimitError" in exc_type or "rate_limit" in str(exc).lower():
        return "Rate limit reached. Please wait a moment and try again."
    return f"The agent could not complete the request: {exc_type}"


async def _stream_agent(
    agent: Any,
    messages: list[dict[str, object]],
) -> AsyncIterator[AgentEvent]:
    produced_spec = False
    final_text = ""
    try:
        async for mode, chunk in agent.astream(
            {"messages": messages},
            stream_mode=["custom", "values"],
        ):
            if mode == "values":
                final_text = _last_text(chunk) or final_text
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
        fallback = final_text or "I wasn't able to produce a result for that question."
        yield SpecFragmentEvent(_payload=_narrative_spec(fallback))


def _build_tools(sql_tool: IToolExecutor, state: _RunState) -> Sequence[Callable[..., Any]]:
    def request_clarification(question: str) -> str:
        """Ask the user for more information when their question is too vague.

        Call this INSTEAD of run_sql when you cannot determine what to query.
        Example: request_clarification("Which product category are you asking about?")
        """
        get_stream_writer()({"kind": "spec", "payload": _narrative_spec(question)})
        return "Clarification sent to user."

    async def run_sql(sql: str, reasoning: str = "") -> str:
        """Execute a DuckDB SELECT against the dataset views and return the result.

        Returns JSON with `columns`, sample `rows`, and `row_count`. Example:
        run_sql(sql="SELECT region, SUM(amount) AS revenue FROM ds_x GROUP BY region").
        """
        _log.info("run_sql.attempt", extra={"sql": sql})
        get_stream_writer()({"kind": "tool_call", "name": "run_sql", "sql": sql})
        try:
            result = await sql_tool.execute(Parameters({"sql": sql}))
            rows = [dict(r) for r in result._rows[:_SAMPLE_ROW_LIMIT]]
            state.record(sql, result)
            return json.dumps(
                {"columns": list(result._columns), "rows": rows, "row_count": result.row_count()},
                default=_json_default,
            )
        except Exception as exc:
            failures = state.record_failure()
            hint = _sql_repair_hint(str(exc))
            _log.warning(
                "run_sql.error",
                extra={"sql": sql, "error": str(exc), "attempt": failures},
            )
            if failures >= _MAX_SQL_RETRIES:
                return (
                    f"SQL error (attempt {failures}/{_MAX_SQL_RETRIES}): {exc}\n"
                    "Maximum retries reached. Call request_clarification to ask the user."
                )
            return f"SQL error (attempt {failures}/{_MAX_SQL_RETRIES}): {exc}\nRepair hint: {hint}"

    def build_visualization(component: str, label_column: str = "", value_column: str = "") -> str:
        """Present the last run_sql result as a chart, metric, or table.

        `component` is one of BarChart, LineChart, PieChart, Metric, DataTable.
        Pass `label_column` + `value_column` for charts and `value_column` for
        Metric, using exact column names from the result. The backend fills the
        data — do not pass raw rows.
        """
        request = _VizRequest(
            component=component,
            title=_default_title(component, label_column, value_column),
            label_column=label_column,
            value_column=value_column,
            content="",
        )
        return _emit_spec(state, request)

    def write_narrative(content: str) -> str:
        """Present a plain-text answer when no chart or table fits the question."""
        request = _VizRequest("NarrativeText", "", "", "", content)
        return _emit_spec(state, request)

    return [request_clarification, run_sql, build_visualization, write_narrative]


_SQL_ERROR_HINTS: list[tuple[tuple[str, ...], str]] = [
    (("column", "not found"), "Column name is wrong; use exact names from the schema."),
    (("table", "not found"), "View name is wrong; use only ds_XXXX names from the schema."),
    (("table", "does not exist"), "View name is wrong; use only ds_XXXX names from the schema."),
    (("syntax error",), "Syntax error; check commas, keywords, or unsupported functions."),
    (("ambiguous",), "Ambiguous column; qualify with ds_xxx.column_name."),
    (("type", "cast"), "Type mismatch; use CAST(col AS DOUBLE) or TRY_CAST."),
]
_SQL_HINT_FALLBACK = "Review the SQL for typos or unsupported DuckDB syntax and retry."


def _sql_repair_hint(error: str) -> str:
    """Return a targeted fix hint based on common DuckDB SQL errors."""
    err = error.lower()
    hint = next((h for patterns, h in _SQL_ERROR_HINTS if all(p in err for p in patterns)), None)
    return hint or _SQL_HINT_FALLBACK


def _emit_spec(state: _RunState, request: _VizRequest) -> str:
    try:
        spec = _spec_from_result(state, request)
    except _BuildError as exc:
        return f"ERROR: {exc}"
    get_stream_writer()({"kind": "spec", "payload": spec})
    return "Visualization built successfully."


def _spec_from_result(state: _RunState, request: _VizRequest) -> dict[str, object]:
    if request.component not in _VALID_COMPONENTS:
        msg = f"Unknown component {request.component!r}. Choose one of {list(_VALID_COMPONENTS)}."
        raise _BuildError(msg)
    if request.component == "NarrativeText":
        props: dict[str, object] = {"content": request.content or "No answer."}
        return _spec(request, props, state)
    last = state.latest()
    if last is None:
        msg = "No query result available. Call run_sql before presenting a result."
        raise _BuildError(msg)
    return _spec(request, _viz_props(request, last.result), state)


def _viz_props(request: _VizRequest, result: QueryResult) -> dict[str, object]:
    if request.component == "DataTable":
        columns = [{"key": c, "header": c} for c in result._columns]
        return {"title": request.title, "columns": columns, "rows": [dict(r) for r in result._rows]}
    if request.component == "Metric":
        _require_column(request.value_column, result)
        value = _number(result._rows[0][request.value_column]) if result._rows else 0.0
        metric: dict[str, object] = {
            "label": request.title or request.value_column,
            "value": _format_number(value),
        }
        return metric
    return _chart_props(request, result)


def _chart_props(request: _VizRequest, result: QueryResult) -> dict[str, object]:
    _require_column(request.label_column, result)
    _require_column(request.value_column, result)
    data = [
        {"label": str(row[request.label_column]), "value": _number(row[request.value_column])}
        for row in result._rows
    ]
    props: dict[str, object] = {"title": request.title, "data": data}
    if request.component != "PieChart":
        props["xAxis"] = request.label_column
        props["yAxis"] = request.value_column
    return props


def _require_column(column: str, result: QueryResult) -> None:
    if column in result._columns:
        return
    msg = f"Column {column!r} not in result. Available columns: {list(result._columns)}."
    raise _BuildError(msg)


def _number(value: object) -> float:
    if isinstance(value, bool):
        msg = f"Expected a numeric value, got boolean {value!r}."
        raise _BuildError(msg)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError as exc:
        msg = f"Value {value!r} is not numeric; pick a numeric value_column."
        raise _BuildError(msg) from exc


def _format_number(value: float) -> str:
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.2f}"


def _json_default(obj: object) -> object:
    """Serialize DuckDB native types that json.dumps can't handle by default."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    msg = f"Object of type {type(obj).__name__} is not JSON serializable"
    raise TypeError(msg)


def _default_title(component: str, label_column: str, value_column: str) -> str:
    if component == "Metric":
        return _humanize(value_column)
    if component in _CHART_COMPONENTS and label_column and value_column:
        return f"{_humanize(value_column)} by {_humanize(label_column)}"
    return ""


def _humanize(column: str) -> str:
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", column).replace("_", " ")
    return " ".join(spaced.split()).title()


def _spec(request: _VizRequest, props: dict[str, object], state: _RunState) -> dict[str, object]:
    last = state.latest()
    return {
        "root": "main",
        "elements": {"main": {"type": request.component, "props": props}},
        "meta": {
            "title": request.title,
            "sql": last.sql if last else "",
            "dataset_id": state.dataset_id(),
            "format": _format_kind(request.component).name,
        },
    }


def _format_kind(component: str) -> ResponseKind:
    if component == "DataTable":
        return ResponseKind.TABLE
    if component == "NarrativeText":
        return ResponseKind.TEXT
    return ResponseKind.CHART


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


def _history(conversation: Conversation) -> list[dict[str, object]]:
    return [
        {"role": m._identity._role.name.lower(), "content": m._body._content.value}
        for m in conversation._history.to_list()
        if not m.is_from(MessageRole.SYSTEM)
    ]


def _last_text(state_chunk: object) -> str:
    messages = state_chunk.get("messages") if isinstance(state_chunk, dict) else None
    if not isinstance(messages, list):
        return ""
    texts = [
        message.content
        for message in messages
        if getattr(message, "type", "") == "ai"
        and isinstance(getattr(message, "content", None), str)
        and message.content
    ]
    return texts[-1] if texts else ""


def _schema_context(datasets: list[Dataset]) -> str:
    lines = [
        f"View: ds_{d._identity._id.value.hex}  (dataset: {d.display_name()})\n"
        f"Columns: {d.columns_summary()}"
        for d in datasets
    ]
    return "\n\n".join(lines) if lines else "No datasets registered yet."


def _narrative_spec(text: str) -> dict[str, object]:
    return {
        "root": "answer",
        "elements": {"answer": {"type": "NarrativeText", "props": {"content": text}}},
    }
