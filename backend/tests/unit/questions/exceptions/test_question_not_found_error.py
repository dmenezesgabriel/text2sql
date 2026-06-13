from __future__ import annotations

import pytest

from src.questions.exceptions.question_not_found_error import QuestionNotFoundError


class TestQuestionNotFoundError:
    def test_can_be_instantiated(self) -> None:
        err = QuestionNotFoundError("question missing")
        assert str(err) == "question missing"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(QuestionNotFoundError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(QuestionNotFoundError):
            raise QuestionNotFoundError("not found")
