import './bi-datasets-page';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';
import { http, HttpResponse } from 'msw';

const meta: Meta = {
  title: 'Pages/DatasetsPage',
  component: 'bi-datasets-page',
  tags: ['autodocs'],
};
export default meta;

const mockDatasets = [
  {
    id: 'ds-1',
    name: 'sales',
    kind: 'file',
    location: 's3://bucket/sales.parquet',
    columns: [
      { name: 'month', dtype: 'VARCHAR', nullable: false },
      { name: 'revenue', dtype: 'DOUBLE', nullable: true },
    ],
    createdAt: new Date().toISOString(),
  },
  {
    id: 'ds-2',
    name: 'customers',
    kind: 'file',
    location: 's3://bucket/customers.parquet',
    columns: [
      { name: 'id', dtype: 'VARCHAR', nullable: false },
      { name: 'name', dtype: 'VARCHAR', nullable: false },
    ],
    createdAt: new Date().toISOString(),
  },
];

export const WithDatasets: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/datasets', () => HttpResponse.json({ datasets: mockDatasets })),
        http.post('/api/v1/datasets/register-s3', () =>
          HttpResponse.json({
            id: 'ds-3',
            name: 'new',
            kind: 'file',
            location: 's3://b/new.parquet',
            columns: [],
          }),
        ),
        http.delete('/api/v1/datasets/:id', () => new HttpResponse(null, { status: 204 })),
      ],
    },
  },
  render: () => html`<bi-datasets-page></bi-datasets-page>`,
};

export const Empty: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/datasets', () => HttpResponse.json({ datasets: [] })),
        http.post('/api/v1/datasets/register-s3', () =>
          HttpResponse.json({
            id: 'ds-1',
            name: 'sales',
            kind: 'file',
            location: 's3://b/s.parquet',
            columns: [],
          }),
        ),
      ],
    },
  },
  render: () => html`<bi-datasets-page></bi-datasets-page>`,
};
