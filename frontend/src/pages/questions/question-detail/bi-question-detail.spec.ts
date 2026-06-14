import { describe, expect, it } from 'vitest';

import { BiQuestionDetail } from './bi-question-detail';

describe('BiQuestionDetail', () => {
  it('is a defined custom element class', () => {
    expect(BiQuestionDetail).toBeDefined();
  });

  it('has default questionId of empty string', () => {
    const el = new BiQuestionDetail();
    expect(el.questionId).toBe('');
  });

  it('starts with null question', () => {
    const el = new BiQuestionDetail();
    expect(el['_question']).toBeNull();
  });

  it('starts with isLoading false', () => {
    const el = new BiQuestionDetail();
    expect(el['_isLoading']).toBe(false);
  });

  it('starts with empty drillColumn and drillValue', () => {
    const el = new BiQuestionDetail();
    expect(el['_drillColumn']).toBe('');
    expect(el['_drillValue']).toBe('');
  });

  it('starts with isDrilling false', () => {
    const el = new BiQuestionDetail();
    expect(el['_isDrilling']).toBe(false);
  });

  it('skips _handleDelete when no questionId', async () => {
    const el = new BiQuestionDetail();
    let navigated = false;
    el.addEventListener('navigate', () => {
      navigated = true;
    });
    await el['_handleDelete']();
    expect(navigated).toBe(false);
  });
});
