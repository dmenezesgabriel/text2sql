import type { Meta, StoryObj } from '@storybook/react';

import { ChatMessage } from './chat-message';

const meta = {
  title: 'ChatMessage',
  component: ChatMessage,
  tags: ['autodocs'],
} satisfies Meta<typeof ChatMessage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const User: Story = {
  args: { message: { id: '1', role: 'user', content: 'What are my top sales?', createdAt: '' } },
};

export const Assistant: Story = {
  args: {
    message: {
      id: '2',
      role: 'assistant',
      content: 'Your top sales this quarter are $1.2M.',
      createdAt: '',
    },
  },
};
