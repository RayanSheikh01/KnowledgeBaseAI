'use client';

import { useRef, useState } from 'react';

import { ingestFile, ingestUrl } from '@/lib/api';

export function UploadZone({ onDone }: { onDone: () => void }) {
  const [url, setUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file && !url) {
      alert('Please select a file or enter a URL');
      return;
    }
    setLoading(true);
    try {
      if (file) {
        await ingestFile(file);
      } else if (url) {
        await ingestUrl(url);
      }
      setFile(null);
      setUrl('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onDone();
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading document');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-zone">
      <h3>Upload Document</h3>
      <div className="upload-options">
        <div className="upload-option">
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={handleFileChange}
            ref={fileInputRef}
          />
        </div>
        <div className="upload-option">
          <input
            type="text"
            placeholder="Enter URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </div>
      </div>
      <button onClick={handleUpload} disabled={loading}>
        {loading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
}
