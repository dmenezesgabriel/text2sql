import './bi-page-header';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Shared/BiPageHeader',
  tags: ['autodocs'],
};
export default meta;

export const TitleOnly: StoryObj = {
  render: () => html`<bi-page-header heading="Questions"></bi-page-header>`,
};

export const WithDescription: StoryObj = {
  render: () => html`
    <bi-page-header
      heading="Questions"
      description="Saved analytical queries and their visualizations"
    ></bi-page-header>
  `,
};

export const WithActions: StoryObj = {
  render: () => html`
    <bi-page-header heading="Dashboards" description="Compose questions into dashboards">
      <button slot="actions">+ New Dashboard</button>
    </bi-page-header>
  `,
};

export const Full: StoryObj = {
  render: () => html`
    <bi-page-header heading="Question Detail" description="Drill down or export">
      <a slot="breadcrumb" href="#">← Questions</a>
      <button slot="actions">Delete</button>
    </bi-page-header>
  `,
};
