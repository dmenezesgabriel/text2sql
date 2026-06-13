from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.composition_root import ComposeConfig, compose
from src.datasets.infrastructure.duckdb_executor import DuckDBExecutor
from src.datasets.infrastructure.dynamo_repository import DynamoDatasetRepository
from src.shared.infrastructure.duckdb_pool import DuckDBPool
from src.shared.infrastructure.dynamo_models import (
    ConversationModel,
    DashboardModel,
    DatasetModel,
    QuestionModel,
)

_DYNAMO_MODELS = [ConversationModel, QuestionModel, DatasetModel, DashboardModel]


async def _ensure_dynamo_tables(retries: int = 15, delay: float = 2.0) -> None:
    for attempt in range(retries):
        try:
            for model in _DYNAMO_MODELS:
                if not model.exists():
                    model.create_table(billing_mode="PAY_PER_REQUEST")
            return
        except Exception:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _ensure_dynamo_tables()

    pool = DuckDBPool(database_path=os.getenv("DUCKDB_PATH", ":memory:"))
    pool.connect()
    pool.configure_s3(
        endpoint=os.getenv("S3_ENDPOINT", "http://localhost:9000"),
        key=os.getenv("S3_ACCESS_KEY_ID", "minioadmin"),
        secret=os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin"),
    )

    # Recreate S3 views for all persisted datasets (idempotent OR REPLACE)
    executor = DuckDBExecutor(pool)
    try:
        dataset_repo = DynamoDatasetRepository()
        for ds in dataset_repo.find_all().to_list():
            if ds._configuration._location.value:
                await executor.create_view_from_s3(
                    ds._identity._id,
                    ds._configuration._location.value,
                )
    except Exception as exc:
        print(f"[startup] Could not recreate dataset views: {exc}")

    composition = compose(
        pool=pool,
        config=ComposeConfig(
            llm_model_name=os.getenv("LLM_MODEL", "gpt-4o"),
            summarizer_model_name=os.getenv("SUMMARIZER_MODEL", "gpt-4o-mini"),
            token_limit=int(os.getenv("TOKEN_LIMIT", "100000")),
        ),
    )

    app.include_router(composition.chat_router)
    app.include_router(composition.questions_router)
    app.include_router(composition.dashboards_router)
    app.include_router(composition.datasets_router)

    yield

    pool.disconnect()


app = FastAPI(
    title="text2sql",
    version="0.1.0",
    description="Generative Business Intelligence Chat Tool",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok"}
