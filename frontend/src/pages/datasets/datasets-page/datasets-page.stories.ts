import type { Meta, StoryObj } from '@storybook/react';

import { DatasetsPage } from './datasets-page';

const meta = {
  title: 'Pages/DatasetsPage',
  component: DatasetsPage,
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof DatasetsPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
