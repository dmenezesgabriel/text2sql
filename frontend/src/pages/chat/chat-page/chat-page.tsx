import React, { useCallback } from 'react';

import { sendChatMessage } from '@/features/chat/api/chat-api';
import { useChatStore } from '@/features/chat/model/store';
import { ChatInput } from '@/features/chat/ui/chat-input';
import { ChatMessage } from '@/features/chat/ui/chat-message';

const pageStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
};

const messagesStyle: React.CSSProperties = {
  flex: 1,
  overflow: 'auto',
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--spacing-sm)',
  padding: 'var(--spacing-md)',
};

/**
 *
 */
function generateId(): string {
  return crypto.randomUUID();
}

/**
 *
 */
export function ChatPage() {
  const {
    messages,
    isStreaming,
    conversationId,
    addMessage,
    handleEvent,
    setErrorOnLastAssistant,
    setStreaming,
    setConversationId,
  } = useChatStore();

  const handleSend = useCallback(
    (content: string) => {
      const convId = conversationId || generateId();
      if (!conversationId) setConversationId(convId);

      addMessage({
        id: generateId(),
        role: 'user',
        content,
        createdAt: new Date().toISOString(),
      });

      setStreaming(true);

      addMessage({
        id: generateId(),
        role: 'assistant',
        content: '',
        createdAt: new Date().toISOString(),
      });

      sendChatMessage(
        content,
        convId,
        (event) => {
          handleEvent(event);
        },
        (error) => {
          setErrorOnLastAssistant(`Request failed: ${error.message}. Please try again.`);
          setStreaming(false);
        },
        () => {
          setStreaming(false);
        },
      );
    },
    [
      conversationId,
      addMessage,
      handleEvent,
      setErrorOnLastAssistant,
      setStreaming,
      setConversationId,
    ],
  );

  return (
    <div style={pageStyle}>
      <div style={messagesStyle}>
        {messages.length === 0 ? (
          <bi-empty-state
            heading="Generative Business Intelligence"
            description="Ask a question about your data to get started."
          />
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}
      </div>
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
