import { describe, expect, it } from 'vitest';

import { BiQuestionsPage } from './bi-questions-page';

describe('BiQuestionsPage', () => {
  it('is a defined custom element class', () => {
    expect(BiQuestionsPage).toBeDefined();
  });

  it('starts with empty questions', () => {
    const el = new BiQuestionsPage();
    expect(el['_questions']).toEqual([]);
  });

  it('starts with isLoading false', () => {
    const el = new BiQuestionsPage();
    expect(el['_isLoading']).toBe(false);
  });

  it('starts with empty error', () => {
    const el = new BiQuestionsPage();
    expect(el['_error']).toBe('');
  });
});
