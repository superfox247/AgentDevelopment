/**
 * Baseline API client: health + chat only.
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
};

export interface AgentInfo {
    domain: string;
    name: string;
    path: string;
}

export interface AgentsResponse {
    agents: AgentInfo[];
}
