import './bi-spinner';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Spinner',
  component: 'bi-spinner',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`<bi-spinner></bi-spinner>`,
};

export const Small: StoryObj = {
  render: () => html`<bi-spinner size="sm"></bi-spinner>`,
};

export const Large: StoryObj = {
  render: () => html`<bi-spinner size="lg"></bi-spinner>`,
};
