from __future__ import annotations

from src.agent.domain.value_objects import Parameters
from src.agent.infrastructure.tools.viz_selector import VizSelectorTool


class TestVizSelectorTool:
    def setup_method(self) -> None:
        self.tool = VizSelectorTool()

    async def test_returns_text_when_no_rows(self) -> None:
        result = await self.tool.execute(Parameters({"columns": [], "row_count": 0}))
        assert result._rows[0]["kind"] == "text"

    async def test_returns_table_when_row_count_exceeds_ten(self) -> None:
        result = await self.tool.execute(Parameters({"columns": [], "row_count": 11}))
        assert result._rows[0]["kind"] == "table"

    async def test_returns_chart_boundary_ten_rows(self) -> None:
        result = await self.tool.execute(Parameters({"columns": [], "row_count": 10}))
        assert result._rows[0]["kind"] == "chart"

    async def test_returns_chart_for_few_rows(self) -> None:
        result = await self.tool.execute(Parameters({"columns": [], "row_count": 5}))
        assert result._rows[0]["kind"] == "chart"

    async def test_returns_chart_for_single_row(self) -> None:
        result = await self.tool.execute(Parameters({"columns": [], "row_count": 1}))
        assert result._rows[0]["kind"] == "chart"

    async def test_result_has_single_kind_column(self) -> None:
        result = await self.tool.execute(Parameters({"columns": [], "row_count": 0}))
        assert result._columns == ("kind",)
        assert len(result._rows) == 1

    async def test_name_is_viz_selector(self) -> None:
        assert self.tool.name.value == "viz_selector"
