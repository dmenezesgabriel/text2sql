import type { Meta, StoryObj } from '@storybook/react';

import { Providers } from './providers';

const meta = {
  title: 'Providers',
  component: Providers,
  tags: ['autodocs'],
} satisfies Meta<typeof Providers>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { children: 'App content wrapped in providers' },
};
