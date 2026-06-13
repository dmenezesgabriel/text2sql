export function chatStream(
  body: { message: string; conversation_id?: string },
  onEvent: (event: MessageEvent) => void,
  onError: (error: Error) => void,
  onClose: () => void,
): void {
  fetch('/api/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
    .then(async (response) => {
      if (!response.ok) {
        onError(new Error(`Chat stream failed: ${response.statusText}`));
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        onError(new Error('No response body'));
        return;
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onEvent(new MessageEvent('message', { data: JSON.stringify(data) }));
            } catch {
              onEvent(new MessageEvent('message', { data: line.slice(6) }));
            }
          }
        }
      }

      onClose();
    })
    .catch(onError);
}
