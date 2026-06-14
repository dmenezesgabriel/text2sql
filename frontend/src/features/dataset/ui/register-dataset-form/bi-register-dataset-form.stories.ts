import './bi-register-dataset-form';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';
import { http, HttpResponse } from 'msw';

const meta: Meta = {
  title: 'Dataset/RegisterDatasetForm',
  component: 'bi-register-dataset-form',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.post('/api/v1/datasets/register-s3', () =>
          HttpResponse.json({
            id: 'ds-new',
            name: 'sales',
            kind: 'file',
            location: 's3://bucket/sales.parquet',
            columns: [],
          }),
        ),
      ],
    },
  },
  render: () => html`<bi-register-dataset-form></bi-register-dataset-form>`,
};
