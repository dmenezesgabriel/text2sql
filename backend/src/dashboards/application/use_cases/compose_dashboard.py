from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from src.shared.domain.base import EntityId, AuditRecord, CreatedAt, UpdatedAt

from src.dashboards.domain.entities import (
    Dashboard, DashboardIdentity, DashboardLayout,
    DashboardTile, TileIdentity, TilePosition, Tiles,
    DashboardTitle,
    TileNotFoundError,
)
from src.dashboards.application.ports.i_dashboard_repository import (
    IDashboardRepository,
)
from src.questions.application.ports.i_question_repository import (
    IQuestionRepository,
)


@dataclass(frozen=True)
class ComposeDashboardRequest:
    _title: DashboardTitle
    _question_ids: list[EntityId]
    _auto_bind_filters: bool = False


class ComposeDashboardFromQuestionsUseCase:
    def __init__(
        self,
        dashboards: IDashboardRepository,
        questions: IQuestionRepository,
    ) -> None:
        self._dashboards = dashboards
        self._questions = questions

    async def execute(
        self, request: ComposeDashboardRequest
    ) -> Dashboard:
        tiles: list[DashboardTile] = []
        cols = 3

        for i, question_id in enumerate(request._question_ids):
            question = await self._questions.load(question_id)
            if question is None:
                raise TileNotFoundError(
                    f"Question {question_id.value} not found"
                )

            row, col = divmod(i, cols)
            tile = DashboardTile(
                identity=TileIdentity(
                    _id=EntityId(uuid4()),
                    _position=TilePosition(
                        _row=row * 2, _col=col * 4,
                        _width=4, _height=2,
                    ),
                ),
                source=question,
            )
            tiles.append(tile)

        layout = DashboardLayout(
            title=request._title,
            tiles=Tiles(tiles),
        )

        if request._auto_bind_filters:
            for i, ti in enumerate(tiles):
                for j, tj in enumerate(tiles):
                    if (
                        i != j
                        and ti._source.is_compatible_with(tj._source)
                    ):
                        layout.bind_filter(
                            source_tile_id=ti._identity._id,
                            column="*",
                            target_tile_ids={tj._identity._id},
                        )

        dashboard = Dashboard(
            identity=DashboardIdentity(
                id=EntityId(uuid4()),
                audit=AuditRecord(
                    _created=CreatedAt(datetime.utcnow()),
                    _updated=UpdatedAt(datetime.utcnow()),
                ),
            ),
            layout=layout,
        )
        await self._dashboards.save(dashboard)
        return dashboard
