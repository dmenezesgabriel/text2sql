from __future__ import annotations


class TestDynamoModels:
    def test_conversation_model_imports(self) -> None:
        from src.shared.infrastructure.dynamo_models import ConversationModel

        assert ConversationModel is not None

    def test_question_model_imports(self) -> None:
        from src.shared.infrastructure.dynamo_models import QuestionModel

        assert QuestionModel is not None

    def test_dataset_model_imports(self) -> None:
        from src.shared.infrastructure.dynamo_models import DatasetModel

        assert DatasetModel is not None

    def test_dashboard_model_imports(self) -> None:
        from src.shared.infrastructure.dynamo_models import DashboardModel

        assert DashboardModel is not None

    def test_conversation_model_table_name(self) -> None:
        from src.shared.infrastructure.dynamo_models import ConversationModel

        assert ConversationModel.Meta.table_name == "conversations"

    def test_question_model_table_name(self) -> None:
        from src.shared.infrastructure.dynamo_models import QuestionModel

        assert QuestionModel.Meta.table_name == "questions"

    def test_dataset_model_table_name(self) -> None:
        from src.shared.infrastructure.dynamo_models import DatasetModel

        assert DatasetModel.Meta.table_name == "datasets"

    def test_dashboard_model_table_name(self) -> None:
        from src.shared.infrastructure.dynamo_models import DashboardModel

        assert DashboardModel.Meta.table_name == "dashboards"
