import './metric';

import { describe, expect, it } from 'vitest';

describe('MetricElement', () => {
  it('is defined as a custom element', () => {
    expect(customElements.get('bi-metric')).toBeDefined();
  });
});
