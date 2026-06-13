from __future__ import annotations

import pytest

from src.datasets.exceptions.unsupported_format_error import UnsupportedFormatError


class TestUnsupportedFormatError:
    def test_can_be_instantiated(self) -> None:
        err = UnsupportedFormatError("format not supported")
        assert str(err) == "format not supported"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(UnsupportedFormatError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(UnsupportedFormatError):
            raise UnsupportedFormatError("unsupported")
