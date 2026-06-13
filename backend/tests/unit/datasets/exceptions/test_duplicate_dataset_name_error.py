from __future__ import annotations

import pytest

from src.datasets.exceptions.duplicate_dataset_name_error import DuplicateDatasetNameError


class TestDuplicateDatasetNameError:
    def test_can_be_instantiated(self) -> None:
        err = DuplicateDatasetNameError("already exists")
        assert str(err) == "already exists"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(DuplicateDatasetNameError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(DuplicateDatasetNameError):
            raise DuplicateDatasetNameError("duplicate")
