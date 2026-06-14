import './bi-chat-page';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html } from 'lit';
import { http, HttpResponse } from 'msw';

const meta: Meta = {
  title: 'Pages/ChatPage',
  component: 'bi-chat-page',
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
};
export default meta;

const encoder = new TextEncoder();

/**
 *
 * @param {...any} lines
 */
function makeStream(...lines: string[]) {
  return new ReadableStream({
    start(controller) {
      for (const line of lines) {
        controller.enqueue(encoder.encode(line));
      }
      controller.close();
    },
  });
}

export const Empty: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.post(
          '/api/v1/chat',
          () =>
            new HttpResponse(
              makeStream(
                'data: {"type":"ThinkingEvent","payload":"Let me check..."}\n\n',
                'data: [DONE]\n\n',
              ),
              { headers: { 'Content-Type': 'text/event-stream' } },
            ),
        ),
      ],
    },
  },
  render: () => html`<bi-chat-page style="height:100vh"></bi-chat-page>`,
};

export const WithChartResponse: StoryObj = {
  parameters: {
    msw: {
      handlers: [
        http.post(
          '/api/v1/chat',
          () =>
            new HttpResponse(
              makeStream(
                'data: {"type":"ThinkingEvent","payload":"Here is monthly sales:"}\n\n',
                `data: {"type":"SpecFragmentEvent","payload":{"component":"BarChart","title":"Monthly Sales","sql":"SELECT 1","dataset_id":"ds-1","format":"chart","props":{"title":"Monthly Sales","xAxis":"Month","yAxis":"Revenue","data":[{"label":"Jan","value":42000},{"label":"Feb","value":38000},{"label":"Mar","value":55000}]}}}\n\n`,
                'data: [DONE]\n\n',
              ),
              { headers: { 'Content-Type': 'text/event-stream' } },
            ),
        ),
      ],
    },
  },
  render: () => html`<bi-chat-page style="height:100vh"></bi-chat-page>`,
};
