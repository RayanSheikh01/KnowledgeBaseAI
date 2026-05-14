export type DocumentSummary = {
  id: string;
  title: string;
  source_type: 'pdf' | 'text' | 'url';
  source_uri: string | null;
  chunk_count: number;
  created_at: string | null;
};

export type Citation = {
  n: number;
  chunk_id?: string;
  document_id: string;
  source?: string;
  snippet: string;
  page_number: number | null;
  heading_path: string | null;
};

export type ChatRole = 'user' | 'assistant';

export type ChatMessage = {
  role: ChatRole;
  content: string;
  citations?: Citation[];
};

export type ChatStreamEvent =
  | { type: 'session'; session_id: string }
  | { type: 'token'; content: string }
  | { type: 'citations'; citations: Citation[] }
  | { type: 'done' }
  | { type: 'error'; message: string };
