import './bi-sidebar';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Sidebar',
  component: 'bi-sidebar',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`<bi-sidebar style="height:400px"></bi-sidebar>`,
};

export const WithActiveLink: StoryObj = {
  render: () => html`<bi-sidebar active-href="/questions" style="height:400px"></bi-sidebar>`,
};
