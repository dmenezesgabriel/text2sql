from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.composition_root import ComposeConfig, compose
from src.shared.infrastructure.duckdb_pool import DuckDBPool
from src.shared.infrastructure.dynamo_models import (
    ConversationModel,
    DashboardModel,
    DatasetModel,
    QuestionModel,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    for model in [ConversationModel, QuestionModel, DatasetModel, DashboardModel]:
        if not model.exists():
            model.create_table(
                read_capacity_units=5,
                write_capacity_units=5,
                billing_mode="PAY_PER_REQUEST",
            )

    pool = DuckDBPool(
        database_path=os.getenv("DUCKDB_PATH", ":memory:"),
    )
    pool.connect()

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
