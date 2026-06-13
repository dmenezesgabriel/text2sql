from __future__ import annotations

import pytest
from moto import mock_aws

from src.dashboards.infrastructure.dynamo_repository import DynamoDashboardRepository
from src.datasets.infrastructure.dynamo_repository import DynamoDatasetRepository
from src.questions.infrastructure.dynamo_repository import DynamoQuestionRepository
from src.shared.infrastructure.dynamo_models import (
    BaseModel,
    DashboardModel,
    DatasetModel,
    QuestionModel,
)


@pytest.fixture(autouse=True)
def aws_tables():
    """Spin up an in-memory DynamoDB via moto for every test."""
    with mock_aws():
        original_host = BaseModel.Meta.host
        BaseModel.Meta.host = None

        for cls in (DatasetModel, QuestionModel, DashboardModel):
            if hasattr(cls, "_connection"):
                cls._connection = None  # type: ignore[attr-defined]

        DatasetModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        QuestionModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        DashboardModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)

        yield

        BaseModel.Meta.host = original_host
        for cls in (DatasetModel, QuestionModel, DashboardModel):
            if hasattr(cls, "_connection"):
                cls._connection = None  # type: ignore[attr-defined]


@pytest.fixture
def dataset_repo() -> DynamoDatasetRepository:
    return DynamoDatasetRepository()


@pytest.fixture
def question_repo() -> DynamoQuestionRepository:
    return DynamoQuestionRepository()


@pytest.fixture
def dashboard_repo(question_repo: DynamoQuestionRepository) -> DynamoDashboardRepository:
    return DynamoDashboardRepository(questions=question_repo)


@pytest.fixture
def ctx() -> dict:
    """Mutable context bag shared between Gherkin steps within one scenario."""
    return {}
