import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useDatasetStore } from '../../model/store';
import { RegisterDatasetForm } from './register-dataset-form';

vi.mock('../../model/store');

const mockRegister = vi.fn<(name: string, s3Uri: string) => Promise<void>>();

beforeEach(() => {
  vi.mocked(useDatasetStore).mockReturnValue({
    datasets: [],
    isLoading: false,
    error: null,
    registerDataset: mockRegister,
    fetchDatasets: vi.fn(),
  });
});

describe('RegisterDatasetForm', () => {
  it('renders name and S3 URI inputs', () => {
    render(<RegisterDatasetForm />);
    expect(screen.getByPlaceholderText(/dataset name/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/s3/i)).toBeInTheDocument();
  });

  it('submit button is disabled when fields are empty', () => {
    render(<RegisterDatasetForm />);
    expect(screen.getByRole('button', { name: /register dataset/i })).toBeDisabled();
  });

  it('submit button is disabled when only name is filled', async () => {
    render(<RegisterDatasetForm />);
    await userEvent.type(screen.getByPlaceholderText(/dataset name/i), 'my-dataset');
    expect(screen.getByRole('button', { name: /register dataset/i })).toBeDisabled();
  });

  it('calls registerDataset with trimmed values on submit', async () => {
    mockRegister.mockResolvedValue();
    render(<RegisterDatasetForm />);
    await userEvent.type(screen.getByPlaceholderText(/dataset name/i), '  sales  ');
    await userEvent.type(screen.getByPlaceholderText(/s3/i), 's3://bucket/data.parquet');
    await userEvent.click(screen.getByRole('button', { name: /register dataset/i }));
    expect(mockRegister).toHaveBeenCalledWith('sales', 's3://bucket/data.parquet');
  });

  it('clears inputs after successful submit', async () => {
    mockRegister.mockResolvedValue();
    render(<RegisterDatasetForm />);
    const nameInput = screen.getByPlaceholderText(/dataset name/i);
    await userEvent.type(nameInput, 'sales');
    await userEvent.type(screen.getByPlaceholderText(/s3/i), 's3://b/f.parquet');
    await userEvent.click(screen.getByRole('button', { name: /register dataset/i }));
    expect(nameInput).toHaveValue('');
  });

  it('shows error from store', () => {
    vi.mocked(useDatasetStore).mockReturnValue({
      datasets: [],
      isLoading: false,
      error: 'Dataset name already exists',
      registerDataset: mockRegister,
      fetchDatasets: vi.fn(),
    });
    render(<RegisterDatasetForm />);
    expect(screen.getByText(/dataset name already exists/i)).toBeInTheDocument();
  });

  it('disables form while loading', () => {
    vi.mocked(useDatasetStore).mockReturnValue({
      datasets: [],
      isLoading: true,
      error: null,
      registerDataset: mockRegister,
      fetchDatasets: vi.fn(),
    });
    render(<RegisterDatasetForm />);
    expect(screen.getByPlaceholderText(/dataset name/i)).toBeDisabled();
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
