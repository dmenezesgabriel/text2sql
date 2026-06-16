import './data-table';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Tables/DataTable',
  component: 'bi-data-table',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`
    <bi-data-table
      title="Sales Data"
      .columns=${[
        { key: 'name', header: 'Name' },
        { key: 'value', header: 'Value' },
      ]}
      .rows=${[
        { name: 'Product A', value: 100 },
        { name: 'Product B', value: 200 },
      ]}
    ></bi-data-table>
  `,
};
