'use client';

import { useEffect, useState } from 'react';

import { DocumentList } from '@/components/DocumentList';
import { UploadZone } from '@/components/UploadZone';
import { listDocuments } from '@/lib/api';
import type { DocumentSummary } from '@/lib/types';

export default function Page() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);

  const fetchDocuments = async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);

    } catch (error) {
      console.error('Error fetching documents:', error);
      alert('Error fetching documents');
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <div className="page">
      <h1>Document Q&amp;A</h1>
      <UploadZone onDone={fetchDocuments} />
      <DocumentList docs={documents} onChange={fetchDocuments} />
    </div>
  );
}
