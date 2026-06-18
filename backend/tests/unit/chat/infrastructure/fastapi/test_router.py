from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

from fastapi.testclient import TestClient

from src.chat.application.ports.i_conversation_repository import ConversationSummary
from src.chat.domain.value_objects import (
    AgentEvent,
    ConversationId,
    ErrorEvent,
    Parameters,
    SpecFragmentEvent,
    ThinkingEvent,
    ToolCallEvent,
    ToolName,
)
from src.chat.infrastructure.fastapi.router import _serialize_event, create_chat_router


class _FakeRepo:
    def __init__(self, summaries: list[ConversationSummary]) -> None:
        self._summaries = summaries

    def find_all(self) -> list[ConversationSummary]:
        return self._summaries

    def save(self, conv: object) -> None: ...
    def load(self, cid: object) -> None:
        return None

    def delete(self, cid: object) -> None: ...


class _FakeOrchestrator:
    def __init__(self, messages: list[dict]) -> None:
        self._messages = messages

    async def run(self, content: str, conversation_id: object) -> AsyncIterator[AgentEvent]:
        return
        yield  # type: ignore[misc]

    async def get_messages(self, conversation_id: ConversationId) -> list[dict]:
        return self._messages


class TestSerializeEvent:
    def test_thinking_event(self) -> None:
        result = _serialize_event(ThinkingEvent(message="processing"))
        assert result["type"] == "ThinkingEvent"
        assert result["payload"] == "processing"

    def test_tool_call_event(self) -> None:
        event = ToolCallEvent(
            _tool_name=ToolName("sql_generator"),
            _parameters=Parameters({"sql": "SELECT 1"}),
        )
        result = _serialize_event(event)
        assert result["type"] == "ToolCallEvent"
        assert result["payload"]["tool_name"] == "sql_generator"

    def test_spec_fragment_event(self) -> None:
        payload = {
            "root": "answer",
            "elements": {"answer": {"type": "NarrativeText", "props": {"content": "ok"}}},
        }
        event = SpecFragmentEvent(_payload=payload)
        result = _serialize_event(event)
        assert result["type"] == "SpecFragmentEvent"
        assert result["payload"] == payload

    def test_error_event(self) -> None:
        event = ErrorEvent(_message="something failed")
        result = _serialize_event(event)
        assert result["type"] == "ErrorEvent"
        assert result["payload"] == "something failed"

    def test_unknown_event_fallback(self) -> None:
        class UnknownEvent:
            pass

        result = _serialize_event(UnknownEvent())  # type: ignore[arg-type]
        assert result["type"] == "UnknownEvent"

    def test_unknown_event_has_payload_key(self) -> None:
        class UnknownEvent:
            pass

        result = _serialize_event(UnknownEvent())  # type: ignore[arg-type]
        assert "payload" in result

    def test_unknown_event_payload_is_empty_dict(self) -> None:
        class UnknownEvent:
            pass

        result = _serialize_event(UnknownEvent())  # type: ignore[arg-type]
        assert result["payload"] == {}


class TestCreateChatRouter:
    def test_router_is_created(self) -> None:
        router = create_chat_router()
        assert router is not None

    def test_router_prefix(self) -> None:
        router = create_chat_router()
        assert router.prefix == "/api/v1"

    def test_router_has_chat_tag(self) -> None:
        router = create_chat_router()
        assert "chat" in (router.tags or [])


class TestListConversationsEndpoint:
    def _client(self, summaries: list[ConversationSummary]) -> TestClient:
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(create_chat_router(conversation_repo=_FakeRepo(summaries)))
        return TestClient(app)

    def test_returns_200_with_conversations_key(self) -> None:
        summary = ConversationSummary(
            id=str(uuid4()),
            title="Sales query",
            updated_at="2024-01-01T00:00:00",
        )
        client = self._client([summary])
        resp = client.get("/api/v1/conversations")
        assert resp.status_code == 200
        assert "conversations" in resp.json()

    def test_returns_conversation_fields(self) -> None:
        uid = str(uuid4())
        summary = ConversationSummary(
            id=uid,
            title="Revenue chart",
            updated_at="2024-06-01T10:00:00",
        )
        client = self._client([summary])
        data = client.get("/api/v1/conversations").json()
        conv = data["conversations"][0]
        assert conv["id"] == uid
        assert conv["title"] == "Revenue chart"
        assert conv["updated_at"] == "2024-06-01T10:00:00"

    def test_returns_empty_list_when_no_conversations(self) -> None:
        client = self._client([])
        data = client.get("/api/v1/conversations").json()
        assert data["conversations"] == []

    def test_returns_501_when_repo_not_wired(self) -> None:
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(create_chat_router())
        client = TestClient(app)
        resp = client.get("/api/v1/conversations")
        assert resp.status_code == 501


class TestGetConversationMessagesEndpoint:
    def _client(self, messages: list[dict]) -> TestClient:
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(create_chat_router(orchestrator=_FakeOrchestrator(messages)))
        return TestClient(app)

    def test_returns_200_with_messages_key(self) -> None:
        msgs = [{"role": "user", "content": "Hello"}]
        client = self._client(msgs)
        uid = str(uuid4())
        resp = client.get(f"/api/v1/conversations/{uid}/messages")
        assert resp.status_code == 200
        assert "messages" in resp.json()

    def test_returns_messages_from_orchestrator(self) -> None:
        msgs = [
            {"role": "user", "content": "Show sales"},
            {"role": "assistant", "content": "Here is the chart"},
        ]
        client = self._client(msgs)
        uid = str(uuid4())
        data = client.get(f"/api/v1/conversations/{uid}/messages").json()
        assert data["messages"] == msgs

    def test_returns_501_when_orchestrator_not_wired(self) -> None:
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(create_chat_router())
        client = TestClient(app)
        uid = str(uuid4())
        resp = client.get(f"/api/v1/conversations/{uid}/messages")
        assert resp.status_code == 501
