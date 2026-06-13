from __future__ import annotations

from dataclasses import dataclass

from src.questions.application.ports.i_question_repository import IQuestionRepository
from src.questions.domain.entities import Question
from src.questions.domain.value_objects import VizDecision
from src.questions.exceptions.question_not_found_error import QuestionNotFoundError
from src.shared.domain.base import EntityId


@dataclass(frozen=True)
class DrillDownRequest:
    _source_id: EntityId
    _column: str
    _value: str
    _change_viz: bool = False
    _new_viz: VizDecision | None = None


class DrillDownQuestionUseCase:
    def __init__(self, questions: IQuestionRepository) -> None:
        self._questions = questions

    def execute(self, request: DrillDownRequest) -> Question:
        source = self._questions.load(request._source_id)
        if source is None:
            msg = f"Question {request._source_id.value} not found"
            raise QuestionNotFoundError(msg)

        derived = source.derive_drill_down(
            column=request._column,
            value=request._value,
        )

        if request._change_viz and request._new_viz is not None:
            derived.change_decision(request._new_viz)

        self._questions.save(derived)
        return derived
