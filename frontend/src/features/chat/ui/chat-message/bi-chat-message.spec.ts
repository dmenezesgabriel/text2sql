import { describe, expect, it } from 'vitest';

import { BiChatMessage } from './bi-chat-message';

describe('BiChatMessage', () => {
  it('is a defined custom element class', () => {
    expect(BiChatMessage).toBeDefined();
  });

  it('has default _saved of false', () => {
    const el = new BiChatMessage();
    expect(el['_saved']).toBe(false);
  });

  it('has default _saving of false', () => {
    const el = new BiChatMessage();
    expect(el['_saving']).toBe(false);
  });

  it('skips _saveAsQuestion when already saved', async () => {
    const el = new BiChatMessage();
    el.message = {
      id: 'm-1',
      role: 'assistant',
      content: '',
      spec: { component: 'BarChart', props: {} },
      createdAt: '',
    };
    el['_saved'] = true;
    // Should exit immediately — no dispatch, no throw
    await el['_saveAsQuestion']();
    expect(el['_saving']).toBe(false);
  });

  it('skips _saveAsQuestion when no spec', async () => {
    const el = new BiChatMessage();
    el.message = { id: 'm-2', role: 'assistant', content: '', createdAt: '' };
    await el['_saveAsQuestion']();
    expect(el['_saving']).toBe(false);
  });
});
