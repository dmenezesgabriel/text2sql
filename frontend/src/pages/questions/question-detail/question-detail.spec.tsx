import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { QuestionDetail } from './question-detail';

describe('QuestionDetail', () => {
  it('renders question detail with id', () => {
    render(
      <MemoryRouter initialEntries={['/questions/1']}>
        <Routes>
          <Route path="/questions/:id" element={<QuestionDetail />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText(/Question 1/)).toBeInTheDocument();
  });
});
