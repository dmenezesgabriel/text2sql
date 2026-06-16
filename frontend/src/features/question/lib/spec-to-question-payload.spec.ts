import { describe, expect, it } from 'vitest';

import { specToQuestionPayload } from './spec-to-question-payload';

describe('specToQuestionPayload', () => {
  it('maps a full spec to a create-question payload', () => {
    const payload = specToQuestionPayload({
      meta: { title: 'Revenue', sql: 'SELECT 1', dataset_id: 'ds-1', format: 'chart' },
      root: 'main',
      elements: { main: { type: 'BarChart', props: { color: 'blue' } } },
    });

    expect(payload).toEqual({
      title: 'Revenue',
      sql: 'SELECT 1',
      dataset_id: 'ds-1',
      viz_component: 'BarChart',
      viz_format: 'CHART',
      viz_props: { color: 'blue' },
    });
  });

  it('defaults missing fields for an empty spec', () => {
    expect(specToQuestionPayload({})).toEqual({
      title: 'Untitled question',
      sql: '',
      dataset_id: '',
      viz_component: '',
      viz_format: 'CHART',
      viz_props: {},
    });
  });

  it('resolves the root element via a non-default root key', () => {
    const payload = specToQuestionPayload({
      root: 'tile-1',
      elements: { 'tile-1': { type: 'PieChart', props: {} } },
    });

    expect(payload.viz_component).toBe('PieChart');
  });
});
