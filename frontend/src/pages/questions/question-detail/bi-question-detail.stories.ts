import './bi-question-detail';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';
import { http, HttpResponse } from 'msw';

const meta: Meta = {
  title: 'Pages/QuestionDetail',
  component: 'bi-question-detail',
  tags: ['autodocs'],
};
export default meta;

const mockQuestion = {
  id: 'q-1',
  title: 'Monthly Revenue',
  sql: 'SELECT month, SUM(revenue) AS revenue FROM sales GROUP BY month ORDER BY month',
  datasetId: 'ds-1',
  vizComponent: 'BarChart',
  vizFormat: 'CHART',
  vizProps: {
    title: 'Monthly Revenue',
    xAxis: 'Month',
    yAxis: 'Revenue',
    data: [
      { label: 'Jan', value: 42_000 },
      { label: 'Feb', value: 38_000 },
      { label: 'Mar', value: 55_000 },
    ],
  },
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

export const Default: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/questions/q-1', () => HttpResponse.json(mockQuestion)),
        http.delete('/api/v1/questions/q-1', () => new HttpResponse(null, { status: 204 })),
        http.post('/api/v1/questions/q-1/drill', () =>
          HttpResponse.json({ ...mockQuestion, id: 'q-2', title: 'Drilled' }),
        ),
      ],
    },
  },
  render: () => html`<bi-question-detail question-id="q-1"></bi-question-detail>`,
};
