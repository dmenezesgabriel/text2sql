import './bi-card';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Card',
  component: 'bi-card',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`<bi-card>Card content goes here</bi-card>`,
};

export const WithTitle: StoryObj = {
  render: () => html`<bi-card heading="Section Title">Content with a title</bi-card>`,
};
