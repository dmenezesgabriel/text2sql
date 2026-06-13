import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Providers } from './providers';

describe('Providers', () => {
  it('renders children', () => {
    render(<Providers>Child</Providers>);
    expect(screen.getByText('Child')).toBeInTheDocument();
  });
});
