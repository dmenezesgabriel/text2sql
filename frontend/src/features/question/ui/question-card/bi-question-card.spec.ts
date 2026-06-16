import { describe, expect, it } from 'vitest';

import { BiQuestionCard } from './bi-question-card';

describe('BiQuestionCard', () => {
  it('is a defined custom element class', () => {
    expect(BiQuestionCard).toBeDefined();
  });

  it('stores questionId property', () => {
    const el = new BiQuestionCard();
    el.questionId = 'abc-123';
    expect(el.questionId).toBe('abc-123');
  });

  it('stores title property', () => {
    const el = new BiQuestionCard();
    el.title = 'Monthly Revenue';
    expect(el.title).toBe('Monthly Revenue');
  });

  it('showDelete defaults to false', () => {
    const el = new BiQuestionCard();
    expect(el.showDelete).toBe(false);
  });

  it('dispatches bi-question-delete event on delete', () => {
    const el = new BiQuestionCard();
    el.questionId = 'q-1';
    let receivedDetail: unknown = null;
    el.addEventListener('bi-question-delete', (e) => {
      receivedDetail = (e as CustomEvent).detail;
    });
    el['_onDelete']();
    expect(receivedDetail).toBe('q-1');
  });
});
