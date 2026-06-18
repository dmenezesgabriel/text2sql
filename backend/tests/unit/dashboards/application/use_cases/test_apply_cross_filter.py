from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.dashboards.application.use_cases.apply_cross_filter import (
    ApplyCrossFilterUseCase,
    CrossFilterRequest,
)
from src.dashboards.domain.entities import (
    Dashboard,
    DashboardIdentity,
    DashboardLayout,
    DashboardTile,
    TileIdentity,
    Tiles,
)
from src.dashboards.domain.value_objects import DashboardTitle, TilePosition
from src.dashboards.exceptions.dashboard_not_found_error import DashboardNotFoundError
from src.questions.domain.entities import (
    DatasetReference,
    QueryDefinition,
    Question,
    QuestionDescription,
    QuestionIdentity,
    QuestionSpecification,
    RenderDirective,
)
from src.questions.domain.value_objects import QuestionTitle, SqlQuery, VizDecision, VizSpec
from src.shared.domain.base import (
    AuditRecord,
    CreatedAt,
    EntityId,
    QueryResult,
    ResponseKind,
    UpdatedAt,
)


def _make_question(sql: str = "SELECT 1") -> Question:
    dataset_id = EntityId(uuid4())
    return Question(
        identity=QuestionIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(
                _created=CreatedAt(datetime.now(UTC)),
                _updated=UpdatedAt(datetime.now(UTC)),
            ),
        ),
        specification=QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle("Q"),
                _query=QueryDefinition(
                    _sql=SqlQuery(sql),
                    _source=DatasetReference(_id=dataset_id, _alias=None),
                ),
            ),
            rendering=RenderDirective(
                _decision=VizDecision(
                    _format=ResponseKind.TABLE,
                    _spec=VizSpec(_component="Table", _props={}, _children=()),
                ),
            ),
        ),
    )


def _make_dashboard(dashboard_id: EntityId) -> Dashboard:
    return Dashboard(
        identity=DashboardIdentity(
            entity_id=dashboard_id,
            audit=AuditRecord(
                _created=CreatedAt(datetime.now(UTC)),
                _updated=UpdatedAt(datetime.now(UTC)),
            ),
        ),
        layout=DashboardLayout(
            title=DashboardTitle("Test Dashboard"),
            tiles=Tiles(),
        ),
    )


def _make_dashboard_with_filter(
    source_tile_id: EntityId,
    target_tile_id: EntityId,
    column: str,
    question: Question,
) -> Dashboard:
    """Dashboard with one source tile that filters one target tile."""
    dashboard_id = EntityId(uuid4())
    src_tile = DashboardTile(
        identity=TileIdentity(
            _id=source_tile_id,
            _position=TilePosition(_row=0, _col=0, _width=4, _height=2),
        ),
        source=_make_question(),
    )
    target_tile = DashboardTile(
        identity=TileIdentity(
            _id=target_tile_id,
            _position=TilePosition(_row=0, _col=4, _width=4, _height=2),
        ),
        source=question,
    )
    now = datetime.now(UTC)
    layout = DashboardLayout(title=DashboardTitle("D"), tiles=Tiles([src_tile, target_tile]))
    layout.bind_filter(source_tile_id, column, {target_tile_id})
    return Dashboard(
        identity=DashboardIdentity(
            entity_id=dashboard_id,
            audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
        ),
        layout=layout,
    )


class FakeDashboardRepository:
    def __init__(self, dashboard: Dashboard | None = None) -> None:
        self._dashboard = dashboard

    def load(self, dashboard_id: EntityId) -> Dashboard | None:
        if self._dashboard and self._dashboard._identity._id == dashboard_id:
            return self._dashboard
        return None

    def save(self, dashboard: Dashboard) -> None:
        self._dashboard = dashboard

    def delete(self, dashboard_id: EntityId) -> None:
        pass

    def find_all(self) -> list[Dashboard]:
        return [self._dashboard] if self._dashboard else []


class CapturingQueryExecutor:
    def __init__(self) -> None:
        self.received_sql: str | None = None
        self.received_dataset_id: EntityId | None = None

    async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
        self.received_sql = sql
        self.received_dataset_id = dataset_id
        return QueryResult(_columns=("col",), _rows=({"col": "val"},))


class FakeQueryExecutor:
    async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
        return QueryResult(_columns=("col",), _rows=({"col": "val"},))


class TestApplyCrossFilterUseCase:
    async def test_raises_when_dashboard_not_found(self) -> None:
        repo = FakeDashboardRepository(dashboard=None)
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=FakeQueryExecutor())
        request = CrossFilterRequest(
            _dashboard_id=EntityId(uuid4()),
            _source_tile_id=EntityId(uuid4()),
            _column="status",
            _value="active",
        )
        with pytest.raises(DashboardNotFoundError):
            await use_case.execute(request)

    async def test_not_found_error_message_contains_dashboard_id(self) -> None:
        missing_id = EntityId(uuid4())
        repo = FakeDashboardRepository(dashboard=None)
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=FakeQueryExecutor())
        request = CrossFilterRequest(
            _dashboard_id=missing_id,
            _source_tile_id=EntityId(uuid4()),
            _column="status",
            _value="active",
        )
        with pytest.raises(DashboardNotFoundError) as exc_info:
            await use_case.execute(request)
        assert str(missing_id.value) in str(exc_info.value)

    async def test_returns_empty_results_when_no_bound_tiles(self) -> None:
        dashboard_id = EntityId(uuid4())
        source_tile_id = EntityId(uuid4())
        dashboard = _make_dashboard(dashboard_id)
        repo = FakeDashboardRepository(dashboard=dashboard)
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=FakeQueryExecutor())

        request = CrossFilterRequest(
            _dashboard_id=dashboard_id,
            _source_tile_id=source_tile_id,
            _column="status",
            _value="active",
        )
        result = await use_case.execute(request)
        assert result._tile_results == {}
        assert result._filter_column == "status"
        assert result._filter_value == "active"

    async def test_result_source_tile_matches_request(self) -> None:
        source_tile_id = EntityId(uuid4())
        target_tile_id = EntityId(uuid4())
        question = _make_question("SELECT region, revenue FROM sales")
        dashboard = _make_dashboard_with_filter(source_tile_id, target_tile_id, "region", question)
        repo = FakeDashboardRepository(dashboard=dashboard)
        executor = CapturingQueryExecutor()
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=executor)

        request = CrossFilterRequest(
            _dashboard_id=dashboard._identity._id,
            _source_tile_id=source_tile_id,
            _column="region",
            _value="West",
        )
        result = await use_case.execute(request)
        assert result._source_tile == source_tile_id

    async def test_filter_sql_uses_equality_operator(self) -> None:
        source_tile_id = EntityId(uuid4())
        target_tile_id = EntityId(uuid4())
        question = _make_question("SELECT region, revenue FROM sales")
        dashboard = _make_dashboard_with_filter(source_tile_id, target_tile_id, "region", question)
        repo = FakeDashboardRepository(dashboard=dashboard)
        executor = CapturingQueryExecutor()
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=executor)

        request = CrossFilterRequest(
            _dashboard_id=dashboard._identity._id,
            _source_tile_id=source_tile_id,
            _column="region",
            _value="West",
        )
        await use_case.execute(request)
        assert executor.received_sql is not None
        assert "= 'West'" in executor.received_sql

    async def test_filter_sql_includes_original_query(self) -> None:
        source_tile_id = EntityId(uuid4())
        target_tile_id = EntityId(uuid4())
        question = _make_question("SELECT region, revenue FROM sales")
        dashboard = _make_dashboard_with_filter(source_tile_id, target_tile_id, "region", question)
        repo = FakeDashboardRepository(dashboard=dashboard)
        executor = CapturingQueryExecutor()
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=executor)

        request = CrossFilterRequest(
            _dashboard_id=dashboard._identity._id,
            _source_tile_id=source_tile_id,
            _column="region",
            _value="West",
        )
        await use_case.execute(request)
        assert "SELECT region, revenue FROM sales" in executor.received_sql

    async def test_filter_uses_question_dataset_id(self) -> None:
        source_tile_id = EntityId(uuid4())
        target_tile_id = EntityId(uuid4())
        question = _make_question("SELECT x FROM t")
        expected_dataset_id = question._specification._description._query._source._id
        dashboard = _make_dashboard_with_filter(source_tile_id, target_tile_id, "x", question)
        repo = FakeDashboardRepository(dashboard=dashboard)
        executor = CapturingQueryExecutor()
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=executor)

        request = CrossFilterRequest(
            _dashboard_id=dashboard._identity._id,
            _source_tile_id=source_tile_id,
            _column="x",
            _value="1",
        )
        await use_case.execute(request)
        assert executor.received_dataset_id == expected_dataset_id

    async def test_filter_sql_uses_request_column_in_where(self) -> None:
        # Kills mutmut_14: column=None instead of column=request._column
        source_tile_id = EntityId(uuid4())
        target_tile_id = EntityId(uuid4())
        question = _make_question("SELECT city, revenue FROM sales")
        dashboard = _make_dashboard_with_filter(source_tile_id, target_tile_id, "city", question)
        repo = FakeDashboardRepository(dashboard=dashboard)
        executor = CapturingQueryExecutor()
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=executor)
        request = CrossFilterRequest(
            _dashboard_id=dashboard._identity._id,
            _source_tile_id=source_tile_id,
            _column="city",
            _value="Paris",
        )
        await use_case.execute(request)
        assert executor.received_sql is not None
        assert "city = 'Paris'" in executor.received_sql

    async def test_result_contains_target_tile_id(self) -> None:
        source_tile_id = EntityId(uuid4())
        target_tile_id = EntityId(uuid4())
        question = _make_question("SELECT x FROM t")
        dashboard = _make_dashboard_with_filter(source_tile_id, target_tile_id, "x", question)
        repo = FakeDashboardRepository(dashboard=dashboard)
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=FakeQueryExecutor())

        request = CrossFilterRequest(
            _dashboard_id=dashboard._identity._id,
            _source_tile_id=source_tile_id,
            _column="x",
            _value="1",
        )
        result = await use_case.execute(request)
        assert target_tile_id in result._tile_results
