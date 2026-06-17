from __future__ import annotations

from src.chat.infrastructure.agent_graph.agent_state import AgentState

_MAX_SQL_RETRIES = 3


def route_intent(state: AgentState) -> str:
    """Route after classify_intent: data query or clarification."""
    if state.get("intent") == "clarification_needed":
        return "emit_clarification"
    return "generate_sql"


def route_sql_result(state: AgentState) -> str:
    """Route after execute_sql: success, retry, or too many errors."""
    if not state.get("sql_error"):
        return "choose_visualization"
    if state.get("sql_retries", 0) >= _MAX_SQL_RETRIES:
        return "emit_clarification"
    return "repair_sql"
