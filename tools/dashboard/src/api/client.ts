import axios, { AxiosInstance } from 'axios';
import {
    AgentsResponseSchema,
    ArtifactsResponseSchema,
    ContainerControlResponseSchema,
    ContainerLogsResponseSchema,
    DockerStatsResponseSchema,
    ModelsResponseSchema,
    SkillsResponseSchema,
    SystemFixResponseSchema,
    SystemStatusSchema,
    type AgentsResponse,
    type ArtifactsResponse,
    type DockerStatsResponse,
    type ModelsResponse,
    type SkillsResponse,
    type SystemFixResponse,
    type SystemStatus,
} from './schemas';

const API_BASE = 'http://localhost:8010/api';

/**
 * Standardized API Client for Dashboard
 */
class ApiClient {
    private readonly client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: API_BASE,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Response interceptor for consistent error handling
        this.client.interceptors.response.use(
            (response) => {
                // Unwrap standardized response envelope if present
                if (response.data?.data) {
                    return response.data.data;
                }
                return response.data;
            },
            (error) => {
                console.error('API Error:', error);
                // Standardized error object
                const message = error.response?.data?.detail || error.message || 'Unknown Error';
                return Promise.reject(new Error(message));
            }
        );
    }

    // --- Docker Infrastructure ---

    /**
     * Retrieves current Docker container statistics.
     * @returns Parsed Docker statistics including container status and resource usage.
     */
    async getDockerStats(): Promise<DockerStatsResponse> {
        const data = await this.client.get('/docker');
        return DockerStatsResponseSchema.parse(data);
    }

    /**
     * Controls a Docker container's state.
     * @param id - The container ID or name.
     * @param action - The action to perform ('start', 'stop', 'restart').
     * @returns The result of the control operation.
     */
    async controlContainer(id: string, action: string) {
        const data = await this.client.post(`/docker/${id}/${action}`);
        return ContainerControlResponseSchema.parse(data);
    }

    async getContainerLogs(id: string, tail = 50) {
        const data = await this.client.get(`/logs/${id}?tail=${tail}`);
        return ContainerLogsResponseSchema.parse(data);
    }

    async getContainerLogsStream(id: string, signal?: AbortSignal) {
        const response = await fetch(`${this.client.defaults.baseURL}/logs/${id}`, { signal });
        if (!response.ok) throw new Error('Log stream failed');
        return response;
    }

    async logError(error: Error, component?: string) {
        // Safe logging that doesn't throw if telemetry fails
        try {
            await this.client.post('/telemetry/log', {
                level: 'error',
                message: error.message,
                stack: error.stack,
                component: component || 'frontend',
                url: globalThis.location.href,
                user_agent: navigator.userAgent
            });
        } catch (e) {
            console.warn('Failed to send telemetry:', e);
        }
    }

    // --- System Operations ---

    async getSystemStatus(): Promise<SystemStatus> {
        const data = await this.client.get('/status');
        return SystemStatusSchema.parse(data);
    }

    async runSystemFix(): Promise<SystemFixResponse> {
        const data = await this.client.post('/system/fix');
        return SystemFixResponseSchema.parse(data);
    }

    async verifySystem(testName = 'content_engine') {
        return this.client.post('/verify', { test_name: testName });
    }

    async verifySystemStream(testName = 'content_engine') {
        const response = await fetch(`${this.client.defaults.baseURL}/verify/stream?test_name=${testName}`);
        if (!response.ok) throw new Error('Verification stream failed');
        return response;
    }

    async runBenchmarkStream() {
        const response = await fetch(`${this.client.defaults.baseURL}/benchmark/stream`);
        if (!response.ok) throw new Error('Benchmark stream failed');
        return response;
    }

    // --- Knowledge & Skills ---

    async getArtifacts(): Promise<ArtifactsResponse> {
        const data = await this.client.get('/artifacts');
        return ArtifactsResponseSchema.parse(data);
    }

    async getSkills(): Promise<SkillsResponse> {
        const data = await this.client.get('/skills');
        return SkillsResponseSchema.parse(data);
    }

    async getSkillDetails(name: string) {
        // Returns text content (FileResponse)
        const data = await this.client.get(`/skills/${name}`);
        return data as unknown as string;
    }

    // --- Agents & Models ---

    async getAgents(): Promise<AgentsResponse> {
        const data = await this.client.get('/agents');
        return AgentsResponseSchema.parse(data);
    }

    async getAgentDetails(domain: string, name: string) {
        // Returns text content (FileResponse)
        const data = await this.client.get(`/agents/${domain}/${name}`);
        return data as unknown as string;
    }

    async getModels(): Promise<ModelsResponse> {
        const data = await this.client.get('/models');
        return ModelsResponseSchema.parse(data);
    }

    /**
     * Sends a chat message to a specific agent.
     * @param agentName - The name of the target agent.
     * @param prompt - The user's message/prompt.
     * @returns The agent's response.
     */
    async chatWithAgent(agentName: string, prompt: string) {
        return this.client.post(`/chat/${agentName}`, { prompt });
    }

    async chatWithAgentStream(agentName: string, message: string, sessionId: string) {
        // Use native fetch for streaming to support ReadableStream
        const response = await fetch(`${this.client.defaults.baseURL}/chat/${agentName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: sessionId })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Stream failed');
        }

        return response;
    }

    /**
     * Triggers the image generation agent.
     * @param prompt - The image description prompt.
     * @param model - Optional model identifier (e.g., 'imagen-3.0').
     * @returns The generation result containing the image path.
     */
    async generateImage(prompt: string, model: string | null = null): Promise<unknown> {
        return this.client.post('/generate/image', { prompt, model });
    }
}

export const apiClient = new ApiClient();
