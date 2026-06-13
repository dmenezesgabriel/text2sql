from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from pytest_bdd import given, parsers, scenarios, then, when

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

scenarios("features/questions.feature")


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_question(
    *,
    viz_format: ResponseKind = ResponseKind.CHART,
    viz_props: dict[str, object] | None = None,
    viz_children: tuple[object, ...] = (),
) -> Question:
    now = datetime.now(UTC)
    return Question(
        identity=QuestionIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
        ),
        specification=QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle("Test"),
                _query=QueryDefinition(
                    _sql=SqlQuery("SELECT 1"),
                    _source=DatasetReference(_id=EntityId(uuid4()), _alias=None),
                ),
            ),
            rendering=RenderDirective(
                _decision=VizDecision(
                    _format=viz_format,
                    _spec=VizSpec(
                        _component="BarChart",
                        _props=viz_props or {},
                        _children=viz_children,
                    ),
                ),
            ),
        ),
    )


# ── given ─────────────────────────────────────────────────────────────────────


@given("a question with TABLE viz format")
def question_with_table_format(ctx: dict) -> None:
    ctx["question"] = _make_question(viz_format=ResponseKind.TABLE)


@given(parsers.parse("a question with viz props {props_json}"))
def question_with_viz_props(ctx: dict, props_json: str) -> None:
    ctx["question"] = _make_question(viz_props=json.loads(props_json))


@given(parsers.parse("a question with viz children {children_json}"))
def question_with_viz_children(ctx: dict, children_json: str) -> None:
    ctx["question"] = _make_question(viz_children=tuple(json.loads(children_json)))


@given("a saved question")
def a_saved_question(ctx: dict, question_repo: DynamoQuestionRepository) -> None:
    question = _make_question()
    question_repo.save(question)
    ctx["question"] = question


@given(parsers.parse("{count:d} saved questions"))
def n_saved_questions(ctx: dict, count: int, question_repo: DynamoQuestionRepository) -> None:
    questions = [_make_question() for _ in range(count)]
    for q in questions:
        question_repo.save(q)
    ctx["questions"] = questions


# ── when ──────────────────────────────────────────────────────────────────────


@when("the question is saved")
def save_question(ctx: dict, question_repo: DynamoQuestionRepository) -> None:
    question_repo.save(ctx["question"])


@when("the question is reloaded by its ID")
def reload_question(ctx: dict, question_repo: DynamoQuestionRepository) -> None:
    ctx["reloaded"] = question_repo.load(ctx["question"]._identity._id)


@when("a random question ID is loaded")
def load_missing_question(ctx: dict, question_repo: DynamoQuestionRepository) -> None:
    ctx["reloaded"] = question_repo.load(EntityId(uuid4()))


@when("the question is deleted")
def delete_question(ctx: dict, question_repo: DynamoQuestionRepository) -> None:
    question_repo.delete(ctx["question"]._identity._id)


@when("all questions are listed")
def list_all_questions(ctx: dict, question_repo: DynamoQuestionRepository) -> None:
    ctx["all_results"] = question_repo.find_all()


# ── then ──────────────────────────────────────────────────────────────────────


@then("the reloaded viz format is TABLE")
def check_table_format(ctx: dict) -> None:
    assert ctx["reloaded"]._specification._rendering._decision._format is ResponseKind.TABLE


@then(parsers.parse("the reloaded viz props are {props_json}"))
def check_viz_props(ctx: dict, props_json: str) -> None:
    expected = json.loads(props_json)
    assert ctx["reloaded"]._specification._rendering._decision._spec._props == expected


@then(parsers.parse("the reloaded viz children are {children_json}"))
def check_viz_children(ctx: dict, children_json: str) -> None:
    expected = tuple(json.loads(children_json))
    assert ctx["reloaded"]._specification._rendering._decision._spec._children == expected


@then("the question result is None")
def check_question_none(ctx: dict) -> None:
    assert ctx["reloaded"] is None


@then(parsers.parse("{count:d} questions are returned"))
def check_question_count(ctx: dict, count: int) -> None:
    assert ctx["all_results"].count() == count
