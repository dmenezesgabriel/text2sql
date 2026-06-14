import { render } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { DashboardDetail } from './dashboard-detail';

/**
 *
 * @param id
 */
function renderPage(id = '1') {
  return render(
    <MemoryRouter initialEntries={[`/dashboards/${id}`]}>
      <Routes>
        <Route path="/dashboards/:id" element={<DashboardDetail />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('DashboardDetail', () => {
  it('renders the page heading element before data loads', () => {
    const { container } = renderPage();
    const header = container.querySelector('bi-page-header');
    expect(header).toBeTruthy();
    expect(header?.getAttribute('heading')).toBe('Dashboard');
  });

  it('renders without crashing', () => {
    expect(() => renderPage()).not.toThrow();
  });
});
