import './bi-button';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Shared/BiButton',
  tags: ['autodocs'],
};
export default meta;

export const Primary: StoryObj = {
  render: () => html`<bi-button variant="primary">Save</bi-button>`,
};

export const Secondary: StoryObj = {
  render: () => html`<bi-button variant="secondary">Cancel</bi-button>`,
};

export const Ghost: StoryObj = {
  render: () => html`<bi-button variant="ghost">Dismiss</bi-button>`,
};

export const Danger: StoryObj = {
  render: () => html`<bi-button variant="danger">Delete</bi-button>`,
};

export const Small: StoryObj = {
  render: () => html`<bi-button variant="primary" size="sm">Save as Question</bi-button>`,
};

export const Disabled: StoryObj = {
  render: () => html`<bi-button variant="primary" disabled>Saving…</bi-button>`,
};

export const AllVariants: StoryObj = {
  render: () => html`
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <bi-button variant="primary">Primary</bi-button>
      <bi-button variant="secondary">Secondary</bi-button>
      <bi-button variant="ghost">Ghost</bi-button>
      <bi-button variant="danger">Danger</bi-button>
    </div>
  `,
};
