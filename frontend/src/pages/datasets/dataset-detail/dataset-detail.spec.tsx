import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { DatasetDetail } from './dataset-detail';

describe('DatasetDetail', () => {
  it('renders dataset detail with id', () => {
    render(
      <MemoryRouter initialEntries={['/datasets/1']}>
        <Routes>
          <Route path="/datasets/:id" element={<DatasetDetail />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText(/Dataset 1/)).toBeInTheDocument();
  });
});
