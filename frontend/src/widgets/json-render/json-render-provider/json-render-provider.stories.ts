import type { Meta, StoryObj } from '@storybook/react';

import { JsonRenderProvider } from './json-render-provider';

const meta = {
  title: 'JsonRenderProvider',
  component: JsonRenderProvider,
  tags: ['autodocs'],
} satisfies Meta<typeof JsonRenderProvider>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { children: 'Wrapped content' },
};
