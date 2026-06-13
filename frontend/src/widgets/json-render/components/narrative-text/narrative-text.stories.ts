import type { Meta, StoryObj } from '@storybook/web-components';

import { NarrativeTextElement } from './narrative-text';

const meta = {
  title: 'Text/NarrativeText',
  component: NarrativeTextElement,
  tags: ['autodocs'],
  args: {
    content: 'Your sales have increased by 15% this quarter, driven primarily by the APAC region.',
    tone: 'analytical',
  },
} satisfies Meta<NarrativeTextElement>;

export default meta;
type Story = StoryObj<NarrativeTextElement>;

export const Default: Story = {};
