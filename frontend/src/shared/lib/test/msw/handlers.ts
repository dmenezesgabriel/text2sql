import { http, HttpResponse } from 'msw';

import { getText2sqlMock } from '@/shared/api/generated/endpoints.msw';

export const handlers = [
  ...getText2sqlMock(),
  http.post('/api/v1/chat', async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(
          encoder.encode(
            'data: {"type":"ThinkingEvent","payload":"Hello! How can I help you?"}\n\n',
          ),
        );
        controller.enqueue(encoder.encode('data: [DONE]\n\n'));
        controller.close();
      },
    });

    return new HttpResponse(stream, {
      headers: { 'Content-Type': 'text/event-stream' },
    });
  }),
];
