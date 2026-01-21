import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AgentsView } from '../../src/components/AgentsView';
import { apiClient } from '../../src/api/client';

// Mock the API client
vi.mock('../../src/api/client', () => ({
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
        { domain: 'course_creator', name: 'orchestrator', path: 'domains/course_creator/orchestrator' },
        { domain: 'course_creator', name: 'researcher', path: 'domains/course_creator/researcher' },
        { domain: 'customer_service', name: 'support', path: 'domains/customer_service/support' },
    ],
};

describe('AgentsView', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('shows loading state initially', async () => {
        vi.mocked(apiClient.getAgents).mockImplementation(() => new Promise(() => { }));
        render(<AgentsView />);

        expect(screen.getByText('Loading agents...')).toBeInTheDocument();
    });

    it('renders agent registry header', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        render(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('Agent Registry')).toBeInTheDocument();
        });
    });

    it('displays agents grouped by domain', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        render(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('course creator')).toBeInTheDocument();
            expect(screen.getByText('customer service')).toBeInTheDocument();
            expect(screen.getByText('orchestrator')).toBeInTheDocument();
            expect(screen.getByText('researcher')).toBeInTheDocument();
        });
    });

    it('fetches agent config when clicked', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        vi.mocked(apiClient.getAgentDetails).mockResolvedValue('name: orchestrator\nmodel: gemini-2.0-flash');
        render(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('orchestrator')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('orchestrator'));

        await waitFor(() => {
            expect(apiClient.getAgentDetails).toHaveBeenCalledWith('course_creator', 'orchestrator');
        });
    });

    it('shows error message when API fails', async () => {
        vi.mocked(apiClient.getAgents).mockRejectedValue(new Error('Failed to fetch'));
        render(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText(/Error:/)).toBeInTheDocument();
        });
    });

    it('shows placeholder when no agent selected', async () => {
        vi.mocked(apiClient.getAgents).mockResolvedValue(mockAgents);
        render(<AgentsView />);

        await waitFor(() => {
            expect(screen.getByText('Select an agent to view its configuration.')).toBeInTheDocument();
        });
    });
});
