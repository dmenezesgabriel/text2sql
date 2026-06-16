import './metric';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Metrics/Metric',
  component: 'bi-metric',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`
    <bi-metric
      label="Total Revenue"
      value="$1.2M"
      change="+12% vs last month"
      direction="up"
    ></bi-metric>
  `,
};
