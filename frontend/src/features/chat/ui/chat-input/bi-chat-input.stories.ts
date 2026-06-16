import './bi-chat-input';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'ChatInput',
  component: 'bi-chat-input',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`<bi-chat-input></bi-chat-input>`,
};

export const Disabled: StoryObj = {
  render: () => html`<bi-chat-input disabled></bi-chat-input>`,
};
