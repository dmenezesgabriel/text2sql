import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { ChatMessage } from './chat-message';

describe('ChatMessage', () => {
  it('renders user message', () => {
    render(<ChatMessage message={{ id: '1', role: 'user', content: 'Hello', createdAt: '' }} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('renders assistant message', () => {
    render(
      <ChatMessage message={{ id: '2', role: 'assistant', content: 'Hi there', createdAt: '' }} />,
    );
    expect(screen.getByText('Hi there')).toBeInTheDocument();
  });
});
