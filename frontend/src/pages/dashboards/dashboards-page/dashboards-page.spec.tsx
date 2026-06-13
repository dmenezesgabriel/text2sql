import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { DashboardsPage } from './dashboards-page';

describe('DashboardsPage', () => {
  it('renders title', () => {
    render(<DashboardsPage />);
    expect(screen.getByText('Dashboards')).toBeInTheDocument();
  });
});
