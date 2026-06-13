import './narrative-text';

import { describe, expect, it } from 'vitest';

describe('NarrativeTextElement', () => {
  it('is defined as a custom element', () => {
    expect(customElements.get('bi-narrative-text')).toBeDefined();
  });
});
