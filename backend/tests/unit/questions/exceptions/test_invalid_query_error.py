from __future__ import annotations

import pytest

from src.questions.exceptions.invalid_query_error import InvalidQueryError


class TestInvalidQueryError:
    def test_can_be_instantiated(self) -> None:
        err = InvalidQueryError("not a SELECT")
        assert str(err) == "not a SELECT"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(InvalidQueryError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(InvalidQueryError):
            raise InvalidQueryError("invalid")
