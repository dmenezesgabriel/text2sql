import { describe, expect, it } from 'vitest';

import { BiDatasetDetail } from './bi-dataset-detail';

describe('BiDatasetDetail', () => {
  it('is a defined custom element class', () => {
    expect(BiDatasetDetail).toBeDefined();
  });

  it('has default datasetId of empty string', () => {
    const el = new BiDatasetDetail();
    expect(el.datasetId).toBe('');
  });

  it('starts with null dataset', () => {
    const el = new BiDatasetDetail();
    expect(el['_dataset']).toBeNull();
  });

  it('starts with null preview', () => {
    const el = new BiDatasetDetail();
    expect(el['_preview']).toBeNull();
  });

  it('starts with isLoading false', () => {
    const el = new BiDatasetDetail();
    expect(el['_isLoading']).toBe(false);
  });
});
