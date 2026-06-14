import './bi-dashboards-page';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';
import { http, HttpResponse } from 'msw';

const meta: Meta = {
  title: 'Pages/DashboardsPage',
  component: 'bi-dashboards-page',
  tags: ['autodocs'],
};
export default meta;

const mockDashboards = [
  {
    id: 'db-1',
    title: 'Executive Overview',
    tiles: [],
    filters: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'db-2',
    title: 'Sales Performance',
    tiles: [],
    filters: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export const WithDashboards: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/dashboards', () => HttpResponse.json({ dashboards: mockDashboards })),
        http.post('/api/v1/dashboards', () =>
          HttpResponse.json({
            id: 'db-new',
            title: 'New Dashboard',
            tiles: [],
            filters: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }),
        ),
        http.delete('/api/v1/dashboards/:id', () => new HttpResponse(null, { status: 204 })),
      ],
    },
  },
  render: () => html`<bi-dashboards-page></bi-dashboards-page>`,
};

export const Empty: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/dashboards', () => HttpResponse.json({ dashboards: [] })),
        http.post('/api/v1/dashboards', () =>
          HttpResponse.json({
            id: 'db-1',
            title: 'New',
            tiles: [],
            filters: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }),
        ),
      ],
    },
  },
  render: () => html`<bi-dashboards-page></bi-dashboards-page>`,
};
