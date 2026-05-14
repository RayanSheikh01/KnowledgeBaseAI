'use client';

import { useState } from 'react';

import { deleteDocument } from '@/lib/api';
import type { DocumentSummary } from '@/lib/types';

export function DocumentList({
  docs,
  onChange,
}: {
  docs: DocumentSummary[];
  onChange: () => void;
}) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }
    setDeletingId(documentId);
    try {
      await deleteDocument(documentId);
      onChange();
    } catch (error) {
      console.error('Delete error:', error);
      alert('Error deleting document');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="document-list">
      <h3>Your Documents</h3>
      {docs.length === 0 ? (
        <p>No documents uploaded yet.</p>
      ) : (
        <ul>
          {docs.map((doc) => (
            <li key={doc.id} className="document-item">
              <div>
                <strong>{doc.title}</strong> ({doc.source_type}, {doc.chunk_count} chunks)
              </div>
              <button onClick={() => handleDelete(doc.id)} disabled={deletingId === doc.id}>
                {deletingId === doc.id ? 'Deleting...' : 'Delete'}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
