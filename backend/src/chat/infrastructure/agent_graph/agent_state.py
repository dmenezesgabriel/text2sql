from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Graph state for the text2sql agent pipeline."""

    messages: Annotated[list[BaseMessage], add_messages]
    schema_context: str
    dataset_views: dict[str, str]  # view_name → dataset_id
    intent: str  # "data_query" | "clarification_needed"
    clarification_question: str
    sql: str
    sql_result: dict[str, Any] | None  # {"columns": [...], "rows": [...]}
    sql_error: str
    sql_retries: int
    viz_component: str
    label_column: str
    value_column: str
    narrative: str
    spec: dict[str, Any] | None
