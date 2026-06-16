from __future__ import annotations

import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager

import litellm
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

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
from src.shared.infrastructure.logging import REQUEST_ID, setup_logging

setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
_logger = logging.getLogger(__name__)

# LiteLLM prints "Provider List" banners to stderr on every rate-limit retry;
# the retries succeed internally so these are noise.
litellm.suppress_debug_info = True

_DYNAMO_MODELS = [ConversationModel, QuestionModel, DatasetModel, DashboardModel]


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: object) -> Response:
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        token = REQUEST_ID.set(rid)
        try:
            response = await call_next(request)  # type: ignore[arg-type]
            response.headers["X-Request-Id"] = rid
            return response
        finally:
            REQUEST_ID.reset(token)


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
    _logger.info("startup.begin")
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
    except Exception:
        _logger.warning("startup.views_skipped", exc_info=True)

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

    _logger.info("startup.complete")
    yield

    pool.disconnect()
    _logger.info("shutdown.complete")


app = FastAPI(
    title="text2sql",
    version="0.1.0",
    description="Generative Business Intelligence Chat Tool",
    lifespan=lifespan,
)
app.add_middleware(RequestIdMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok"}
