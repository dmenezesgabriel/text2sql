from __future__ import annotations

from src.questions.infrastructure.fastapi.router import create_questions_router


class TestCreateQuestionsRouter:
    def test_router_is_created(self) -> None:
        router = create_questions_router()
        assert router is not None

    def test_router_prefix(self) -> None:
        router = create_questions_router()
        assert router.prefix == "/api/v1/questions"

    def test_router_with_no_use_cases_succeeds(self) -> None:
        router = create_questions_router(
            save_use_case=None,
            drill_use_case=None,
            compare_use_case=None,
        )
        assert router is not None
