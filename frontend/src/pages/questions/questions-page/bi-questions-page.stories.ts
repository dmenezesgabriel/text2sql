import './bi-questions-page';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';
import { http, HttpResponse } from 'msw';

const meta: Meta = {
  title: 'Pages/QuestionsPage',
  component: 'bi-questions-page',
  tags: ['autodocs'],
};
export default meta;

const mockQuestions = [
  {
    id: 'q-1',
    title: 'Monthly Revenue',
    sql: 'SELECT month, SUM(revenue) FROM sales GROUP BY month',
    datasetId: 'ds-1',
    vizComponent: 'BarChart',
    vizFormat: 'CHART',
    vizProps: { title: 'Monthly Revenue', xAxis: 'Month', yAxis: 'Revenue', data: [] },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'q-2',
    title: 'Top Products',
    sql: 'SELECT product, COUNT(*) FROM orders GROUP BY product LIMIT 10',
    datasetId: 'ds-1',
    vizComponent: 'DataTable',
    vizFormat: 'TABLE',
    vizProps: { title: 'Top Products', columns: [], rows: [] },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export const WithQuestions: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/questions', () => HttpResponse.json({ questions: mockQuestions })),
        http.delete('/api/v1/questions/:id', () => new HttpResponse(null, { status: 204 })),
      ],
    },
  },
  render: () => html`<bi-questions-page></bi-questions-page>`,
};

export const Empty: StoryObj = {
  parameters: {
    msw: {
      handlers: [http.get('/api/v1/questions', () => HttpResponse.json({ questions: [] }))],
    },
  },
  render: () => html`<bi-questions-page></bi-questions-page>`,
};
