from __future__ import annotations

import pytest

from src.questions.exceptions.same_visualization_error import SameVisualizationError


class TestSameVisualizationError:
    def test_can_be_instantiated(self) -> None:
        err = SameVisualizationError("same viz")
        assert str(err) == "same viz"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(SameVisualizationError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(SameVisualizationError):
            raise SameVisualizationError("same")
