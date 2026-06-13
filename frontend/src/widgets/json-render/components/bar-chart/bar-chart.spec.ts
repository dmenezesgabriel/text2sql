import './bar-chart';

import { describe, expect, it } from 'vitest';

describe('BarChartElement', () => {
  it('is defined as a custom element', () => {
    expect(customElements.get('bi-bar-chart')).toBeDefined();
  });
});
