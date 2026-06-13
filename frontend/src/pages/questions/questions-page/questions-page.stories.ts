import type { Meta, StoryObj } from '@storybook/react';

import { QuestionsPage } from './questions-page';

const meta = {
  title: 'Pages/QuestionsPage',
  component: QuestionsPage,
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof QuestionsPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
