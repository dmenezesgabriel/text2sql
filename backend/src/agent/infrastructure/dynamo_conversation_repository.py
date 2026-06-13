from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

from src.agent.application.ports.i_conversation_repository import (
    IConversationRepository,
)
from src.agent.domain.entities import (
    Conversation,
    Message,
    MessageBody,
    MessageIdentity,
    Messages,
)
from src.agent.domain.value_objects import (
    ConversationId,
    MessageContent,
    MessageRole,
    Parameters,
    ToolCallEvent,
    ToolName,
)
from src.shared.domain.base import CreatedAt, EntityId
from src.shared.infrastructure.dynamo_models import ConversationModel


class DynamoConversationRepository(IConversationRepository):
    def save(self, conversation: Conversation) -> None:
        messages = [
            {
                "id": str(msg._identity._id.value),
                "role": msg._identity._role.name,
                "timestamp": msg._identity._timestamp.value.isoformat(),
                "content": msg._body._content.value,
                "tool_call": (
                    {
                        "tool_name": msg._body._tool_call._tool_name.value,
                        "parameters": msg._body._tool_call._parameters.value,
                    }
                    if msg._body._tool_call is not None
                    else None
                ),
            }
            for msg in conversation._history.to_list()
        ]
        model = ConversationModel(
            id=str(conversation._identity.value),
            state=conversation._state.name,
            messages=json.dumps(messages),
            updated_at=datetime.utcnow().isoformat(),
        )
        model.save()

    def load(self, conversation_id: ConversationId) -> Conversation | None:
        try:
            model = ConversationModel.get(str(conversation_id.value))
        except ConversationModel.DoesNotExist:
            return None
        return self._doc_to_conversation(model)

    def delete(self, conversation_id: ConversationId) -> None:
        try:
            ConversationModel.get(str(conversation_id.value)).delete()
        except ConversationModel.DoesNotExist:
            return

    def _doc_to_conversation(self, model: ConversationModel) -> Conversation:
        messages_data = json.loads(model.messages)
        messages = Messages()
        for msg_doc in messages_data:
            tool_call = None
            tc = msg_doc.get("tool_call")
            if tc is not None:
                tool_call = ToolCallEvent(
                    _tool_name=ToolName(tc["tool_name"]),
                    _parameters=Parameters(tc["parameters"]),
                )
            message = Message(
                identity=MessageIdentity(
                    _id=EntityId(UUID(msg_doc["id"])),
                    _role=MessageRole[msg_doc["role"]],
                    _timestamp=CreatedAt(
                        datetime.fromisoformat(msg_doc["timestamp"]),
                    ),
                ),
                body=MessageBody(
                    _content=MessageContent(msg_doc["content"]),
                    _tool_call=tool_call,
                ),
            )
            messages.append(message)

        conversation = Conversation(
            identity=EntityId(UUID(model.id)),
            history=messages,
        )
        if model.state == "CLOSED":
            conversation.close()
        return conversation
