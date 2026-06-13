import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import { DashboardDetail } from './dashboard-detail';

const meta = {
  title: 'Pages/DashboardDetail',
  component: DashboardDetail,
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={['/dashboards/1']}>
        <Routes>
          <Route path="/dashboards/:id" element={<Story />} />
        </Routes>
      </MemoryRouter>
    ),
  ],
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof DashboardDetail>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
