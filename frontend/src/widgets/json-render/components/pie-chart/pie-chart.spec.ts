import './pie-chart';

import { describe, expect, it } from 'vitest';

describe('PieChartElement', () => {
  it('is defined as a custom element', () => {
    expect(customElements.get('bi-pie-chart')).toBeDefined();
  });
});
