from __future__ import annotations


class TestDynamoQuestionRepository:
    def test_module_imports(self) -> None:
        from src.questions.infrastructure.dynamo_repository import DynamoQuestionRepository

        assert DynamoQuestionRepository is not None

    def test_class_is_instantiable(self) -> None:
        from src.questions.infrastructure.dynamo_repository import DynamoQuestionRepository

        repo = DynamoQuestionRepository()
        assert repo is not None
