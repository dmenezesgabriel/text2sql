import { describe, expect, it } from 'vitest';

import { BiDashboardDetail } from './bi-dashboard-detail';

describe('BiDashboardDetail', () => {
  it('is a defined custom element class', () => {
    expect(BiDashboardDetail).toBeDefined();
  });

  it('has default dashboardId of empty string', () => {
    const el = new BiDashboardDetail();
    expect(el.dashboardId).toBe('');
  });

  it('starts with null dashboard', () => {
    const el = new BiDashboardDetail();
    expect(el['_dashboard']).toBeNull();
  });

  it('starts with empty tileQuestions', () => {
    const el = new BiDashboardDetail();
    expect(el['_tileQuestions']).toEqual({});
  });

  it('starts with isLoading false', () => {
    const el = new BiDashboardDetail();
    expect(el['_isLoading']).toBe(false);
  });
});
