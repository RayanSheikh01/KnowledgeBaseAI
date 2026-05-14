import type { ChatStreamEvent } from './types';

export async function* parseChatStream(
  response: Response,
): AsyncGenerator<ChatStreamEvent> {
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('Response has no body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sep = buffer.indexOf('\n\n');
    while (sep !== -1) {
      const frame = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      sep = buffer.indexOf('\n\n');

      let eventName: string | null = null;
      const dataLines: string[] = [];
      for (const line of frame.split('\n')) {
        if (line.startsWith('event:')) {
          eventName = line.slice(6).trim();
        } else if (line.startsWith('data:')) {
          dataLines.push(line.slice(5).replace(/^ /, ''));
        }
      }
      if (!eventName || dataLines.length === 0) continue;

      let payload: Record<string, unknown>;
      try {
        payload = JSON.parse(dataLines.join('\n'));
      } catch {
        continue;
      }

      yield { type: eventName, ...payload } as unknown as ChatStreamEvent;
    }
  }
}
