from __future__ import annotations

import pytest

from src.dashboards.exceptions.self_filter_error import SelfFilterError


class TestSelfFilterError:
    def test_can_be_instantiated(self) -> None:
        err = SelfFilterError("cannot self-filter")
        assert str(err) == "cannot self-filter"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(SelfFilterError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(SelfFilterError):
            raise SelfFilterError("self filter")
