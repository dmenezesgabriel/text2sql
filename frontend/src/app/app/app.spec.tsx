import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { App } from './app';

describe('App', () => {
  it('renders the app shell', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>,
    );
    expect(screen.getByText('Generative Business Intelligence')).toBeInTheDocument();
  });
});
