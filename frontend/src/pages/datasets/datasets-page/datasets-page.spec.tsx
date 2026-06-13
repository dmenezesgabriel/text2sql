import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { DatasetsPage } from './datasets-page';

describe('DatasetsPage', () => {
  it('renders title', () => {
    render(<DatasetsPage />);
    expect(screen.getByText('Datasets')).toBeInTheDocument();
  });
});
