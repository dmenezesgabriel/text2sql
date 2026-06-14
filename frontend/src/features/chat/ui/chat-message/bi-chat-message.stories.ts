import './bi-chat-message';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Chat/ChatMessage',
  component: 'bi-chat-message',
  tags: ['autodocs'],
};
export default meta;

const userMsg = {
  id: 'u-1',
  role: 'user' as const,
  content: 'Show me monthly sales',
  createdAt: new Date().toISOString(),
};

const assistantThinking = {
  id: 'a-1',
  role: 'assistant' as const,
  content: 'Let me check the data for you…',
  createdAt: new Date().toISOString(),
};

const assistantWithChart = {
  id: 'a-2',
  role: 'assistant' as const,
  content: 'Here is the monthly breakdown:',
  spec: {
    component: 'BarChart',
    title: 'Monthly Sales',
    sql: 'SELECT month, revenue FROM sales',
    dataset_id: 'ds-1',
    format: 'chart',
    props: {
      title: 'Monthly Sales',
      xAxis: 'Month',
      yAxis: 'Revenue',
      data: [
        { label: 'Jan', value: 42_000 },
        { label: 'Feb', value: 38_000 },
        { label: 'Mar', value: 55_000 },
      ],
    },
  },
  createdAt: new Date().toISOString(),
};

export const UserMessage: StoryObj = {
  render: () => html`<bi-chat-message .message=${userMsg}></bi-chat-message>`,
};

export const AssistantThinking: StoryObj = {
  render: () => html`<bi-chat-message .message=${assistantThinking}></bi-chat-message>`,
};

export const AssistantWithChart: StoryObj = {
  render: () => html`<bi-chat-message .message=${assistantWithChart}></bi-chat-message>`,
};
