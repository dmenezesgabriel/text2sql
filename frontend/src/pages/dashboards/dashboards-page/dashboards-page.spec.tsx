import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { DashboardsPage } from './dashboards-page';

/**
 *
 */
function renderPage() {
  return render(
    <MemoryRouter>
      <DashboardsPage />
    </MemoryRouter>,
  );
}

describe('DashboardsPage', () => {
  it('renders the page heading element', () => {
    const { container } = renderPage();
    const header = container.querySelector('bi-page-header');
    expect(header).toBeTruthy();
    expect(header?.getAttribute('heading')).toBe('Dashboards');
  });

  it('renders without crashing', () => {
    expect(() => renderPage()).not.toThrow();
  });
});
