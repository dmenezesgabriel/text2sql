import type { Meta, StoryObj } from '@storybook/react';

import { DashboardsPage } from './dashboards-page';

const meta = {
  title: 'Pages/DashboardsPage',
  component: DashboardsPage,
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof DashboardsPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
