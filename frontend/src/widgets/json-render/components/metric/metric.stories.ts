import type { Meta, StoryObj } from '@storybook/web-components';

import { MetricElement } from './metric';

const meta = {
  title: 'Metrics/Metric',
  component: MetricElement,
  tags: ['autodocs'],
  args: {
    label: 'Total Revenue',
    value: '$1.2M',
    change: '+12% vs last month',
    direction: 'up',
  },
} satisfies Meta<MetricElement>;

export default meta;
type Story = StoryObj<MetricElement>;

export const Default: Story = {};
