import './bi-layout';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Layout',
  component: 'bi-layout',
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
};
export default meta;

export const Default: StoryObj = {
  render: () => html`
    <bi-layout>
      <p>Page content goes here</p>
    </bi-layout>
  `,
};

export const WithHeaderActions: StoryObj = {
  render: () => html`
    <bi-layout>
      <button slot="header-actions">Settings</button>
      <p>Page content goes here</p>
    </bi-layout>
  `,
};
