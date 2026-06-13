import { create } from 'zustand';

import type { Dataset } from '@/entities/dataset/types';

import { listDatasets, registerS3Dataset } from '../api/dataset-api';

interface DatasetState {
  datasets: Dataset[];
  isLoading: boolean;
  error: string | null;
  fetchDatasets: () => Promise<void>;
  registerDataset: (name: string, s3Uri: string) => Promise<void>;
}

export const useDatasetStore = create<DatasetState>((set) => ({
  datasets: [],
  isLoading: false,
  error: null,

  fetchDatasets: async () => {
    set({ isLoading: true, error: null });
    try {
      const datasets = await listDatasets();
      set({ datasets, isLoading: false });
    } catch (error) {
      set({ error: String(error), isLoading: false });
    }
  },

  registerDataset: async (name, s3Uri) => {
    set({ isLoading: true, error: null });
    try {
      await registerS3Dataset({ name, s3_uri: s3Uri });
      const datasets = await listDatasets();
      set({ datasets, isLoading: false });
    } catch (error) {
      set({ error: String(error), isLoading: false });
    }
  },
}));
