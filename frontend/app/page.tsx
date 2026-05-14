'use client';

import Link from 'next/link';
import { useState } from 'react';

import { ChatInput } from '@/components/ChatInput';
import { ChatMessageView } from '@/components/ChatMessage';
import { chatHeaders, chatStreamUrl } from '@/lib/api';
import { parseChatStream } from '@/lib/sse';
import type { ChatMessage, Citation } from '@/lib/types';

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const send = async (text: string) => {
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: text },
      { role: 'assistant', content: '' },
    ]);
    setStreaming(true);

    try {
      const resp = await fetch(chatStreamUrl(), {
        method: 'POST',
        headers: chatHeaders(),
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
      }

      let answer = '';
      let citations: Citation[] = [];
      for await (const ev of parseChatStream(resp)) {
        if (ev.type === 'session') {
          setSessionId(ev.session_id);
        } else if (ev.type === 'token') {
          answer += ev.content;
          setMessages((prev) => patchLastAssistant(prev, { content: answer, citations }));
        } else if (ev.type === 'citations') {
          citations = ev.citations;
          setMessages((prev) => patchLastAssistant(prev, { content: answer, citations }));
        } else if (ev.type === 'error') {
          setMessages((prev) =>
            patchLastAssistant(prev, { content: `Error: ${ev.message}` }),
          );
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setMessages((prev) => patchLastAssistant(prev, { content: `Error: ${message}` }));
    } finally {
      setStreaming(false);
    }
  };

  return (
    <main className="mx-auto flex h-screen max-w-3xl flex-col">
      <header className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <h1 className="text-lg font-semibold">KnowledgeBase AI</h1>
        <Link href="/documents" className="text-sm text-blue-600 hover:underline">
          Documents
        </Link>
      </header>
      <div className="flex-1 overflow-y-auto px-4 py-2">
        {messages.length === 0 ? (
          <p className="mt-8 text-center text-sm text-gray-500">
            Ask a question about your ingested documents.
          </p>
        ) : (
          messages.map((msg, i) => <ChatMessageView key={i} msg={msg} />)
        )}
      </div>
      <ChatInput onSend={send} disabled={streaming} />
    </main>
  );
}

function patchLastAssistant(
  messages: ChatMessage[],
  patch: Partial<Pick<ChatMessage, 'content' | 'citations'>>,
): ChatMessage[] {
  const next = messages.slice();
  for (let i = next.length - 1; i >= 0; i--) {
    if (next[i].role === 'assistant') {
      next[i] = { ...next[i], ...patch };
      break;
    }
  }
  return next;
}
