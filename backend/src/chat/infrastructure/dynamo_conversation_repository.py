from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from src.chat.application.ports.i_conversation_repository import (
    IConversationRepository,
)
from src.chat.domain.entities import Conversation, ConversationState
from src.chat.domain.value_objects import ConversationId
from src.shared.domain.base import EntityId
from src.shared.infrastructure.dynamo_models import ConversationModel


class DynamoConversationRepository(IConversationRepository):
    def save(self, conversation: Conversation) -> None:
        model = ConversationModel(
            id=str(conversation._identity.value),
            state=conversation._state.name,
            updated_at=datetime.now(UTC).isoformat(),
        )
        model.save()

    def load(self, conversation_id: ConversationId) -> Conversation | None:
        try:
            model = ConversationModel.get(str(conversation_id.value))
        except ConversationModel.DoesNotExist:
            return None
        return _model_to_conversation(model)

    def delete(self, conversation_id: ConversationId) -> None:
        try:
            ConversationModel.get(str(conversation_id.value)).delete()
        except ConversationModel.DoesNotExist:
            return


def _model_to_conversation(model: ConversationModel) -> Conversation:
    conversation = Conversation(identity=EntityId(UUID(model.id)))
    if model.state == ConversationState.CLOSED.name:
        conversation.close()
    return conversation
