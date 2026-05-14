import NEXT_PUBLIC_API_BASE_URL from '../config';
import NEXT_PUBLIC_APP_TOKEN from '../config';

export const APP_TOKEN = NEXT_PUBLIC_APP_TOKEN;
export const API_BASE_URL = NEXT_PUBLIC_API_BASE_URL;

headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${APP_TOKEN}`
}

export async function listDocuments() {
    const response = await fetch(`${API_BASE_URL}/documents`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${APP_TOKEN}`
        }
    });

    if (!response.ok) {
        throw new Error(`Error fetching documents: ${response.statusText}`);
    }
    return await response.json();
}

export async function deleteDocument(documentId: string) {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${APP_TOKEN}`
        }
    });

    if (!response.ok) {
        throw new Error(`Error deleting document: ${response.statusText}`);
    }
    return await response.json();
}

export async function ingestFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/documents/ingest`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${APP_TOKEN}`
        },
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Error ingesting file: ${response.statusText}`);
    }
    return await response.json();
}

export async function ingestUrl(url: string) {
    const response = await fetch(`${API_BASE_URL}/documents/ingest_url`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${APP_TOKEN}`
        },
        body: JSON.stringify({ url })
    });

    if (!response.ok) {
        throw new Error(`Error ingesting URL: ${response.statusText}`);
    }
    return await response.json();
}

export function chatStreamUrl() {
    const url = new URL(`${API_BASE_URL}/chat`);
    url.searchParams.append('app_token', APP_TOKEN);
    return url.toString();
}

export function chatHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${APP_TOKEN}`
    };
}

