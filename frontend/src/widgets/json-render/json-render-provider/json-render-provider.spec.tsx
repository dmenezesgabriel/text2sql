import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { JsonRenderProvider } from './json-render-provider';

describe('JsonRenderProvider', () => {
  it('renders children', () => {
    render(<JsonRenderProvider>Content</JsonRenderProvider>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
});
