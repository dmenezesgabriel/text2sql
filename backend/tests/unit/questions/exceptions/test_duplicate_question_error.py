from __future__ import annotations

import pytest

from src.questions.exceptions.duplicate_question_error import DuplicateQuestionError


class TestDuplicateQuestionError:
    def test_can_be_instantiated(self) -> None:
        err = DuplicateQuestionError("already exists")
        assert str(err) == "already exists"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(DuplicateQuestionError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(DuplicateQuestionError):
            raise DuplicateQuestionError("duplicate")
