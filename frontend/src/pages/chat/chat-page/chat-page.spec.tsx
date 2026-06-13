import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { ChatPage } from './chat-page';

describe('ChatPage', () => {
  it('renders without crashing', () => {
    const { container } = render(
      <BrowserRouter>
        <ChatPage />
      </BrowserRouter>,
    );
    expect(container).toBeInTheDocument();
  });
});
