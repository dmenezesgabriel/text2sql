import type { Meta, StoryObj } from '@storybook/web-components';

import { BarChartElement } from './bar-chart';

const meta = {
  title: 'Charts/BarChart',
  component: BarChartElement,
  tags: ['autodocs'],
  args: {
    title: 'Sales by Month',
    xAxis: 'Month',
    yAxis: 'Revenue',
    data: [
      { label: 'Jan', value: 100 },
      { label: 'Feb', value: 200 },
      { label: 'Mar', value: 150 },
    ],
  },
} satisfies Meta<BarChartElement>;

export default meta;
type Story = StoryObj<BarChartElement>;

export const Default: Story = {};
