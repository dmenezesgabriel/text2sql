import './data-table';

import { describe, expect, it } from 'vitest';

describe('DataTableElement', () => {
  it('is defined as a custom element', () => {
    expect(customElements.get('bi-data-table')).toBeDefined();
  });
});
