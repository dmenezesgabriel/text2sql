import { describe, expect, it } from 'vitest';

import { BiPageHeader } from './bi-page-header';

describe('BiPageHeader', () => {
  it('is a defined custom element class', () => {
    expect(BiPageHeader).toBeDefined();
  });

  it('stores heading property', () => {
    const el = new BiPageHeader();
    el.heading = 'Questions';
    expect(el.heading).toBe('Questions');
  });

  it('stores description property', () => {
    const el = new BiPageHeader();
    el.description = 'Saved queries';
    expect(el.description).toBe('Saved queries');
  });
});
