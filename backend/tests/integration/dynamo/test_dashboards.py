from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pytest_bdd import given, parsers, scenarios, then, when

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
from src.dashboards.infrastructure.dynamo_repository import DynamoDashboardRepository
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
from src.questions.infrastructure.dynamo_repository import DynamoQuestionRepository
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, ResponseKind, UpdatedAt

scenarios("features/dashboards.feature")


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_question() -> Question:
    now = datetime.now(UTC)
    return Question(
        identity=QuestionIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
        ),
        specification=QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle("Q"),
                _query=QueryDefinition(
                    _sql=SqlQuery("SELECT 1"),
                    _source=DatasetReference(_id=EntityId(uuid4()), _alias=None),
                ),
            ),
            rendering=RenderDirective(
                _decision=VizDecision(
                    _format=ResponseKind.CHART,
                    _spec=VizSpec(_component="BarChart", _props={}, _children=()),
                ),
            ),
        ),
    )


def _make_tile(question: Question, row: int, col: int, width: int, height: int) -> DashboardTile:
    return DashboardTile(
        identity=TileIdentity(
            _id=EntityId(uuid4()),
            _position=TilePosition(_row=row, _col=col, _width=width, _height=height),
        ),
        source=question,
    )


def _make_dashboard(title: str, tiles: list[DashboardTile]) -> Dashboard:
    now = datetime.now(UTC)
    return Dashboard(
        identity=DashboardIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
        ),
        layout=DashboardLayout(title=DashboardTitle(title), tiles=Tiles(tiles)),
    )


# ── given ─────────────────────────────────────────────────────────────────────


@given(parsers.parse('a dashboard titled "{title}"'))
def dashboard_with_title(ctx: dict, title: str) -> None:
    ctx["dashboard"] = _make_dashboard(title, [])


@given("a saved question")
def a_saved_question(ctx: dict, question_repo: DynamoQuestionRepository) -> None:
    q = _make_question()
    question_repo.save(q)
    ctx["question"] = q


@given(parsers.parse("{count:d} saved questions"))
def n_saved_questions(ctx: dict, count: int, question_repo: DynamoQuestionRepository) -> None:
    questions = [_make_question() for _ in range(count)]
    for q in questions:
        question_repo.save(q)
    ctx["questions"] = questions


@given(
    parsers.parse(
        "a dashboard with a tile for that question at row {row:d} col {col:d} width {width:d} height {height:d}",
    ),
)
def dashboard_with_one_tile(ctx: dict, row: int, col: int, width: int, height: int) -> None:
    tile = _make_tile(ctx["question"], row, col, width, height)
    ctx["tile"] = tile
    ctx["dashboard"] = _make_dashboard("Dash", [tile])


@given("a dashboard with tiles for both questions")
def dashboard_with_two_tiles(ctx: dict) -> None:
    q1, q2 = ctx["questions"][0], ctx["questions"][1]
    t1 = _make_tile(q1, row=0, col=0, width=4, height=2)
    t2 = _make_tile(q2, row=0, col=4, width=4, height=2)
    ctx["tiles"] = [t1, t2]
    ctx["dashboard"] = _make_dashboard("Dash", [t1, t2])


@given(parsers.parse('a filter from tile 1 on column "{column}" targeting tile 2'))
def bind_filter(ctx: dict, column: str) -> None:
    t1, t2 = ctx["tiles"][0], ctx["tiles"][1]
    ctx["dashboard"]._layout.bind_filter(
        source_tile_id=t1._identity._id,
        column=column,
        target_tile_ids={t2._identity._id},
    )
    ctx["filter_column"] = column


@given("an empty dashboard")
def empty_dashboard(ctx: dict) -> None:
    ctx["dashboard"] = _make_dashboard("Empty", [])


# ── when ──────────────────────────────────────────────────────────────────────


@when("the dashboard is saved")
def save_dashboard(ctx: dict, dashboard_repo: DynamoDashboardRepository) -> None:
    dashboard_repo.save(ctx["dashboard"])


@when("the dashboard is reloaded by its ID")
def reload_dashboard(ctx: dict, dashboard_repo: DynamoDashboardRepository) -> None:
    ctx["reloaded"] = dashboard_repo.load(ctx["dashboard"]._identity._id)


@when("a random dashboard ID is loaded")
def load_missing_dashboard(ctx: dict, dashboard_repo: DynamoDashboardRepository) -> None:
    ctx["reloaded"] = dashboard_repo.load(EntityId(uuid4()))


# ── then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('the reloaded dashboard title is "{title}"'))
def check_dashboard_title(ctx: dict, title: str) -> None:
    assert ctx["reloaded"]._layout._title.value == title


@then(parsers.parse("the reloaded dashboard has {count:d} tile"))
def check_tile_count_singular(ctx: dict, count: int) -> None:
    assert len(ctx["reloaded"]._layout._tiles.to_list()) == count


@then(parsers.parse("the reloaded dashboard has {count:d} tiles"))
def check_tile_count_plural(ctx: dict, count: int) -> None:
    assert len(ctx["reloaded"]._layout._tiles.to_list()) == count


@then(
    parsers.parse("the tile position is row {row:d} col {col:d} width {width:d} height {height:d}"),
)
def check_tile_position(ctx: dict, row: int, col: int, width: int, height: int) -> None:
    pos = ctx["reloaded"]._layout._tiles.to_list()[0]._identity._position
    assert (pos._row, pos._col, pos._width, pos._height) == (row, col, width, height)


@then("the tile is linked to the original question ID")
def check_tile_links_question(ctx: dict) -> None:
    tile = ctx["reloaded"]._layout._tiles.to_list()[0]
    assert tile._source._identity._id == ctx["question"]._identity._id


@then(parsers.parse('tile 1 filters tile 2 on column "{column}"'))
def check_filter_binding(ctx: dict, column: str) -> None:
    source_id = ctx["tiles"][0]._identity._id
    target_id = ctx["tiles"][1]._identity._id
    affected = ctx["reloaded"]._layout.tiles_affected_by(source_id, column)
    assert any(t._identity._id == target_id for t in affected)


@then("the dashboard result is None")
def check_dashboard_none(ctx: dict) -> None:
    assert ctx["reloaded"] is None
