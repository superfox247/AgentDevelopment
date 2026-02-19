/**
 * API client for Agent Platform dashboard.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '60000', 10);

export const apiClient = {
    getBaseUrl(): string {
        return typeof API_BASE === 'string' && API_BASE.startsWith('http')
            ? API_BASE
            : (typeof window !== 'undefined' ? window.location.origin : '') + API_BASE;
    },

    async chatWithAgentStream(agentName: string, message: string, sessionId: string): Promise<Response> {
        const base = this.getBaseUrl();
        const url = `${base.replace(/\/$/, '')}/chat/${agentName}`;
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: sessionId }),
            signal: AbortSignal.timeout(API_TIMEOUT),
        });
        if (!res.ok) {
            const err = (await res.json().catch(() => ({}))) as { detail?: string };
            throw new Error(err.detail || 'Chat request failed');
        }
        return res;
    },

    async getAgents(): Promise<AgentInfo[]> {
        const base = this.getBaseUrl();
        const url = `${base.replace(/\/$/, '')}/agents`;
        const res = await fetch(url, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            signal: AbortSignal.timeout(API_TIMEOUT),
        });
        if (!res.ok) {
            const err = (await res.json().catch(() => ({}))) as { detail?: string };
            throw new Error(err.detail || 'Failed to fetch agents');
        }
        const data = (await res.json()) as AgentsResponse;
        return data.agents;
    },

    // --- Context Engine ---

    async searchContextEngine(query: string, limit: number = 10): Promise<SearchResponse> {
        const res = await fetch('/api/context-engine/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, limit }),
            signal: AbortSignal.timeout(API_TIMEOUT),
        });
        if (!res.ok) {
            const err = (await res.json().catch(() => ({}))) as { detail?: string };
            throw new Error(err.detail || 'Search failed');
        }
        return res.json();
    },

    async getContextEngineStats(): Promise<StatsResponse> {
        const res = await fetch('/api/context-engine/stats', {
            signal: AbortSignal.timeout(API_TIMEOUT),
        });
        if (!res.ok) throw new Error('Failed to fetch stats');
        return res.json();
    },

    async getContextEngineFiles(): Promise<FilesResponse> {
        const res = await fetch('/api/context-engine/files', {
            signal: AbortSignal.timeout(API_TIMEOUT),
        });
        if (!res.ok) throw new Error('Failed to fetch files');
        return res.json();
    },
};

// --- Types ---

export interface AgentInfo {
    domain: string;
    name: string;
    path: string;
}

export interface AgentsResponse {
    agents: AgentInfo[];
}

export interface SearchResult {
    id: string;
    name: string | null;
    description: string | null;
    score: number | null;
    rerank_score: number | null;
    graph_props: Record<string, unknown>;
}

export interface SearchResponse {
    query: string;
    results: SearchResult[];
    count: number;
}

export interface StatsResponse {
    graph: Record<string, unknown>;
    vector: Record<string, unknown>;
}

export interface IndexedFile {
    path: string;
    hash: string | null;
    updated_at: number | null;
}

export interface FilesResponse {
    files: IndexedFile[];
    count: number;
}
