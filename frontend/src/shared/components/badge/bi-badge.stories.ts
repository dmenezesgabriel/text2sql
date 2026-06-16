import './bi-badge';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Shared/BiBadge',
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'primary', 'success', 'warning', 'error', 'mono'],
    },
  },
};
export default meta;

export const Default: StoryObj = {
  render: () => html`<bi-badge variant="default">Default</bi-badge>`,
};

export const Primary: StoryObj = {
  render: () => html`<bi-badge variant="primary">CHART</bi-badge>`,
};

export const Success: StoryObj = {
  render: () => html`<bi-badge variant="success">Active</bi-badge>`,
};

export const Warning: StoryObj = {
  render: () => html`<bi-badge variant="warning">Warning</bi-badge>`,
};

export const ErrorVariant: StoryObj = {
  render: () => html`<bi-badge variant="error">Failed</bi-badge>`,
};

export const Mono: StoryObj = {
  render: () => html`<bi-badge variant="mono">VARCHAR</bi-badge>`,
};

export const AllVariants: StoryObj = {
  render: () => html`
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
      <bi-badge variant="default">default</bi-badge>
      <bi-badge variant="primary">CHART</bi-badge>
      <bi-badge variant="success">Active</bi-badge>
      <bi-badge variant="warning">Warning</bi-badge>
      <bi-badge variant="error">Failed</bi-badge>
      <bi-badge variant="mono">VARCHAR</bi-badge>
    </div>
  `,
};
