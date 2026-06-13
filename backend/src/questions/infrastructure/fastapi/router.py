from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.questions.application.use_cases.compare_questions import (
    CompareQuestionsUseCase,
)
from src.questions.application.use_cases.drill_down_question import (
    DrillDownQuestionUseCase,
)
from src.questions.application.use_cases.save_question_from_chat import (
    SaveQuestionFromChatUseCase,
)


def create_questions_router(
    save_use_case: SaveQuestionFromChatUseCase | None = None,
    drill_use_case: DrillDownQuestionUseCase | None = None,
    compare_use_case: CompareQuestionsUseCase | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/questions", tags=["questions"])

    @router.get("")
    async def list_questions():
        return {"questions": []}

    @router.post("")
    async def create_question(body: dict):
        if save_use_case is None:
            return JSONResponse(status_code=501, content={"error": "Not wired"})
        return {"status": "ok"}

    @router.get("/{question_id}")
    async def get_question(question_id: str):
        return {"id": question_id}

    @router.delete("/{question_id}")
    async def delete_question(question_id: str):
        return {"status": "deleted"}

    @router.post("/{question_id}/drill")
    async def drill_question(question_id: str, body: dict):
        return {"status": "drilled"}

    @router.post("/compare")
    async def compare_questions(body: dict):
        return {"status": "compared"}

    return router
