import type { AgentEvent } from '@/entities/agent/types';
import { chatStream } from '@/shared/api/chat-stream';

/**
 *
 * @param message
 * @param conversationId
 * @param onEvent
 * @param onError
 * @param onClose
 */
export function sendChatMessage(
  message: string,
  conversationId: string | null,
  onEvent: (event: AgentEvent) => void,
  onError: (error: Error) => void,
  onClose: () => void,
): void {
  chatStream(
    { message, conversation_id: conversationId ?? undefined },
    (messageEvent) => {
      try {
        const data = JSON.parse(messageEvent.data);
        onEvent(data as AgentEvent);
      } catch {
        onEvent({
          type: 'SpecFragmentEvent',
          payload: messageEvent.data,
        });
      }
    },
    onError,
    onClose,
  );
}
