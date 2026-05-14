import type { DocumentSummary } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
const APP_TOKEN = process.env.NEXT_PUBLIC_APP_TOKEN ?? '';

function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
  return {
    'X-App-Token': APP_TOKEN,
    ...extra,
  };
}

export async function listDocuments(): Promise<DocumentSummary[]> {
  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: 'GET',
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Error fetching documents: ${response.statusText}`);
  }
  return await response.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Error deleting document: ${response.statusText}`);
  }
}

export async function ingestFile(file: File, title?: string): Promise<{ document_id: string; chunk_count: number }> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title ?? file.name);

  const response = await fetch(`${API_BASE_URL}/ingest/file`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`Error ingesting file: ${response.statusText}`);
  }
  return await response.json();
}

export async function ingestUrl(url: string): Promise<{ document_id: string; chunk_count: number }> {
  const response = await fetch(`${API_BASE_URL}/ingest/url`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ url }),
  });
  if (!response.ok) {
    throw new Error(`Error ingesting URL: ${response.statusText}`);
  }
  return await response.json();
}

export function chatStreamUrl(): string {
  return `${API_BASE_URL}/chat`;
}

export function chatHeaders(): Record<string, string> {
  return authHeaders({ 'Content-Type': 'application/json' });
}
