import './bi-input';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Shared/BiInput',
  tags: ['autodocs'],
};
export default meta;

export const Default: StoryObj = {
  render: () => html`<bi-input placeholder="Type something…"></bi-input>`,
};

export const WithLabel: StoryObj = {
  render: () => html`<bi-input label="Dataset name" placeholder="e.g. sales_q3"></bi-input>`,
};

export const WithError: StoryObj = {
  render: () => html`
    <bi-input label="S3 URI" value="not-a-uri" error="Must start with s3://"></bi-input>
  `,
};

export const WithHint: StoryObj = {
  render: () => html`
    <bi-input label="Column" hint="Column names are case-sensitive" placeholder="region"></bi-input>
  `,
};

export const Disabled: StoryObj = {
  render: () => html`<bi-input label="Name" value="sales_2024" disabled></bi-input>`,
};
