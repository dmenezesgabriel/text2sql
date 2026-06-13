from __future__ import annotations

from fastapi import FastAPI

from src.agent.infrastructure.fastapi.router import create_chat_router
from src.questions.infrastructure.fastapi.router import create_questions_router
from src.dashboards.infrastructure.fastapi.router import create_dashboards_router
from src.datasets.infrastructure.fastapi.router import create_datasets_router

app = FastAPI(
    title="text2sql",
    version="0.1.0",
    description="Generative Business Intelligence Chat Tool",
)

app.include_router(create_chat_router())
app.include_router(create_questions_router())
app.include_router(create_dashboards_router())
app.include_router(create_datasets_router())


@app.get("/health")
async def health():
    return {"status": "ok"}
