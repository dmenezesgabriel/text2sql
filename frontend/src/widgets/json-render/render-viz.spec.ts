import { nothing } from 'lit';
import { describe, expect, it } from 'vitest';

import { renderViz } from './render-viz';

describe('renderViz', () => {
  it.each([
    ['BarChart', 'bi-bar-chart'],
    ['LineChart', 'bi-line-chart'],
    ['PieChart', 'bi-pie-chart'],
    ['DataTable', 'bi-data-table'],
    ['Metric', 'bi-metric'],
    ['NarrativeText', 'bi-narrative-text'],
  ])('renders a %s as a %s template', (component, tagName) => {
    const result = renderViz(component, {});
    expect(result).not.toBe(nothing);
    expect(String((result as { strings: readonly string[] }).strings)).toContain(tagName);
  });

  it('returns nothing for an unknown component', () => {
    expect(renderViz('UnknownComponent', {})).toBe(nothing);
  });
});
