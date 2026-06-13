import React from 'react';

import type { AgentMessage } from '@/entities/agent/types';

interface ChatMessageProps {
  readonly message: AgentMessage;
}

const containerStyle: React.CSSProperties = {
  display: 'flex',
  gap: 'var(--spacing-md)',
  padding: 'var(--spacing-md)',
  borderRadius: 'var(--radius-md)',
  marginBottom: 'var(--spacing-sm)',
};

const userStyle: React.CSSProperties = {
  ...containerStyle,
  background: 'var(--color-primary)',
  color: '#ffffff',
  alignSelf: 'flex-end',
};

const assistantStyle: React.CSSProperties = {
  ...containerStyle,
  background: 'var(--color-bg-secondary)',
  alignSelf: 'flex-start',
};

const bubbleStyle: React.CSSProperties = {
  maxWidth: '70%',
  borderRadius: 'var(--radius-md)',
  padding: 'var(--spacing-sm) var(--spacing-md)',
};

/**
 *
 * @param root0
 * @param root0.message
 */
export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const style = {
    ...bubbleStyle,
    ...(isUser ? userStyle : assistantStyle),
  };

  return (
    <div
      style={{
        ...style,
        alignSelf: isUser ? 'flex-end' : 'flex-start',
      }}
    >
      {message.content}
    </div>
  );
}
