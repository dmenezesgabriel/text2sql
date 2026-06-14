from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.chat.application.use_cases.replay_conversation import ReplayConversationUseCase
from src.chat.domain.entities import (
    Conversation,
    MessageBody,
    MessageIdentity,
)
from src.chat.domain.value_objects import (
    AgentEvent,
    ConversationId,
    MessageContent,
    MessageRole,
    ThinkingEvent,
)
from src.shared.domain.base import CreatedAt, EntityId


class FakeConversationRepository:
    def __init__(self, conversations: dict[str, Conversation]) -> None:
        self._conversations = conversations

    def load(self, conversation_id: ConversationId) -> Conversation | None:
        return self._conversations.get(str(conversation_id.value))

    def save(self, conversation: Conversation) -> None:
        self._conversations[str(conversation._identity.value)] = conversation

    def delete(self, conversation_id: ConversationId) -> None:
        self._conversations.pop(str(conversation_id.value), None)


class FakeOrchestrator:
    def __init__(self, events: list[AgentEvent]) -> None:
        self._events = events

    async def run(
        self,
        message: object,
        conversation: object,
        toolkit: object,
    ) -> AsyncIterator[AgentEvent]:
        for event in self._events:
            yield event


class FakeToolKit:
    def register(self, tool: object) -> None:
        pass

    def find(self, name: object) -> None:
        return None

    def all(self) -> list[object]:
        return []


def _make_conversation_with_user_message(conv_id: ConversationId) -> Conversation:
    from src.chat.domain.entities import Message

    conv = Conversation(identity=EntityId(conv_id.value))
    conv.add_user_message("Original question")
    assistant_msg = Message(
        identity=MessageIdentity(
            _id=EntityId(uuid4()),
            _role=MessageRole.ASSISTANT,
            _timestamp=CreatedAt(datetime.now(UTC)),
        ),
        body=MessageBody(
            _content=MessageContent("Answer"),
            _tool_call=None,
        ),
    )
    conv._history.append(assistant_msg)
    return conv


class TestReplayConversationUseCase:
    def setup_method(self) -> None:
        self.toolkit = FakeToolKit()

    def _make_use_case(
        self,
        conversations: dict[str, Conversation],
        events: list[AgentEvent],
    ) -> ReplayConversationUseCase:
        return ReplayConversationUseCase(
            conversations=FakeConversationRepository(conversations),
            orchestrator=FakeOrchestrator(events),
            toolkit=self.toolkit,
        )

    async def test_raises_when_conversation_not_found(self) -> None:
        use_case = self._make_use_case({}, [])
        missing_id = ConversationId(uuid4())
        with pytest.raises(ValueError, match="not found"):
            async for _ in use_case.execute(missing_id, None):
                pass

    async def test_replays_user_messages(self) -> None:
        conv_id = ConversationId(uuid4())
        conv = _make_conversation_with_user_message(conv_id)
        thinking = ThinkingEvent("Replaying...")
        use_case = self._make_use_case({str(conv_id.value): conv}, [thinking])
        events = [e async for e in use_case.execute(conv_id, None)]
        assert thinking in events
