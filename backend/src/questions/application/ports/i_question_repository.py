from __future__ import annotations

from typing import Protocol

from src.questions.domain.entities import Question, Questions
from src.shared.domain.base import EntityId


class IQuestionRepository(Protocol):
    def save(self, question: Question) -> None: ...

    def load(self, question_id: EntityId) -> Question | None: ...

    def delete(self, question_id: EntityId) -> None: ...

    def find_all(self) -> Questions: ...
