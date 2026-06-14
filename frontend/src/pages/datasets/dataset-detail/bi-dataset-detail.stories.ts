import './bi-dataset-detail';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';
import { http, HttpResponse } from 'msw';

const meta: Meta = {
  title: 'Pages/DatasetDetail',
  component: 'bi-dataset-detail',
  tags: ['autodocs'],
};
export default meta;

const mockDataset = {
  id: 'ds-1',
  name: 'sales',
  kind: 'file',
  location: 's3://bucket/sales.parquet',
  columns: [
    { name: 'month', dtype: 'VARCHAR', nullable: false },
    { name: 'revenue', dtype: 'DOUBLE', nullable: true },
    { name: 'region', dtype: 'VARCHAR', nullable: true },
  ],
  createdAt: new Date().toISOString(),
};

const mockPreview = {
  columns: ['month', 'revenue', 'region'],
  rows: [
    { month: 'Jan', revenue: 42_000, region: 'North' },
    { month: 'Feb', revenue: 38_000, region: 'South' },
    { month: 'Mar', revenue: 55_000, region: 'East' },
  ],
};

export const Default: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/datasets', () => HttpResponse.json({ datasets: [mockDataset] })),
        http.get('/api/v1/datasets/ds-1/preview', () => HttpResponse.json(mockPreview)),
      ],
    },
  },
  render: () => html`<bi-dataset-detail dataset-id="ds-1"></bi-dataset-detail>`,
};
