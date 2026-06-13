import type { Meta, StoryObj } from '@storybook/web-components';

import { DataTableElement } from './data-table';

const meta = {
  title: 'Tables/DataTable',
  component: DataTableElement,
  tags: ['autodocs'],
  args: {
    title: 'Sales Data',
    columns: [
      { key: 'name', header: 'Name' },
      { key: 'value', header: 'Value' },
    ],
    rows: [
      { name: 'Product A', value: 100 },
      { name: 'Product B', value: 200 },
    ],
  },
} satisfies Meta<DataTableElement>;

export default meta;
type Story = StoryObj<DataTableElement>;

export const Default: Story = {};
