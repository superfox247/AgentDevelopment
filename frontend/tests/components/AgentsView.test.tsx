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
        { domain: 'content_creation', name: 'orchestrator', path: 'domains/content_creation/orchestrator' },
        { domain: 'content_creation', name: 'researcher', path: 'domains/content_creation/researcher' },
        { domain: 'customer_service', name: 'support', path: 'domains/customer_service/support' },
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
});
