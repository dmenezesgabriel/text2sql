import { describe, expect, it } from 'vitest';

import { biCatalog } from './catalog';

describe('biCatalog', () => {
  it('registers all four custom actions in the prompt', () => {
    const prompt = biCatalog.prompt();
    expect(prompt).toContain('save_as_question');
    expect(prompt).toContain('add_to_dashboard');
    expect(prompt).toContain('export_data');
    expect(prompt).toContain('drill_down');
  });

  it('registers all six visualization components in the prompt', () => {
    const prompt = biCatalog.prompt();
    for (const component of [
      'BarChart',
      'LineChart',
      'PieChart',
      'DataTable',
      'Metric',
      'NarrativeText',
    ]) {
      expect(prompt).toContain(component);
    }
  });
});
