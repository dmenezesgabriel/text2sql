import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { ChatInput } from './chat-input';

describe('ChatInput', () => {
  it('renders input and send button', () => {
    render(<ChatInput onSend={() => {}} disabled={false} />);
    expect(screen.getByPlaceholderText('Ask a question about your data...')).toBeInTheDocument();
    expect(screen.getByText('Send')).toBeInTheDocument();
  });

  it('calls onSend when submitting', async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    render(<ChatInput onSend={onSend} disabled={false} />);
    await user.type(screen.getByPlaceholderText('Ask a question about your data...'), 'hello');
    await user.click(screen.getByText('Send'));
    expect(onSend).toHaveBeenCalledWith('hello');
  });
});
