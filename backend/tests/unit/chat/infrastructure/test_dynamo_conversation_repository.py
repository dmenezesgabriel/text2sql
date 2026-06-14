from __future__ import annotations


class TestDynamoConversationRepository:
    def test_module_imports(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        assert DynamoConversationRepository is not None

    def test_class_is_instantiable(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        assert repo is not None
