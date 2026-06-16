import './bi-header';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Header',
  component: 'bi-header',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`<bi-header></bi-header>`,
};

export const WithActions: StoryObj = {
  render: () => html`
    <bi-header>
      <button slot="actions">Settings</button>
    </bi-header>
  `,
};
