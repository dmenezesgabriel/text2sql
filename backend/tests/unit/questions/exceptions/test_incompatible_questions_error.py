from __future__ import annotations

import pytest

from src.questions.exceptions.incompatible_questions_error import IncompatibleQuestionsError


class TestIncompatibleQuestionsError:
    def test_can_be_instantiated(self) -> None:
        err = IncompatibleQuestionsError("questions incompatible")
        assert str(err) == "questions incompatible"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(IncompatibleQuestionsError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(IncompatibleQuestionsError):
            raise IncompatibleQuestionsError("incompatible")
