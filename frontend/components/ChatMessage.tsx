'use client';

import type { ReactNode } from 'react';

import { CitationPopover } from '@/components/CitationPopover';
import type { ChatMessage, Citation } from '@/lib/types';

export function renderWithCitations(text: string, citations: Citation[]): ReactNode[] {
  const map = new Map<number, Citation>();
  for (const c of citations) map.set(c.n, c);

  const parts: ReactNode[] = [];
  const regex = /\[(\d+)\]/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<span key={key++}>{text.slice(lastIndex, match.index)}</span>);
    }
    const n = Number(match[1]);
    const cite = map.get(n);
    if (cite) {
      parts.push(<CitationPopover key={key++} cite={cite} />);
    } else {
      parts.push(<span key={key++}>{match[0]}</span>);
    }
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) {
    parts.push(<span key={key++}>{text.slice(lastIndex)}</span>);
  }
  return parts;
}

export function ChatMessageView({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-2`}>
      <div
        className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
          isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
        }`}
      >
        {isUser ? (
          <span className="whitespace-pre-wrap">{msg.content}</span>
        ) : (
          <span className="whitespace-pre-wrap">
            {renderWithCitations(msg.content, msg.citations ?? [])}
          </span>
        )}
      </div>
    </div>
  );
}
