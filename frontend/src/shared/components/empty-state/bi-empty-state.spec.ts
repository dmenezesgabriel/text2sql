import { describe, expect, it } from 'vitest';

import { BiEmptyState } from './bi-empty-state';

describe('BiEmptyState', () => {
  it('is a defined custom element class', () => {
    expect(BiEmptyState).toBeDefined();
  });

  it('has heading property', () => {
    const el = new BiEmptyState();
    el.heading = 'No data';
    expect(el.heading).toBe('No data');
  });

  it('has description property', () => {
    const el = new BiEmptyState();
    el.description = 'Start by adding some data.';
    expect(el.description).toBe('Start by adding some data.');
  });
});
