import './bi-dashboard-detail';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';
import { http, HttpResponse } from 'msw';

const meta: Meta = {
  title: 'Pages/DashboardDetail',
  component: 'bi-dashboard-detail',
  tags: ['autodocs'],
};
export default meta;

const mockQuestion = {
  id: 'q-1',
  title: 'Monthly Revenue',
  sql: 'SELECT month, SUM(revenue) FROM sales GROUP BY month',
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

const mockDashboard = {
  id: 'db-1',
  title: 'Executive Overview',
  tiles: [
    {
      id: 't-1',
      questionId: 'q-1',
      position: { row: 1, col: 1, width: 6, height: 2 },
    },
  ],
  filters: [],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

export const WithTile: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/dashboards/db-1', () => HttpResponse.json(mockDashboard)),
        http.get('/api/v1/questions/q-1', () => HttpResponse.json(mockQuestion)),
      ],
    },
  },
  render: () => html`<bi-dashboard-detail dashboard-id="db-1"></bi-dashboard-detail>`,
};

export const EmptyDashboard: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/dashboards/db-2', () =>
          HttpResponse.json({
            id: 'db-2',
            title: 'Empty Board',
            tiles: [],
            filters: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }),
        ),
      ],
    },
  },
  render: () => html`<bi-dashboard-detail dashboard-id="db-2"></bi-dashboard-detail>`,
};
