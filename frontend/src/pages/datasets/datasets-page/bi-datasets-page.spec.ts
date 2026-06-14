import { describe, expect, it } from 'vitest';

import { BiDatasetsPage } from './bi-datasets-page';

describe('BiDatasetsPage', () => {
  it('is a defined custom element class', () => {
    expect(BiDatasetsPage).toBeDefined();
  });

  it('starts with empty datasets', () => {
    const el = new BiDatasetsPage();
    expect(el['_datasets']).toEqual([]);
  });

  it('starts with isLoading false', () => {
    const el = new BiDatasetsPage();
    expect(el['_isLoading']).toBe(false);
  });

  it('starts with empty error', () => {
    const el = new BiDatasetsPage();
    expect(el['_error']).toBe('');
  });

  it('_handleRegistered appends dataset to list', () => {
    const el = new BiDatasetsPage();
    const ds = { id: 'ds-1', name: 'sales', kind: 'file' as const, columns: [] };
    el['_handleRegistered'](new CustomEvent('dataset-registered', { detail: ds }));
    expect(el['_datasets']).toEqual([ds]);
  });
});
