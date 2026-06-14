import { describe, expect, it } from 'vitest';

import { BiChatPage } from './bi-chat-page';

describe('BiChatPage', () => {
  it('is a defined custom element class', () => {
    expect(BiChatPage).toBeDefined();
  });

  it('starts with empty messages', () => {
    const el = new BiChatPage();
    expect(el['_messages']).toEqual([]);
  });

  it('starts with isStreaming false', () => {
    const el = new BiChatPage();
    expect(el['_isStreaming']).toBe(false);
  });

  it('starts with null conversationId', () => {
    const el = new BiChatPage();
    expect(el['_conversationId']).toBeNull();
  });

  it('_appendToLast appends content to last assistant message', () => {
    const el = new BiChatPage();
    el['_messages'] = [
      { id: '1', role: 'user', content: 'hello', createdAt: '' },
      { id: '2', role: 'assistant', content: 'Hi', createdAt: '' },
    ];
    el['_appendToLast'](' there');
    expect(el['_messages'].at(-1)?.content).toBe('Hi there');
  });

  it('_setSpecOnLast sets spec on last assistant message', () => {
    const el = new BiChatPage();
    const spec = { component: 'BarChart', props: {} };
    el['_messages'] = [{ id: '1', role: 'assistant', content: '', createdAt: '' }];
    el['_setSpecOnLast'](spec);
    expect(el['_messages'].at(-1)?.spec).toEqual(spec);
  });
});
