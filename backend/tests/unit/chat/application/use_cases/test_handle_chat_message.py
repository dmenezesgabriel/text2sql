from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

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
    TokenCount,
)


class FakeConversationRepository:
    def __init__(self) -> None:
        self._store: dict[str, Conversation] = {}

    def load(self, conversation_id: ConversationId) -> Conversation | None:
        return self._store.get(str(conversation_id.value))

    def save(self, conversation: Conversation) -> None:
        self._store[str(conversation._identity.value)] = conversation

    def delete(self, conversation_id: ConversationId) -> None:
        self._store.pop(str(conversation_id.value), None)


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


class FakeSummarizer:
    async def summarize(self, text: str) -> str:
        return f"Summary of: {text[:20]}"


class TestHandleChatMessageUseCase:
    def setup_method(self) -> None:
        self.repo = FakeConversationRepository()
        self.toolkit = FakeToolKit()
        self.summarizer = FakeSummarizer()

    def _make_use_case(
        self,
        events: list[AgentEvent],
        token_limit: TokenCount = TokenCount(10000),
    ) -> HandleChatMessageUseCase:
        return HandleChatMessageUseCase(
            conversations=self.repo,
            agent=AgentConfig(
                _orchestrator=FakeOrchestrator(events),
                _toolkit=self.toolkit,
                _summarizer=self.summarizer,
                _token_limit=token_limit,
            ),
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

    async def test_summarizes_when_token_limit_exceeded(self) -> None:
        # Token limit of 1 forces summarization on any non-empty message.
        use_case = self._make_use_case([], token_limit=TokenCount(1))
        await self._collect(use_case, "A message long enough to exceed the limit")
        saved = next(iter(self.repo._store.values()))
        # After summarization the history starts with a SYSTEM summary message.
        first_msg = saved._history.to_list()[0]
        assert "Summary of earlier conversation:" in first_msg._body._content.value
