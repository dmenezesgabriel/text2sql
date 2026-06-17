from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.config import get_stream_writer

from src.chat.application.ports.i_tool_executor import IToolExecutor
from src.chat.domain.spec_validation import validate_spec
from src.chat.domain.value_objects import Parameters
from src.chat.infrastructure.agent_graph.agent_state import AgentState
from src.chat.infrastructure.agent_graph.schemas import (
    GeneratedSQL,
    Intent,
    RepairedSQL,
    VizChoice,
)
from src.chat.infrastructure.agent_graph.spec_builder import (
    SpecBuildError,
    fallback_spec,
    json_default,
    narrative_spec,
    result_summary,
)
from src.chat.infrastructure.agent_graph.spec_builder import (
    build_spec as build_spec_from_state,
)
from src.chat.infrastructure.agent_graph.sql_helpers import sql_repair_hint

_log = logging.getLogger(__name__)
_SAMPLE_ROW_LIMIT = 50
_CONTEXT_WINDOW = 6  # recent messages passed to LLM nodes


def make_classify_intent(model: BaseChatModel) -> Callable[[AgentState], Any]:
    """Node: determine if question is a data query or needs clarification."""
    intent_model = model.with_structured_output(Intent)

    async def classify_intent(state: AgentState) -> dict[str, Any]:
        system = _intent_system(state["schema_context"])
        msgs = _context_messages(state["messages"])
        result: Intent = await intent_model.ainvoke([SystemMessage(system), *msgs])
        return {"intent": result.intent, "clarification_question": result.clarification_question}

    return classify_intent


def make_generate_sql(model: BaseChatModel) -> Callable[[AgentState], Any]:
    """Node: generate DuckDB SQL for the user question."""
    sql_model = model.with_structured_output(GeneratedSQL)

    async def generate_sql(state: AgentState) -> dict[str, Any]:
        system = _sql_system(state["schema_context"])
        msgs = _context_messages(state["messages"])
        result: GeneratedSQL = await sql_model.ainvoke([SystemMessage(system), *msgs])
        return {"sql": result.sql, "sql_retries": 0, "sql_error": ""}

    return generate_sql


def make_execute_sql(executor: IToolExecutor) -> Callable[[AgentState], Any]:
    """Node: run the SQL query against DuckDB and capture the result."""

    async def execute_sql(state: AgentState) -> dict[str, Any]:
        sql = state.get("sql", "")
        get_stream_writer()({"kind": "tool_call", "name": "run_sql", "sql": sql})
        _log.info("execute_sql.attempt", extra={"sql": sql})
        try:
            query_result = await executor.execute(Parameters({"sql": sql}))
            rows = [dict(r) for r in query_result._rows[:_SAMPLE_ROW_LIMIT]]
            serialized = json.dumps(
                {"columns": list(query_result._columns), "rows": rows},
                default=json_default,
            )
            parsed: dict[str, Any] = json.loads(serialized)
            return {"sql_result": parsed, "sql_error": ""}
        except Exception as exc:
            retries = state.get("sql_retries", 0) + 1
            _log.warning(
                "execute_sql.error",
                extra={"sql": sql, "error": str(exc), "retries": retries},
            )
            return {"sql_error": str(exc), "sql_retries": retries, "sql_result": None}

    return execute_sql


def make_repair_sql(model: BaseChatModel) -> Callable[[AgentState], Any]:
    """Node: rewrite failed SQL based on the error and a targeted hint."""
    repair_model = model.with_structured_output(RepairedSQL)

    async def repair_sql(state: AgentState) -> dict[str, Any]:
        hint = sql_repair_hint(state.get("sql_error", ""))
        system = _repair_system(state["schema_context"])
        prompt = _repair_prompt(state.get("sql", ""), state.get("sql_error", ""), hint)
        result: RepairedSQL = await repair_model.ainvoke(
            [SystemMessage(system), HumanMessage(prompt)],
        )
        return {"sql": result.sql}

    return repair_sql


def make_choose_visualization(model: BaseChatModel) -> Callable[[AgentState], Any]:
    """Node: pick the visualization component and column mapping."""
    viz_model = model.with_structured_output(VizChoice)

    async def choose_visualization(state: AgentState) -> dict[str, Any]:
        question = _last_user_content(state["messages"])
        summary = result_summary(state.get("sql_result") or {})
        result: VizChoice = await viz_model.ainvoke(
            [
                SystemMessage(_viz_system()),
                HumanMessage(_viz_prompt(question, summary)),
            ],
        )
        return {
            "viz_component": result.component,
            "label_column": result.label_column,
            "value_column": result.value_column,
            "narrative": result.narrative,
        }

    return choose_visualization


def build_spec_node(state: AgentState) -> dict[str, Any]:
    """Node: deterministically build and validate the json-render spec."""
    try:
        spec = build_spec_from_state(state)
        validate_spec(spec)
    except (SpecBuildError, ValueError) as exc:
        _log.warning("build_spec.fallback", extra={"error": str(exc)})
        spec = fallback_spec(state)
    get_stream_writer()({"kind": "spec", "payload": spec})
    summary = _response_summary(state)
    return {"spec": spec, "messages": [AIMessage(content=summary)]}


def emit_clarification_node(state: AgentState) -> dict[str, Any]:
    """Node: stream a clarification question as a NarrativeText spec."""
    question = state.get("clarification_question") or "Could you provide more details?"
    spec = narrative_spec(question)
    get_stream_writer()({"kind": "spec", "payload": spec})
    return {"spec": spec, "messages": [AIMessage(content=f"Asked for clarification: {question}")]}


# ── Private prompt helpers ────────────────────────────────────────────────────


def _intent_system(schema_context: str) -> str:
    return (
        "Classify the user's message as data_query or clarification_needed.\n\n"
        "Use data_query when the question:\n"
        "- Names a metric, column, or aggregation (sales, revenue, count, avg)\n"
        "- Specifies a chart type (bar chart, line chart, table, metric)\n"
        "- Asks for comparison, ranking, trend, or breakdown over dataset fields\n"
        "- Can be answered with a SQL SELECT on the available data\n\n"
        "Use clarification_needed ONLY when the question is completely unrelated "
        "to data analysis, or there is no way to infer any metric or entity.\n\n"
        "When in doubt, choose data_query — let SQL generation clarify.\n\n"
        f"Available datasets:\n{schema_context}"
    )


def _sql_system(schema_context: str) -> str:
    return (
        "Write a DuckDB SQL SELECT to answer the user's question.\n\n"
        f"Available views:\n{schema_context}\n\n"
        "Rules: quote multi-word column names with double quotes. "
        "Aggregate in SQL (GROUP BY, SUM, AVG). Keep results ≤25 rows with ORDER BY + LIMIT."
    )


def _repair_system(schema_context: str) -> str:
    return (
        "Fix the SQL query based on the error message. "
        "Return only the corrected SQL.\n\n"
        f"Schema:\n{schema_context}"
    )


def _viz_system() -> str:
    return (
        "Choose the best visualization for the SQL result. "
        "Use EXACT column names from the result. Options: "
        "BarChart (compare across categories), LineChart (over time), "
        "PieChart (parts of a whole), Metric (single number), "
        "DataTable (multi-column), NarrativeText (text answer)."
    )


def _repair_prompt(sql: str, error: str, hint: str) -> str:
    return f"Failed SQL:\n{sql}\n\nError: {error}\n\nHint: {hint}"


def _viz_prompt(question: str, summary: str) -> str:
    return f"Question: {question}\n\nResult:\n{summary}"


def _context_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    return messages[-_CONTEXT_WINDOW:]


def _last_user_content(messages: list[BaseMessage]) -> str:
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return str(msg.content)
    return ""


def _response_summary(state: AgentState) -> str:
    component = state.get("viz_component", "")
    sql = state.get("sql", "")
    if not component:
        return "Responded with a clarification request."
    return f"Showed {component}. SQL: {sql}"
