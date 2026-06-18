from __future__ import annotations

import json
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.chat.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.chat.application.ports.i_conversation_repository import IConversationRepository
from src.chat.application.use_cases.handle_chat_message import (
    HandleChatMessageUseCase,
    ProcessMessageRequest,
)
from src.chat.domain.value_objects import (
    AgentEvent,
    ConversationId,
    ErrorEvent,
    SpecFragmentEvent,
    ThinkingEvent,
    ToolCallEvent,
)


def _serialize_event(event: AgentEvent) -> dict[str, object]:  # noqa: PLR0911
    if isinstance(event, ThinkingEvent):
        return {"type": "ThinkingEvent", "payload": event.message}
    if isinstance(event, ToolCallEvent):
        return {"type": "ToolCallEvent", "payload": {"tool_name": event._tool_name.value}}
    if isinstance(event, SpecFragmentEvent):
        return {"type": "SpecFragmentEvent", "payload": event._payload}
    if isinstance(event, ErrorEvent):
        return {"type": "ErrorEvent", "payload": event._message}
    return {"type": "UnknownEvent", "payload": {}}


def create_chat_router(
    use_case: HandleChatMessageUseCase | None = None,
    conversation_repo: IConversationRepository | None = None,
    orchestrator: IAgentOrchestrator | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["chat"])

    @router.post("/chat")
    async def chat(
        body: dict[str, object],
        _use_case: HandleChatMessageUseCase | None = Depends(lambda: use_case),
    ):
        if _use_case is None:
            from fastapi.responses import JSONResponse  # noqa: PLC0415

            return JSONResponse(status_code=501, content={"error": "Chat use case not wired"})

        raw_id = body.get("conversation_id")
        conversation_id = UUID(str(raw_id)) if raw_id is not None else uuid4()
        request = ProcessMessageRequest(
            content=str(body.get("message", "")),
            conversation_id=conversation_id,
        )

        async def event_stream():
            async for event in _use_case.execute(request):
                yield f"data: {json.dumps(_serialize_event(event))}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    @router.get("/conversations")
    async def list_conversations(
        _repo: IConversationRepository | None = Depends(lambda: conversation_repo),
    ):
        if _repo is None:
            from fastapi.responses import JSONResponse  # noqa: PLC0415

            return JSONResponse(status_code=501, content={"error": "Conversation repo not wired"})

        summaries = _repo.find_all()
        return {
            "conversations": [
                {"id": s.id, "title": s.title, "updated_at": s.updated_at} for s in summaries
            ],
        }

    @router.get("/conversations/{conversation_id}/messages")
    async def get_conversation_messages(
        conversation_id: str,
        _orchestrator: IAgentOrchestrator | None = Depends(lambda: orchestrator),
    ):
        if _orchestrator is None:
            from fastapi.responses import JSONResponse  # noqa: PLC0415

            return JSONResponse(status_code=501, content={"error": "Orchestrator not wired"})

        conv_id = ConversationId(UUID(conversation_id))
        messages = await _orchestrator.get_messages(conv_id)
        return {"messages": messages}

    return router
