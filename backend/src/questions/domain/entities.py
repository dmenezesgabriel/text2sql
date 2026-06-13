from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from src.questions.domain.value_objects import (
    QuestionTitle,
    SqlQuery,
    VizDecision,
)
from src.questions.exceptions.invalid_query_error import InvalidQueryError
from src.questions.exceptions.same_visualization_error import SameVisualizationError
from src.shared.domain.base import (
    AuditRecord,
    CreatedAt,
    Entity,
    EntityId,
    UpdatedAt,
    ValueObject,
)

_SAFE_IDENTIFIER = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _validated_identifier(value: str) -> str:
    """Reject values that cannot safely appear as SQL identifiers."""
    if not _SAFE_IDENTIFIER.match(value):
        msg = f"Unsafe SQL identifier: {value!r}"
        raise ValueError(msg)
    return value


@dataclass(frozen=True)
class DatasetReference(ValueObject):
    _id: EntityId
    _alias: str | None

    def qualified_name(self) -> str:
        return self._alias or str(self._id.value)


@dataclass(frozen=True)
class QueryDefinition(ValueObject):
    _sql: SqlQuery
    _source: DatasetReference

    def __post_init__(self) -> None:
        if not self._sql.is_select():
            msg = f"Only SELECT queries supported, got: {self._sql.value[:50]}"
            raise InvalidQueryError(msg)

    def with_filter(
        self,
        column: str,
        operator: str,
        value: str,
    ) -> QueryDefinition:
        filtered_sql = SqlQuery(
            f"{self._sql.value.rstrip(';')} WHERE {column} {operator} '{value}'",
        )
        return QueryDefinition(sql=filtered_sql, source=self._source)

    def with_grouping(
        self,
        group_column: str,
        agg_column: str,
        agg_func: str,
    ) -> QueryDefinition:
        safe_group = _validated_identifier(group_column)
        safe_col = _validated_identifier(agg_column)
        safe_func = _validated_identifier(agg_func)
        base = self._sql.value.rstrip(";")
        sql = " ".join(
            [
                "SELECT",
                f"{safe_group}, {safe_func}({safe_col})",
                "FROM",
                f"({base}) AS _drill",
                "GROUP BY",
                safe_group,
            ],
        )
        return QueryDefinition(sql=SqlQuery(sql), source=self._source)

    def with_limit(self, limit: int) -> QueryDefinition:
        limited_sql = SqlQuery(
            f"{self._sql.value.rstrip(';')} LIMIT {limit}",
        )
        return QueryDefinition(sql=limited_sql, source=self._source)

    def is_equivalent_to(self, other: QueryDefinition) -> bool:
        return self._normalize() == other._normalize()

    def _normalize(self) -> str:
        return re.sub(r"\s+", " ", self._sql.value).strip().lower()


@dataclass(frozen=True)
class QuestionDescription(ValueObject):
    _title: QuestionTitle
    _query: QueryDefinition


@dataclass(frozen=True)
class RenderDirective(ValueObject):
    _decision: VizDecision


class QuestionSpecification:
    def __init__(
        self,
        description: QuestionDescription,
        rendering: RenderDirective,
    ) -> None:
        self._description = description
        self._rendering = rendering


class QuestionIdentity:
    def __init__(self, entity_id: EntityId, audit: AuditRecord) -> None:
        self._id = entity_id
        self._audit = audit


class Question(Entity):
    def __init__(
        self,
        identity: QuestionIdentity,
        specification: QuestionSpecification,
    ) -> None:
        self._identity = identity
        self._specification = specification

    def rename(self, new_title: QuestionTitle) -> None:
        self._specification = QuestionSpecification(
            description=QuestionDescription(
                _title=new_title,
                _query=self._specification._description._query,
            ),
            rendering=self._specification._rendering,
        )

    def change_decision(self, new_decision: VizDecision) -> None:
        if new_decision._format is self._specification._rendering._decision._format:
            msg = "New viz must differ from current"
            raise SameVisualizationError(msg)
        self._specification = QuestionSpecification(
            description=self._specification._description,
            rendering=RenderDirective(_decision=new_decision),
        )

    def derive_drill_down(
        self,
        column: str,
        value: str,
    ) -> Question:
        new_query = self._specification._description._query.with_filter(
            column=column,
            operator="=",
            value=value,
        )
        drill_spec = QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle(
                    f"{self._specification._description._title.value} \u2014 {column}={value}",
                ),
                _query=new_query,
            ),
            rendering=self._specification._rendering,
        )
        return Question(
            identity=QuestionIdentity(
                entity_id=EntityId(uuid4()),
                audit=AuditRecord(
                    _created=CreatedAt(datetime.utcnow()),
                    _updated=UpdatedAt(datetime.utcnow()),
                ),
            ),
            specification=drill_spec,
        )

    def duplicate(self, new_title: QuestionTitle) -> Question:
        return Question(
            identity=QuestionIdentity(
                entity_id=EntityId(uuid4()),
                audit=AuditRecord(
                    _created=CreatedAt(datetime.utcnow()),
                    _updated=UpdatedAt(datetime.utcnow()),
                ),
            ),
            specification=QuestionSpecification(
                description=QuestionDescription(
                    _title=new_title,
                    _query=self._specification._description._query,
                ),
                rendering=self._specification._rendering,
            ),
        )

    def is_compatible_with(self, other: Question) -> bool:
        return (
            self._specification._description._query._source._id
            == other._specification._description._query._source._id
        )

    def compiled_sql(self) -> str:
        return self._specification._description._query._sql.value


class Questions:
    def __init__(self, items: list[Question] | None = None) -> None:
        self._items: list[Question] = items or []

    def add(self, question: Question) -> None:
        self._items.append(question)

    def remove(self, question_id: EntityId) -> None:
        self._items = [q for q in self._items if q._identity._id != question_id]

    def to_list(self) -> list[Question]:
        return list(self._items)

    def count(self) -> int:
        return len(self._items)
