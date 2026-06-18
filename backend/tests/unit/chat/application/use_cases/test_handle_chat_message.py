from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import patch
from uuid import uuid4

from src.chat.application.ports.i_conversation_repository import ConversationSummary
from src.chat.application.use_cases.handle_chat_message import (
    AgentConfig,
    HandleChatMessageUseCase,
    ProcessMessageRequest,
)
from src.chat.domain.entities import Conversation
from src.chat.domain.value_objects import (
    AgentEvent,
    ConversationId,
    SpecFragmentEvent,
    ThinkingEvent,
)
from src.shared.domain.base import EntityId


class FakeConversationRepository:
    def __init__(self) -> None:
        self._store: dict[str, Conversation] = {}

    def load(self, conversation_id: ConversationId) -> Conversation | None:
        return self._store.get(str(conversation_id.value))

    def save(self, conversation: Conversation) -> None:
        self._store[str(conversation._identity.value)] = conversation

    def delete(self, conversation_id: ConversationId) -> None:
        self._store.pop(str(conversation_id.value), None)

    def find_all(self) -> list[ConversationSummary]:
        return []


class FakeOrchestrator:
    def __init__(self, events: list[AgentEvent]) -> None:
        self._events = events

    async def run(
        self,
        content: str,
        conversation_id: object,
    ) -> AsyncIterator[AgentEvent]:
        for event in self._events:
            yield event

    async def get_messages(self, conversation_id: object) -> list[dict]:
        return []


class _CapturingOrchestrator:
    def __init__(self) -> None:
        self.received_content: str | None = None
        self.received_conversation_id: object = None

    async def run(self, content: str, conversation_id: object) -> AsyncIterator[AgentEvent]:
        self.received_content = content
        self.received_conversation_id = conversation_id
        return
        yield  # type: ignore[misc]

    async def get_messages(self, conversation_id: object) -> list[dict]:
        return []


class TestHandleChatMessageUseCase:
    def setup_method(self) -> None:
        self.repo = FakeConversationRepository()

    def _make_use_case(self, events: list[AgentEvent]) -> HandleChatMessageUseCase:
        return HandleChatMessageUseCase(
            conversations=self.repo,
            agent=AgentConfig(_orchestrator=FakeOrchestrator(events)),
        )

    async def _collect(self, use_case: HandleChatMessageUseCase, content: str) -> list[AgentEvent]:
        request = ProcessMessageRequest(content=content, conversation_id=uuid4())
        return [event async for event in use_case.execute(request)]

    async def test_yields_thinking_event(self) -> None:
        use_case = self._make_use_case([])
        events = await self._collect(use_case, "What is revenue?")
        assert any(isinstance(e, ThinkingEvent) for e in events)

    async def test_yields_orchestrator_events(self) -> None:
        spec = SpecFragmentEvent(_payload={"root": "x", "elements": {}})
        use_case = self._make_use_case([spec])
        events = await self._collect(use_case, "What is revenue?")
        assert spec in events

    async def test_saves_conversation_after_execute(self) -> None:
        use_case = self._make_use_case([])
        await self._collect(use_case, "Question?")
        assert len(self.repo._store) == 1

    async def test_creates_new_conversation_when_not_found(self) -> None:
        use_case = self._make_use_case([])
        events = await self._collect(use_case, "Hello")
        assert len(events) > 0

    async def test_reuses_existing_conversation(self) -> None:
        uid = uuid4()
        existing = Conversation(identity=EntityId(uid))
        self.repo._store[str(uid)] = existing
        use_case = self._make_use_case([])
        request = ProcessMessageRequest(content="Hi", conversation_id=uid)
        [_ async for _ in use_case.execute(request)]
        # Same conversation object is saved back (not a new one)
        assert self.repo._store[str(uid)] is existing

    async def test_new_conversation_gets_title_from_content(self) -> None:
        use_case = self._make_use_case([])
        await self._collect(use_case, "What is total revenue?")
        saved = next(iter(self.repo._store.values()))
        assert saved._title == "What is total revenue?"

    async def test_existing_conversation_title_not_overwritten(self) -> None:
        uid = uuid4()
        existing = Conversation(identity=EntityId(uid))
        existing.set_title("Original title")
        self.repo._store[str(uid)] = existing
        use_case = self._make_use_case([])
        request = ProcessMessageRequest(content="New message", conversation_id=uid)
        [_ async for _ in use_case.execute(request)]
        assert self.repo._store[str(uid)]._title == "Original title"

    async def test_thinking_event_message_is_exact(self) -> None:
        use_case = self._make_use_case([])
        events = await self._collect(use_case, "Hello")
        thinking = [e for e in events if isinstance(e, ThinkingEvent)]
        assert len(thinking) == 1
        assert thinking[0].message == "Processing your question..."

    async def test_orchestrator_receives_exact_content(self) -> None:
        capturing = _CapturingOrchestrator()
        use_case = HandleChatMessageUseCase(
            conversations=self.repo,
            agent=AgentConfig(_orchestrator=capturing),
        )
        request = ProcessMessageRequest(content="What is revenue?", conversation_id=uuid4())
        [_ async for _ in use_case.execute(request)]
        assert capturing.received_content == "What is revenue?"

    async def test_orchestrator_receives_non_none_conversation_id(self) -> None:
        capturing = _CapturingOrchestrator()
        use_case = HandleChatMessageUseCase(
            conversations=self.repo,
            agent=AgentConfig(_orchestrator=capturing),
        )
        request = ProcessMessageRequest(content="Q", conversation_id=uuid4())
        [_ async for _ in use_case.execute(request)]
        assert capturing.received_conversation_id is not None

    async def test_process_message_request_conversation_id_preserved(self) -> None:
        from src.chat.domain.value_objects import ConversationId

        uid = uuid4()
        req = ProcessMessageRequest(content="test", conversation_id=uid)
        assert req._conversation_id == ConversationId(uid)

    async def test_new_conversation_stored_under_correct_id(self) -> None:
        uid = uuid4()
        use_case = self._make_use_case([])
        request = ProcessMessageRequest(content="Hello", conversation_id=uid)
        [_ async for _ in use_case.execute(request)]
        assert str(uid) in self.repo._store

    async def test_logs_chat_start_with_correct_args(self) -> None:
        uid = uuid4()
        use_case = self._make_use_case([])
        request = ProcessMessageRequest(content="Q", conversation_id=uid)
        with patch("src.chat.application.use_cases.handle_chat_message._logger") as mock_log:
            [_ async for _ in use_case.execute(request)]
        mock_log.info.assert_any_call("chat.start", extra={"conversation_id": str(uid)})

    async def test_logs_chat_complete_with_correct_args(self) -> None:
        uid = uuid4()
        use_case = self._make_use_case([])
        request = ProcessMessageRequest(content="Q", conversation_id=uid)
        with patch("src.chat.application.use_cases.handle_chat_message._logger") as mock_log:
            [_ async for _ in use_case.execute(request)]
        mock_log.info.assert_any_call("chat.complete", extra={"conversation_id": str(uid)})
