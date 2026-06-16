import './narrative-text';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Text/NarrativeText',
  component: 'bi-narrative-text',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`
    <bi-narrative-text
      content="Your sales have increased by 15% this quarter, driven primarily by the APAC region."
      tone="analytical"
    ></bi-narrative-text>
  `,
};
