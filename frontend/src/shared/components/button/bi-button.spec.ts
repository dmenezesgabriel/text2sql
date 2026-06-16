import { describe, expect, it } from 'vitest';

import { BiButton } from './bi-button';

describe('BiButton', () => {
  it('is a defined custom element class', () => {
    expect(BiButton).toBeDefined();
  });

  it('defaults to secondary variant', () => {
    const el = new BiButton();
    expect(el.variant).toBe('secondary');
  });

  it('defaults to button type', () => {
    const el = new BiButton();
    expect(el.type).toBe('button');
  });

  it('stores disabled property', () => {
    const el = new BiButton();
    el.disabled = true;
    expect(el.disabled).toBe(true);
  });

  it('accepts all variants', () => {
    const el = new BiButton();
    const variants = ['primary', 'secondary', 'ghost', 'danger'] as const;
    for (const v of variants) {
      el.variant = v;
      expect(el.variant).toBe(v);
    }
  });
});
