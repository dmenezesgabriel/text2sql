import { describe, expect, it } from 'vitest';

import { BiInput } from './bi-input';

describe('BiInput', () => {
  it('is a defined custom element class', () => {
    expect(BiInput).toBeDefined();
  });

  it('has default empty value', () => {
    const el = new BiInput();
    expect(el.value).toBe('');
  });

  it('stores label property', () => {
    const el = new BiInput();
    el.label = 'Column name';
    expect(el.label).toBe('Column name');
  });

  it('stores error property', () => {
    const el = new BiInput();
    el.error = 'Required';
    expect(el.error).toBe('Required');
  });

  it('has disabled property', () => {
    const el = new BiInput();
    el.disabled = true;
    expect(el.disabled).toBe(true);
  });
});
