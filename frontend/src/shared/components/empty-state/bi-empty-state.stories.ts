import './bi-empty-state';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Shared/BiEmptyState',
  tags: ['autodocs'],
};
export default meta;

export const TitleOnly: StoryObj = {
  render: () => html`<bi-empty-state heading="No questions yet"></bi-empty-state>`,
};

export const WithDescription: StoryObj = {
  render: () => html`
    <bi-empty-state
      heading="No questions yet"
      description="Ask a question in the chat to get started."
    ></bi-empty-state>
  `,
};

export const WithAction: StoryObj = {
  render: () => html`
    <bi-empty-state heading="No dashboards yet" description="Create a dashboard to begin.">
      <button slot="action">Create Dashboard</button>
    </bi-empty-state>
  `,
};
