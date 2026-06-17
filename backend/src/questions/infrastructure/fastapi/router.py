from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.questions.application.ports.i_question_repository import IQuestionRepository
from src.questions.application.use_cases.drill_down_question import (
    DrillDownQuestionUseCase,
    DrillDownRequest,
)
from src.questions.application.use_cases.save_question_from_chat import (
    SaveQuestionFromChatRequest,
    SaveQuestionFromChatUseCase,
)
from src.questions.domain.entities import (
    DatasetReference,
    QueryDefinition,
    Question,
    QuestionDescription,
    QuestionSpecification,
    RenderDirective,
)
from src.questions.domain.value_objects import QuestionTitle, SqlQuery, VizDecision, VizSpec
from src.questions.exceptions.dataset_not_found_error import DatasetNotFoundError
from src.questions.exceptions.duplicate_question_error import DuplicateQuestionError
from src.questions.exceptions.invalid_query_error import InvalidQueryError
from src.questions.exceptions.question_not_found_error import QuestionNotFoundError
from src.shared.domain.base import EntityId, ResponseKind


def _question_to_dict(q: Question) -> dict[str, object]:
    spec = q._specification
    decision = spec._rendering._decision
    return {
        "id": str(q._identity._id.value),
        "title": spec._description._title.value,
        "sql": spec._description._query._sql.value,
        "datasetId": str(spec._description._query._source._id.value),
        "vizComponent": decision._spec._component,
        "vizFormat": decision._format.name,
        "vizProps": decision._spec._props,
        "vizChildren": list(decision._spec._children),
        "createdAt": q._identity._audit._created.value.isoformat(),
        "updatedAt": q._identity._audit._updated.value.isoformat(),
    }


def _parse_viz_format(raw: object) -> ResponseKind:
    name = str(raw).upper() if raw else "CHART"
    return ResponseKind[name] if name in ResponseKind.__members__ else ResponseKind.CHART


def _build_save_request(body: dict[str, object]) -> SaveQuestionFromChatRequest:
    dataset_uuid = UUID(str(body.get("dataset_id", "")))
    dataset_ref = DatasetReference(_id=EntityId(dataset_uuid), _alias=None)
    sql = SqlQuery(str(body.get("sql", "")))
    query = QueryDefinition(_sql=sql, _source=dataset_ref)
    title = QuestionTitle(str(body.get("title") or "Untitled question"))
    description = QuestionDescription(_title=title, _query=query)
    viz_format = _parse_viz_format(body.get("viz_format"))
    props = body.get("viz_props") or {}
    children_raw = body.get("viz_children") or []
    viz_spec = VizSpec(
        _component=str(body.get("viz_component", "")),
        _props=props if isinstance(props, dict) else {},
        _children=tuple(children_raw if isinstance(children_raw, list) else []),
    )
    decision = VizDecision(_format=viz_format, _spec=viz_spec)
    spec = QuestionSpecification(
        description=description,
        rendering=RenderDirective(_decision=decision),
    )
    return SaveQuestionFromChatRequest(
        _sql=sql,
        _title=title,
        _dataset_id=EntityId(dataset_uuid),
        _decision=decision,
        _spec=spec,
    )


def _create_question_response(
    body: dict[str, object],
    save_use_case: SaveQuestionFromChatUseCase,
) -> JSONResponse | dict[str, object]:
    try:
        request = _build_save_request(body)
        question = save_use_case.execute(request)
    except (ValueError, KeyError) as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except (DatasetNotFoundError, DuplicateQuestionError) as exc:
        status = 409 if isinstance(exc, DuplicateQuestionError) else 404
        return JSONResponse(status_code=status, content={"error": str(exc)})
    return _question_to_dict(question)


def _get_question_response(
    question_id: str,
    repo: IQuestionRepository,
) -> JSONResponse | dict[str, object]:
    try:
        question = repo.load(EntityId(UUID(question_id)))
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid question ID"})
    if question is None:
        return JSONResponse(status_code=404, content={"error": "Question not found"})
    return _question_to_dict(question)


def _execute_drill(
    drill_use_case: DrillDownQuestionUseCase,
    question_id: str,
    body: dict[str, object],
) -> Question:
    source_id = EntityId(UUID(question_id))
    column = str(body.get("column", "")).strip()
    value = str(body.get("value", "")).strip()
    if not column or not value:
        msg = "'column' and 'value' are required"
        raise ValueError(msg)
    return drill_use_case.execute(
        DrillDownRequest(_source_id=source_id, _column=column, _value=value),
    )


def create_questions_router(
    question_repo: IQuestionRepository,
    save_use_case: SaveQuestionFromChatUseCase,
    drill_use_case: DrillDownQuestionUseCase,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/questions", tags=["questions"])

    @router.get("")
    async def list_questions():
        questions = question_repo.find_all().to_list()
        return {"questions": [_question_to_dict(q) for q in questions]}

    @router.post("")
    async def create_question(body: dict[str, object]):
        return _create_question_response(body, save_use_case)

    @router.get("/{question_id}")
    async def get_question(question_id: str):
        return _get_question_response(question_id, question_repo)

    @router.delete("/{question_id}")
    async def delete_question(question_id: str):
        try:
            question_repo.delete(EntityId(UUID(question_id)))
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "Invalid question ID"})
        return {"status": "deleted"}

    @router.post("/{question_id}/drill")
    async def drill_question(question_id: str, body: dict[str, object]):
        try:
            derived = _execute_drill(drill_use_case, question_id, body)
        except (ValueError, QuestionNotFoundError, InvalidQueryError) as exc:
            status = (
                404
                if isinstance(exc, QuestionNotFoundError)
                else (422 if isinstance(exc, InvalidQueryError) else 400)
            )
            return JSONResponse(status_code=status, content={"error": str(exc)})
        return _question_to_dict(derived)

    return router
