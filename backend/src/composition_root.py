from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter
from langgraph.checkpoint.memory import InMemorySaver

from src.chat.application.use_cases.handle_chat_message import (
    AgentConfig,
    HandleChatMessageUseCase,
)
from src.chat.infrastructure.agent_graph.builder import build_agent_graph
from src.chat.infrastructure.chat_model import build_chat_model
from src.chat.infrastructure.dynamo_checkpointer import DynamoCheckpointer
from src.chat.infrastructure.dynamo_conversation_repository import DynamoConversationRepository
from src.chat.infrastructure.fastapi.router import create_chat_router
from src.chat.infrastructure.langgraph_orchestrator import LangGraphOrchestrator
from src.chat.infrastructure.tools.sql_generator import SQLGeneratorTool
from src.dashboards.application.use_cases.apply_cross_filter import ApplyCrossFilterUseCase
from src.dashboards.application.use_cases.compose_dashboard import (
    ComposeDashboardFromQuestionsUseCase,
)
from src.dashboards.infrastructure.dynamo_repository import DynamoDashboardRepository
from src.dashboards.infrastructure.fastapi.router import create_dashboards_router
from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.datasets.application.use_cases.register_s3_dataset import RegisterS3DatasetUseCase
from src.datasets.infrastructure.duckdb_executor import DuckDBExecutor
from src.datasets.infrastructure.dynamo_repository import DynamoDatasetRepository
from src.datasets.infrastructure.fastapi.router import create_datasets_router
from src.datasets.infrastructure.query_executor import DuckDBQueryExecutor
from src.questions.application.use_cases.drill_down_question import DrillDownQuestionUseCase
from src.questions.application.use_cases.save_question_from_chat import SaveQuestionFromChatUseCase
from src.questions.infrastructure.dynamo_repository import DynamoQuestionRepository
from src.questions.infrastructure.fastapi.router import create_questions_router
from src.shared.domain.base import EntityId
from src.shared.infrastructure.duckdb_pool import DuckDBPool


class DatasetExistenceAdapter:
    def __init__(self, repo: IDatasetRepository) -> None:
        self._repo = repo

    def exists(self, dataset_id: EntityId) -> bool:
        return self._repo.load(dataset_id) is not None


@dataclass
class ComposeConfig:
    llm_model_name: str = "gpt-4o"
    use_dynamo_checkpointer: bool = False


@dataclass
class Composition:
    chat_router: APIRouter
    questions_router: APIRouter
    dashboards_router: APIRouter
    datasets_router: APIRouter
    duckdb: DuckDBPool


def compose(pool: DuckDBPool, config: ComposeConfig | None = None) -> Composition:
    cfg = config or ComposeConfig()

    # ── Repositories ──
    question_repo = DynamoQuestionRepository()
    dataset_repo = DynamoDatasetRepository()
    dashboard_repo = DynamoDashboardRepository(questions=question_repo)
    conversation_repo = DynamoConversationRepository()

    # ── Query engine ──
    engine = DuckDBExecutor(pool)
    query_executor = DuckDBQueryExecutor(engine)

    # ── SQL tool (injected into graph) ──
    sql_tool = SQLGeneratorTool(engine)

    # ── LangGraph checkpointer ──
    checkpointer = DynamoCheckpointer() if cfg.use_dynamo_checkpointer else InMemorySaver()

    # ── Agent graph (built once at startup) ──
    graph = build_agent_graph(
        model=build_chat_model(cfg.llm_model_name),
        executor=sql_tool,
        checkpointer=checkpointer,
    )
    orchestrator = LangGraphOrchestrator(graph=graph, datasets=dataset_repo)

    # ── Use Cases: Agent ──
    chat_use_case = HandleChatMessageUseCase(
        conversations=conversation_repo,
        agent=AgentConfig(_orchestrator=orchestrator),
    )

    # ── Use Cases: Questions ──
    save_question_use_case = SaveQuestionFromChatUseCase(
        questions=question_repo,
        datasets=DatasetExistenceAdapter(dataset_repo),
    )
    drill_question_use_case = DrillDownQuestionUseCase(questions=question_repo)

    # ── Use Cases: Dashboards ──
    compose_dashboard_use_case = ComposeDashboardFromQuestionsUseCase(
        dashboards=dashboard_repo,
        questions=question_repo,
    )
    apply_cross_filter_use_case = ApplyCrossFilterUseCase(
        dashboards=dashboard_repo,
        executor=query_executor,
    )

    # ── Use Cases: Datasets ──
    register_s3_use_case = RegisterS3DatasetUseCase(datasets=dataset_repo, engine=engine)

    # ── Routers ──
    return Composition(
        chat_router=create_chat_router(chat_use_case),
        questions_router=create_questions_router(
            question_repo=question_repo,
            save_use_case=save_question_use_case,
            drill_use_case=drill_question_use_case,
        ),
        dashboards_router=create_dashboards_router(
            dashboard_repo=dashboard_repo,
            compose_use_case=compose_dashboard_use_case,
            filter_use_case=apply_cross_filter_use_case,
        ),
        datasets_router=create_datasets_router(
            register_use_case=register_s3_use_case,
            dataset_repo=dataset_repo,
            engine=engine,
        ),
        duckdb=pool,
    )
