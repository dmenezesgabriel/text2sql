from __future__ import annotations

from src.questions.domain.entities import Question, Questions
from src.questions.infrastructure.fastapi.router import create_questions_router
from src.shared.domain.base import EntityId


class _FakeRepo:
    def save(self, question: Question) -> None:
        pass

    def load(self, question_id: EntityId) -> Question | None:
        return None

    def delete(self, question_id: EntityId) -> None:
        pass

    def find_all(self) -> Questions:
        return Questions()


class _FakeSaveUseCase:
    pass


class _FakeDrillUseCase:
    pass


def _make_router():
    return create_questions_router(
        question_repo=_FakeRepo(),  # type: ignore[arg-type]
        save_use_case=_FakeSaveUseCase(),  # type: ignore[arg-type]
        drill_use_case=_FakeDrillUseCase(),  # type: ignore[arg-type]
    )


class TestCreateQuestionsRouter:
    def test_router_is_created(self) -> None:
        router = _make_router()
        assert router is not None

    def test_router_prefix(self) -> None:
        router = _make_router()
        assert router.prefix == "/api/v1/questions"

    def test_router_has_list_and_create_routes(self) -> None:
        router = _make_router()
        paths = [r.path for r in router.routes]
        assert "/api/v1/questions" in paths

    def test_router_tags_contains_questions(self) -> None:
        # Kills mutmut_3/5/8/9: tags=None/missing/"XXquestionsXX"/"QUESTIONS"
        router = _make_router()
        assert "questions" in router.tags

    def test_router_tags_no_xx(self) -> None:
        router = _make_router()
        assert not any("XX" in str(t) for t in (router.tags or []))

    def test_router_tags_lowercase(self) -> None:
        router = _make_router()
        tags = router.tags or []
        assert all(t == t.lower() for t in tags)
