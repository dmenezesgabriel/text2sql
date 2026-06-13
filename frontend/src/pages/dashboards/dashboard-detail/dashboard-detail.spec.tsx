import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { DashboardDetail } from './dashboard-detail';

describe('DashboardDetail', () => {
  it('renders dashboard detail with id', () => {
    render(
      <MemoryRouter initialEntries={['/dashboards/1']}>
        <Routes>
          <Route path="/dashboards/:id" element={<DashboardDetail />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText(/Dashboard 1/)).toBeInTheDocument();
  });
});
