from __future__ import annotations

import pytest

from src.dashboards.exceptions.tile_not_found_error import TileNotFoundError


class TestTileNotFoundError:
    def test_can_be_instantiated(self) -> None:
        err = TileNotFoundError("tile missing")
        assert str(err) == "tile missing"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(TileNotFoundError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(TileNotFoundError):
            raise TileNotFoundError("not found")
