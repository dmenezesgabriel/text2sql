from __future__ import annotations

from typing import Protocol

from src.shared.domain.base import EntityId
from src.questions.domain.entities import Question, Questions


class IQuestionRepository(Protocol):
    async def save(self, question: Question) -> None: ...

    async def load(self, question_id: EntityId) -> Question | None: ...

    async def delete(self, question_id: EntityId) -> None: ...

    async def find_all(self) -> Questions: ...
