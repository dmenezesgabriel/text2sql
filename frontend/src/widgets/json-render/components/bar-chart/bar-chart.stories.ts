import './bar-chart';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Charts/BarChart',
  component: 'bi-bar-chart',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`
    <bi-bar-chart
      title="Sales by Month"
      .xAxis=${'Month'}
      .yAxis=${'Revenue'}
      .data=${[
        { label: 'Jan', value: 100 },
        { label: 'Feb', value: 200 },
        { label: 'Mar', value: 150 },
      ]}
    ></bi-bar-chart>
  `,
};
