import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';

import { ChatInput } from './chat-input';

const meta = {
  title: 'ChatInput',
  component: ChatInput,
  tags: ['autodocs'],
  args: { onSend: fn(), disabled: false },
} satisfies Meta<typeof ChatInput>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Disabled: Story = {
  args: { disabled: true },
};
