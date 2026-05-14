import { ChatStreamEvent } from '@/types';


export async function parseChatStream(response: Response): Promise<AsyncGenerator<ChatStreamEvent>> {
    const reader = response.body?.getReader();
    if (!reader) {
        throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    return (async function* () {
        while (true) {
            const { value, done } = await reader.read();
            if (done) {
                break;
            }
            buffer += decoder.decode(value, { stream: true });

            let lines = buffer.split('\n');
            buffer = lines.pop() || '';
            for (const line of lines) {
                if (line.trim() === '') {
                    continue;
                }
                try {
                    const event = JSON.parse(line) as ChatStreamEvent;
                    yield event;
                }
                catch (error) {
                    console.error('Error parsing stream event:', error);
                }
            }
        }
        if (buffer.trim() !== '') {
            try {
                const event = JSON.parse(buffer) as ChatStreamEvent;
                yield event;
            }
            catch (error) {
                console.error('Error parsing final stream event:', error);
            }
        }
    })();
}