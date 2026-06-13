from __future__ import annotations

from src.shared.domain.base import EntityId
from src.shared.infrastructure.mongo_client import MongoClientSingleton
from src.dashboards.application.ports.i_dashboard_repository import IDashboardRepository
from src.dashboards.domain.entities import Dashboard


class MongoDashboardRepository(IDashboardRepository):
    def __init__(self, mongo: MongoClientSingleton) -> None:
        self._collection = mongo.database["dashboards"]

    async def save(self, dashboard: Dashboard) -> None:
        doc = {
            "_id": str(dashboard._identity._id.value),
            "title": dashboard._layout._title.value,
            "created_at": dashboard._identity._audit._created.value.isoformat(),
            "updated_at": dashboard._identity._audit._updated.value.isoformat(),
        }
        await self._collection.replace_one(
            {"_id": doc["_id"]}, doc, upsert=True
        )

    async def load(self, dashboard_id: EntityId) -> Dashboard | None:
        doc = await self._collection.find_one(
            {"_id": str(dashboard_id.value)}
        )
        if doc is None:
            return None
        return self._doc_to_dashboard(doc)

    async def delete(self, dashboard_id: EntityId) -> None:
        await self._collection.delete_one(
            {"_id": str(dashboard_id.value)}
        )

    async def find_all(self) -> list[Dashboard]:
        cursor = self._collection.find()
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_dashboard(doc) for doc in docs]

    def _doc_to_dashboard(self, doc: dict) -> Dashboard:
        from uuid import UUID
        from datetime import datetime
        from shared.domain.base import AuditRecord, CreatedAt, UpdatedAt
        from dashboards.domain.entities import (
            DashboardIdentity, DashboardLayout, DashboardTitle, Tiles,
        )

        return Dashboard(
            identity=DashboardIdentity(
                id=EntityId(UUID(doc["_id"])),
                audit=AuditRecord(
                    _created=CreatedAt(
                        datetime.fromisoformat(doc["created_at"])
                    ),
                    _updated=UpdatedAt(
                        datetime.fromisoformat(doc["updated_at"])
                    ),
                ),
            ),
            layout=DashboardLayout(
                title=DashboardTitle(doc["title"]),
                tiles=Tiles(),
            ),
        )
