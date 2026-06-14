import { describe, expect, it } from 'vitest';

import { BiDashboardsPage } from './bi-dashboards-page';

describe('BiDashboardsPage', () => {
  it('is a defined custom element class', () => {
    expect(BiDashboardsPage).toBeDefined();
  });

  it('starts with empty dashboards', () => {
    const el = new BiDashboardsPage();
    expect(el['_dashboards']).toEqual([]);
  });

  it('starts with isLoading false', () => {
    const el = new BiDashboardsPage();
    expect(el['_isLoading']).toBe(false);
  });

  it('starts with empty error', () => {
    const el = new BiDashboardsPage();
    expect(el['_error']).toBe('');
  });
});
