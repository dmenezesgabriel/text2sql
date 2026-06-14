import { render } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { DatasetDetail } from './dataset-detail';

/**
 *
 * @param id
 */
function renderPage(id = '1') {
  return render(
    <MemoryRouter initialEntries={[`/datasets/${id}`]}>
      <Routes>
        <Route path="/datasets/:id" element={<DatasetDetail />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('DatasetDetail', () => {
  it('renders the page heading element before data loads', () => {
    const { container } = renderPage();
    const header = container.querySelector('bi-page-header');
    expect(header).toBeTruthy();
    expect(header?.getAttribute('heading')).toBe('Dataset');
  });

  it('renders without crashing', () => {
    expect(() => renderPage()).not.toThrow();
  });
});
