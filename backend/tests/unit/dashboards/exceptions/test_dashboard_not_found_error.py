from __future__ import annotations

import pytest

from src.dashboards.exceptions.dashboard_not_found_error import DashboardNotFoundError


class TestDashboardNotFoundError:
    def test_can_be_instantiated(self) -> None:
        err = DashboardNotFoundError("not found")
        assert str(err) == "not found"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(DashboardNotFoundError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(DashboardNotFoundError):
            raise DashboardNotFoundError("missing")
