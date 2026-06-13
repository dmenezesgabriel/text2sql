import { JSONUIProvider, Renderer } from '@json-render/react';
import React from 'react';

import type { AgentMessage } from '@/entities/agent/types';
import { registry } from '@/widgets/json-render/registry';

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
      {!isUser && message.spec ? (
        <JSONUIProvider registry={registry}>
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment */}
          <Renderer spec={message.spec as any} registry={registry} />
        </JSONUIProvider>
      ) : (
        message.content
      )}
    </div>
  );
}
