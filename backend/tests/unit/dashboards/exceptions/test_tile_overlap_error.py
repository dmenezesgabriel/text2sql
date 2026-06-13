from __future__ import annotations

import pytest

from src.dashboards.exceptions.tile_overlap_error import TileOverlapError


class TestTileOverlapError:
    def test_can_be_instantiated(self) -> None:
        err = TileOverlapError("tiles overlap")
        assert str(err) == "tiles overlap"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(TileOverlapError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(TileOverlapError):
            raise TileOverlapError("overlap")
