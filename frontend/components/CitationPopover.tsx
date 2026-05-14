'use client';

import { useState } from 'react';

import type { Citation } from '@/lib/types';

export function CitationPopover({ cite }: { cite: Citation }) {
  const [open, setOpen] = useState(false);

  return (
    <span className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="mx-0.5 inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-blue-100 px-1.5 align-baseline text-xs font-medium text-blue-700 hover:bg-blue-200"
      >
        {cite.n}
      </button>
      {open && (
        <span className="absolute left-0 top-full z-10 mt-1 block w-72 rounded border border-gray-200 bg-white p-3 text-left text-sm shadow-lg">
          <span className="block whitespace-pre-wrap text-gray-800">{cite.snippet}</span>
          {cite.heading_path && (
            <span className="mt-2 block text-xs text-gray-500">{cite.heading_path}</span>
          )}
          {cite.page_number != null && (
            <span className="mt-1 block text-xs text-gray-500">Page {cite.page_number}</span>
          )}
        </span>
      )}
    </span>
  );
}
