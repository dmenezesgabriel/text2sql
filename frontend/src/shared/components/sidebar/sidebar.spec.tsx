import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { Sidebar } from './sidebar';

describe('Sidebar', () => {
  it('renders navigation links and new chat button', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>,
    );
    expect(screen.getByRole('button', { name: /new chat/i })).toBeInTheDocument();
    expect(screen.getByText('Questions')).toBeInTheDocument();
    expect(screen.getByText('Dashboards')).toBeInTheDocument();
    expect(screen.getByText('Datasets')).toBeInTheDocument();
  });
});
