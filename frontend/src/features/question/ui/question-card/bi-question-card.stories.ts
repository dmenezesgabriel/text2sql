import './bi-question-card';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';

const meta: Meta = {
  title: 'Features/Question/BiQuestionCard',
  tags: ['autodocs'],
};
export default meta;

const mockId = '11111111-0000-0000-0000-000000000001';
const mockDate = '2026-06-13T10:00:00Z';

export const Default: StoryObj = {
  render: () => html`
    <div style="max-width:380px">
      <bi-question-card
        question-id=${mockId}
        title="Monthly Revenue by Region"
        viz-format="CHART"
        sql="SELECT region, SUM(revenue) FROM sales GROUP BY region"
        created-at=${mockDate}
        show-delete
      ></bi-question-card>
    </div>
  `,
};

export const WithoutDelete: StoryObj = {
  render: () => html`
    <div style="max-width:380px">
      <bi-question-card
        question-id=${mockId}
        title="Top 10 Products"
        viz-format="TABLE"
        sql="SELECT product_name, sales FROM products ORDER BY sales DESC LIMIT 10"
        created-at=${mockDate}
      ></bi-question-card>
    </div>
  `,
};

export const TextFormat: StoryObj = {
  render: () => html`
    <div style="max-width:380px">
      <bi-question-card
        question-id=${mockId}
        title="Sales Summary Narrative"
        viz-format="TEXT"
        sql="SELECT COUNT(*) as total_orders FROM orders WHERE date &gt;= '2026-01-01'"
        created-at=${mockDate}
        show-delete
      ></bi-question-card>
    </div>
  `,
};
