import { describe, expect, it } from 'vitest';

import { BiBadge } from './bi-badge';

describe('BiBadge', () => {
  it('is a defined custom element class', () => {
    expect(BiBadge).toBeDefined();
    expect(typeof BiBadge).toBe('function');
  });

  it('has default variant of "default"', () => {
    const el = new BiBadge();
    expect(el.variant).toBe('default');
  });

  it('accepts all valid variants', () => {
    const el = new BiBadge();
    const variants = ['default', 'primary', 'success', 'warning', 'error', 'mono'] as const;
    for (const v of variants) {
      el.variant = v;
      expect(el.variant).toBe(v);
    }
  });
});
