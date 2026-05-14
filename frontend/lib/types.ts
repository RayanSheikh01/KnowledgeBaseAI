export DocumentSummary = {
    id: string;
    title: string;
    source_type: 'pdf' | 'text' | 'url';
    source_uri: string | null;
    chunk_count: number;
    created_at: string | null
}

export Citation = {
    n : number;
    chunk_id?: string;
    document_id: string;
    source?: string;
    snippet: string;
    page_number: number | null;
    head_path: string | null;
}

export ChatRole = 'user' | 'assistant';

export ChatMessage = {
    role: ChatRole;
    content: string;
    citations?: Citation[];
}

export ChatStreamEvent = {
    type: 'session' | 'token' | 'citations' | 'done' | 'error';
}