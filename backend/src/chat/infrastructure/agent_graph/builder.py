from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from src.chat.application.ports.i_tool_executor import IToolExecutor
from src.chat.infrastructure.agent_graph.agent_state import AgentState
from src.chat.infrastructure.agent_graph.edges import route_intent, route_sql_result
from src.chat.infrastructure.agent_graph.nodes import (
    build_spec_node,
    emit_clarification_node,
    make_choose_visualization,
    make_classify_intent,
    make_execute_sql,
    make_generate_sql,
    make_repair_sql,
)


def build_agent_graph(
    model: BaseChatModel,
    executor: IToolExecutor,
    checkpointer: BaseCheckpointSaver,
) -> object:
    """Compile the text2sql agent graph.

    Example: graph = build_agent_graph(model, executor, InMemorySaver())
    """
    builder = StateGraph(AgentState)

    builder.add_node("classify_intent", make_classify_intent(model))
    builder.add_node("generate_sql", make_generate_sql(model))
    builder.add_node("execute_sql", make_execute_sql(executor))
    builder.add_node("repair_sql", make_repair_sql(model))
    builder.add_node("choose_visualization", make_choose_visualization(model))
    builder.add_node("build_spec", build_spec_node)
    builder.add_node("emit_clarification", emit_clarification_node)

    builder.set_entry_point("classify_intent")

    builder.add_conditional_edges(
        "classify_intent",
        route_intent,
        {"generate_sql": "generate_sql", "emit_clarification": "emit_clarification"},
    )
    builder.add_edge("generate_sql", "execute_sql")
    builder.add_conditional_edges(
        "execute_sql",
        route_sql_result,
        {
            "choose_visualization": "choose_visualization",
            "repair_sql": "repair_sql",
            "emit_clarification": "emit_clarification",
        },
    )
    builder.add_edge("repair_sql", "execute_sql")
    builder.add_edge("choose_visualization", "build_spec")
    builder.add_edge("build_spec", END)
    builder.add_edge("emit_clarification", END)

    return builder.compile(checkpointer=checkpointer)
