from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.dashboards.application.ports.i_dashboard_repository import IDashboardRepository
from src.dashboards.domain.entities import (
    Dashboard,
    DashboardIdentity,
    DashboardLayout,
    DashboardTitle,
    Tiles,
)
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, UpdatedAt
from src.shared.infrastructure.dynamo_models import DashboardModel


class DynamoDashboardRepository(IDashboardRepository):
    def save(self, dashboard: Dashboard) -> None:
        model = DashboardModel(
            id=str(dashboard._identity._id.value),
            title=dashboard._layout._title.value,
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
        return Dashboard(
            identity=DashboardIdentity(
                id=EntityId(UUID(model.id)),
                audit=AuditRecord(
                    _created=CreatedAt(
                        datetime.fromisoformat(model.created_at),
                    ),
                    _updated=UpdatedAt(
                        datetime.fromisoformat(model.updated_at),
                    ),
                ),
            ),
            layout=DashboardLayout(
                title=DashboardTitle(model.title),
                tiles=Tiles(),
            ),
        )
