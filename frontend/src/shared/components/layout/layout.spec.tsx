import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { Layout } from './layout';

describe('Layout', () => {
  it('renders children', () => {
    render(
      <BrowserRouter>
        <Layout>Page Content</Layout>
      </BrowserRouter>,
    );
    expect(screen.getByText('Page Content')).toBeInTheDocument();
  });
});
