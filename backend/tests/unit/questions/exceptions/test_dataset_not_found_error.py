from __future__ import annotations

import pytest

from src.questions.exceptions.dataset_not_found_error import DatasetNotFoundError


class TestDatasetNotFoundError:
    def test_can_be_instantiated(self) -> None:
        err = DatasetNotFoundError("dataset missing")
        assert str(err) == "dataset missing"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(DatasetNotFoundError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(DatasetNotFoundError):
            raise DatasetNotFoundError("not found")
