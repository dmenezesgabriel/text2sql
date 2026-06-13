import type { Meta, StoryObj } from '@storybook/react';

import { Card } from './card';

const meta = {
  title: 'Card',
  component: Card,
  tags: ['autodocs'],
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { children: 'Card content goes here' },
};

export const WithTitle: Story = {
  args: { title: 'Section Title', children: 'Content with a title' },
};
