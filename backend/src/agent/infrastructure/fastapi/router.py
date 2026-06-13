from __future__ import annotations

from fastapi import APIRouter, Depends
from uuid import uuid4

from src.agent.application.use_cases.handle_chat_message import (
    HandleChatMessageUseCase, ProcessMessageRequest,
)


def create_chat_router(
    use_case: HandleChatMessageUseCase | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

    @router.post("")
    async def chat(
        body: dict,
        _use_case: HandleChatMessageUseCase | None = Depends(lambda: use_case),
    ):
        if _use_case is None:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=501,
                content={"error": "Chat use case not wired"},
            )

        request = ProcessMessageRequest(
            content=body.get("message", ""),
            conversation_id=body.get("conversation_id", uuid4()),
        )

        from fastapi.responses import StreamingResponse
        import json

        async def event_stream():
            async for event in _use_case.execute(request):
                yield f"data: {json.dumps({'type': type(event).__name__, 'payload': str(event)})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    return router
