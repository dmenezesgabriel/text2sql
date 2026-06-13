from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

from src.dashboards.application.ports.i_dashboard_repository import IDashboardRepository
from src.dashboards.domain.entities import (
    Dashboard,
    DashboardIdentity,
    DashboardLayout,
    DashboardTile,
    DashboardTitle,
    TileIdentity,
    TilePosition,
    Tiles,
)
from src.dashboards.domain.value_objects import FilterBinding
from src.dashboards.exceptions.tile_not_found_error import TileNotFoundError
from src.questions.application.ports.i_question_repository import IQuestionRepository
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, UpdatedAt
from src.shared.infrastructure.dynamo_models import DashboardModel


class DynamoDashboardRepository(IDashboardRepository):
    def __init__(self, questions: IQuestionRepository) -> None:
        self._questions = questions

    def save(self, dashboard: Dashboard) -> None:
        model = DashboardModel(
            id=str(dashboard._identity._id.value),
            title=dashboard._layout._title.value,
            tiles=json.dumps(self._serialize_tiles(dashboard._layout._tiles)),
            filters=json.dumps(self._serialize_filters(dashboard._layout._filters)),
            created_at=dashboard._identity._audit._created.value.isoformat(),
            updated_at=dashboard._identity._audit._updated.value.isoformat(),
        )
        model.save()

    def load(self, dashboard_id: EntityId) -> Dashboard | None:
        try:
            model = DashboardModel.get(str(dashboard_id.value))
        except DashboardModel.DoesNotExist:
            return None
        return self._doc_to_dashboard(model)

    def delete(self, dashboard_id: EntityId) -> None:
        try:
            DashboardModel.get(str(dashboard_id.value)).delete()
        except DashboardModel.DoesNotExist:
            return

    def find_all(self) -> list[Dashboard]:
        models = list(DashboardModel.scan())
        return [self._doc_to_dashboard(m) for m in models]

    def _doc_to_dashboard(self, model: DashboardModel) -> Dashboard:
        tiles = self._deserialize_tiles(model.tiles or "[]")
        layout = DashboardLayout(title=DashboardTitle(model.title), tiles=tiles)
        self._apply_filters(model.filters or "[]", layout)
        return Dashboard(
            identity=DashboardIdentity(
                entity_id=EntityId(UUID(model.id)),
                audit=AuditRecord(
                    _created=CreatedAt(datetime.fromisoformat(model.created_at)),
                    _updated=UpdatedAt(datetime.fromisoformat(model.updated_at)),
                ),
            ),
            layout=layout,
        )

    def _deserialize_tiles(self, tiles_json: str) -> Tiles:
        tile_list = []
        for td in json.loads(tiles_json):
            question = self._questions.load(EntityId(UUID(td["question_id"])))
            if question is None:
                msg = f"Question {td['question_id']!r} not found while loading dashboard tile"
                raise TileNotFoundError(msg)
            tile_list.append(
                DashboardTile(
                    identity=TileIdentity(
                        _id=EntityId(UUID(td["tile_id"])),
                        _position=TilePosition(
                            _row=td["row"],
                            _col=td["col"],
                            _width=td["width"],
                            _height=td["height"],
                        ),
                    ),
                    source=question,
                ),
            )
        return Tiles(tile_list)

    def _apply_filters(self, filters_json: str, layout: DashboardLayout) -> None:
        for fd in json.loads(filters_json):
            layout.bind_filter(
                source_tile_id=EntityId(UUID(fd["source_tile_id"])),
                column=fd["column"],
                target_tile_ids={EntityId(UUID(tid)) for tid in fd["target_tile_ids"]},
            )

    def _serialize_tiles(self, tiles: Tiles) -> list[dict[str, object]]:
        return [
            {
                "tile_id": str(t._identity._id.value),
                "question_id": str(t._source._identity._id.value),
                "row": t._identity._position._row,
                "col": t._identity._position._col,
                "width": t._identity._position._width,
                "height": t._identity._position._height,
            }
            for t in tiles.to_list()
        ]

    def _serialize_filters(
        self,
        filters: dict[EntityId, tuple[FilterBinding, ...]],
    ) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for source_id, bindings in filters.items():
            for b in bindings:
                result.append(
                    {
                        "source_tile_id": str(source_id.value),
                        "column": b._column,
                        "target_tile_ids": [str(tid.value) for tid in b._target_tiles],
                    },
                )
        return result
