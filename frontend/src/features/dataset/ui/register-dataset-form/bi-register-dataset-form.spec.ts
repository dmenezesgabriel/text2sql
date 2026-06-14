import { describe, expect, it } from 'vitest';

import { BiRegisterDatasetForm } from './bi-register-dataset-form';

describe('BiRegisterDatasetForm', () => {
  it('is a defined custom element class', () => {
    expect(BiRegisterDatasetForm).toBeDefined();
  });

  it('starts with empty name', () => {
    const el = new BiRegisterDatasetForm();
    expect(el['_name']).toBe('');
  });

  it('starts with empty s3Uri', () => {
    const el = new BiRegisterDatasetForm();
    expect(el['_s3Uri']).toBe('');
  });

  it('starts with isLoading false', () => {
    const el = new BiRegisterDatasetForm();
    expect(el['_isLoading']).toBe(false);
  });

  it('starts with empty error', () => {
    const el = new BiRegisterDatasetForm();
    expect(el['_error']).toBe('');
  });
});
