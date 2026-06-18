from __future__ import annotations

from uuid import uuid4

import pytest
from moto import mock_aws

from src.chat.application.ports.i_conversation_repository import ConversationSummary
from src.chat.domain.entities import Conversation
from src.chat.domain.value_objects import ConversationId
from src.shared.domain.base import EntityId
from src.shared.infrastructure.dynamo_models import BaseModel, ConversationModel


@pytest.fixture(autouse=True)
def dynamo_table():
    with mock_aws():
        original_host = BaseModel.Meta.host
        BaseModel.Meta.host = None
        if hasattr(ConversationModel, "_connection"):
            ConversationModel._connection = None  # type: ignore[attr-defined]
        ConversationModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        yield
        BaseModel.Meta.host = original_host
        if hasattr(ConversationModel, "_connection"):
            ConversationModel._connection = None  # type: ignore[attr-defined]


def _make_conv(title: str | None = None) -> Conversation:
    conv = Conversation(identity=EntityId(uuid4()))
    if title:
        conv.set_title(title)
    return conv


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

    def test_save_and_load_round_trip(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv = _make_conv("Test question")
        repo.save(conv)
        loaded = repo.load(ConversationId(conv._identity.value))
        assert loaded is not None
        assert str(loaded._identity.value) == str(conv._identity.value)

    def test_load_returns_none_for_missing(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        result = repo.load(ConversationId(uuid4()))
        assert result is None

    def test_title_persisted_in_save(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv = _make_conv("What is revenue?")
        repo.save(conv)
        loaded = repo.load(ConversationId(conv._identity.value))
        assert loaded is not None
        assert loaded._title == "What is revenue?"

    def test_find_all_returns_empty_when_no_conversations(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        result = repo.find_all()
        assert result == []

    def test_find_all_returns_saved_conversations(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv1 = _make_conv("First question")
        conv2 = _make_conv("Second question")
        repo.save(conv1)
        repo.save(conv2)
        result = repo.find_all()
        assert len(result) == 2
        assert all(isinstance(s, ConversationSummary) for s in result)

    def test_find_all_uses_fallback_title_when_none(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv = _make_conv()  # no title
        repo.save(conv)
        result = repo.find_all()
        assert result[0].title == "Untitled chat"

    def test_find_all_sorted_by_updated_at_desc(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv1 = _make_conv("First")
        conv2 = _make_conv("Second")
        conv3 = _make_conv("Third")
        repo.save(conv1)
        repo.save(conv2)
        repo.save(conv3)
        result = repo.find_all()
        # sorted desc by updated_at — timestamps increase, so last saved comes first
        assert result[0].title == "Third"

    def test_delete_removes_conversation(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv = _make_conv("To delete")
        repo.save(conv)
        repo.delete(ConversationId(conv._identity.value))
        assert repo.load(ConversationId(conv._identity.value)) is None

    def test_closed_conversation_loads_as_closed(self) -> None:
        from src.chat.domain.entities import Conversation
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv = Conversation(identity=EntityId(uuid4()))
        conv.close()
        repo.save(conv)
        loaded = repo.load(ConversationId(conv._identity.value))
        assert loaded is not None
        assert loaded.is_closed()

    def test_active_conversation_loads_as_active(self) -> None:
        from src.chat.domain.entities import Conversation
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv = Conversation(identity=EntityId(uuid4()))
        # do NOT close it — state is ACTIVE
        repo.save(conv)
        loaded = repo.load(ConversationId(conv._identity.value))
        assert loaded is not None
        assert not loaded.is_closed()

    def test_find_all_caps_at_50_results(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        for i in range(51):
            conv = _make_conv(f"conversation {i}")
            repo.save(conv)
        result = repo.find_all()
        assert len(result) == 50

    def test_save_stores_timezone_aware_updated_at(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv = _make_conv("check tz")
        repo.save(conv)
        result = repo.find_all()
        assert len(result) == 1
        # UTC produces "+00:00" in isoformat; naive datetime would not have "+"
        assert "+" in result[0].updated_at

    def test_save_id_matches_conversation_identity(self) -> None:
        from src.chat.infrastructure.dynamo_conversation_repository import (
            DynamoConversationRepository,
        )

        repo = DynamoConversationRepository()
        conv = _make_conv("id check")
        repo.save(conv)
        result = repo.find_all()
        assert len(result) == 1
        assert result[0].id == str(conv._identity.value)
