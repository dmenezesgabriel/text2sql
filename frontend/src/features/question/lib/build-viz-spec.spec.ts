import { describe, expect, it } from 'vitest';

import { buildVizSpec } from './build-viz-spec';

describe('buildVizSpec', () => {
  it('builds a spec with root=main pointing to the viz component', () => {
    const result = buildVizSpec({
      vizComponent: 'BarChart',
      vizProps: { title: 'Revenue', xAxis: 'Month', yAxis: 'USD', data: [] },
      vizChildren: ['child-1'],
    });

    expect(result).toEqual({
      root: 'main',
      elements: {
        main: {
          type: 'BarChart',
          props: { title: 'Revenue', xAxis: 'Month', yAxis: 'USD', data: [] },
          children: ['child-1'],
        },
      },
    });
  });

  it('defaults children to empty array when vizChildren is undefined', () => {
    const result = buildVizSpec({
      vizComponent: 'Metric',
      vizProps: { label: 'Total', value: '100' },
    });

    expect(result.elements['main'].children).toEqual([]);
  });
});
