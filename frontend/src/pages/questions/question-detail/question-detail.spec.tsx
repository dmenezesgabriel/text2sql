import { render } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { QuestionDetail } from './question-detail';

/**
 *
 * @param id
 */
function renderPage(id = '1') {
  return render(
    <MemoryRouter initialEntries={[`/questions/${id}`]}>
      <Routes>
        <Route path="/questions/:id" element={<QuestionDetail />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('QuestionDetail', () => {
  it('renders the page heading element before data loads', () => {
    const { container } = renderPage();
    const header = container.querySelector('bi-page-header');
    expect(header).toBeTruthy();
    // Before fetch resolves, shows fallback heading
    expect(header?.getAttribute('heading')).toBe('Question');
  });

  it('renders without crashing', () => {
    expect(() => renderPage()).not.toThrow();
  });
});
