import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { App } from './app';

describe('App', () => {
  it('renders the app shell with skip-nav and header element', () => {
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>,
    );
    expect(screen.getByText('Skip to content')).toBeInTheDocument();
    expect(container.querySelector('bi-header')).toBeTruthy();
  });
});
