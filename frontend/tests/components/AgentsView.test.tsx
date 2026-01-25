import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AgentsView } from '../../src/components/AgentsView';
import { apiClient } from '@/api/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createTestQueryClient = () => new QueryClient({
    defaultOptions: {
        queries: { retry: false },
    },
});

const renderWithClient = (ui: React.ReactNode) => {
    const testClient = createTestQueryClient();
    return render(
        <QueryClientProvider client={testClient}>{ui}</QueryClientProvider>
    );
};

// Mock the API client
vi.mock('@/api/client', () => ({
    apiClient: {
        getAgents: vi.fn(),
        getAgentDetails: vi.fn(),
        getAgentMetadata: vi.fn(),
    },
}));

// Mock react-syntax-highlighter
vi.mock('react-syntax-highlighter', () => {
    const MockComponent = ({ children }: { children: string }) => <pre data-testid="syntax-highlighter">{children}</pre>;
    MockComponent.registerLanguage = vi.fn();
    return { Light: MockComponent };
});
vi.mock('react-syntax-highlighter/dist/esm/languages/hljs/yaml', () => ({ default: {} }));
vi.mock('react-syntax-highlighter/dist/esm/styles/hljs', () => ({ atomOneDark: {} }));

const mockAgents = {
    agents: [
        { domain: 'content_creation', name: 'orchestrator', path: 'agents/orchestrator' },
        { domain: 'content_creation', name: 'researcher', path: 'agents/researcher_agent' },
        { domain: 'customer_service', name: 'support', path: 'agents/support' },
    ],
};

describe('AgentsView', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('shows loading state initially', async () => {
        vi.mocked(apiClient.getAgents).mockImplementation(() => new Promise(() => { }));
        renderWithClient(<AgentsView />);

        expect(screen.getByText('Loading agents...')).toBeInTheDocument();
    });

    it('renders agent registry header', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        renderWithClient(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('Agent Registry')).toBeInTheDocument();
        });
    });

    it('displays agents grouped by domain', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        renderWithClient(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('content creation')).toBeInTheDocument();
            expect(screen.getByText('customer service')).toBeInTheDocument();
            expect(screen.getByText('orchestrator')).toBeInTheDocument();
            expect(screen.getByText('researcher')).toBeInTheDocument();
        });
    });

    it('fetches agent config when clicked', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        vi.mocked(apiClient.getAgentDetails).mockResolvedValue('name: orchestrator\nmodel: gemini-2.0-flash');
        renderWithClient(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('orchestrator')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('orchestrator'));

        await waitFor(() => {
            expect(apiClient.getAgentDetails).toHaveBeenCalledWith('content_creation', 'orchestrator');
        });
    });

    it('shows error message when API fails', async () => {
        vi.mocked(apiClient.getAgents).mockRejectedValue(new Error('Failed to fetch'));
        renderWithClient(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText(/Error:/)).toBeInTheDocument();
        });
    });

    it('shows placeholder when no agent selected', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        renderWithClient(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('Select an agent to view its configuration.')).toBeInTheDocument();
        });
    });

    it('fetches and displays agent metadata when agent is selected', async () => {
        const mockMetadata = {
            name: 'researcher',
            path: 'agents/researcher_agent',
            description: 'Research assistant that browses the web',
            model: 'gemini-2.0-flash',
            has_server: true,
        };

        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        vi.mocked(apiClient.getAgentMetadata).mockResolvedValue(mockMetadata);
        vi.mocked(apiClient.getAgentDetails).mockResolvedValue('agent code');

        renderWithClient(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('researcher')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('researcher'));

        await waitFor(() => {
            expect(apiClient.getAgentMetadata).toHaveBeenCalledWith('researcher');
        });

        await waitFor(() => {
            expect(screen.getByText('Research assistant that browses the web')).toBeInTheDocument();
            expect(screen.getByText('gemini-2.0-flash')).toBeInTheDocument();
        });
    });

    it('displays server status indicator when server is available', async () => {
        const mockMetadata = {
            name: 'researcher',
            path: 'agents/researcher_agent',
            description: 'Test agent',
            model: 'gemini-2.0-flash',
            has_server: true,
        };

        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        vi.mocked(apiClient.getAgentMetadata).mockResolvedValue(mockMetadata);

        renderWithClient(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('researcher')).toBeInTheDocument();
        });

        // Check that metadata is fetched for preview (in list item)
        await waitFor(() => {
            expect(apiClient.getAgentMetadata).toHaveBeenCalled();
        });
    });

    it('handles metadata loading state', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        vi.mocked(apiClient.getAgentMetadata).mockImplementation(() => new Promise(() => { })); // Never resolves
        vi.mocked(apiClient.getAgentDetails).mockResolvedValue('agent code');

        renderWithClient(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('researcher')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('researcher'));

        // Should show loading state
        await waitFor(() => {
            expect(screen.getByText('Loading...')).toBeInTheDocument();
        });
    });
});
