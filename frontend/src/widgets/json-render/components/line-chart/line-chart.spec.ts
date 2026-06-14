import './line-chart';

import { describe, expect, it } from 'vitest';

describe('LineChartElement', () => {
  it('is defined as a custom element', () => {
    expect(customElements.get('bi-line-chart')).toBeDefined();
  });
});
