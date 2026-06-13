import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { QuestionsPage } from './questions-page';

describe('QuestionsPage', () => {
  it('renders title', () => {
    render(<QuestionsPage />);
    expect(screen.getByText('Questions')).toBeInTheDocument();
  });
});
