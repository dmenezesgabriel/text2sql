import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Header } from './header';

describe('Header', () => {
  it('renders the app title', () => {
    render(<Header />);
    expect(screen.getByText('Generative BI')).toBeInTheDocument();
  });

  it('has banner landmark role', () => {
    render(<Header />);
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('renders children in action area', () => {
    render(
      <Header>
        <button>Action</button>
      </Header>,
    );
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });
});
