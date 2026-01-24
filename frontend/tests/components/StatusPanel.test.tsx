import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import StatusPanel from '../../src/components/StatusPanel';
import { apiClient } from '../../src/api/client';

// Mock the API client
vi.mock('../../src/api/client', () => ({
    apiClient: {
        getSystemStatus: vi.fn(),
    },
}));

// Mock LogViewer to avoid complexity
vi.mock('../../src/components/LogViewer', () => ({
    default: ({ containerName, onClose }: { containerName: string; onClose: () => void }) => (
        <div data-testid="log-viewer">
            <span>Logs for {containerName}</span>
            <button onClick={onClose}>Close</button>
        </div>
    ),
}));

const mockStatus = {
    status: 'online',
    orchestrator: 'online',
    content_builder: 'online',
    image_generator: 'offline',
    customer_service: 'offline',
};

describe('StatusPanel', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders loading state initially', () => {
        vi.mocked(apiClient.getSystemStatus).mockImplementation(() => new Promise(() => { }));
        render(<StatusPanel />);

        // Should show loading placeholders (5 skeleton cards)
        const skeletons = document.querySelectorAll('.animate-pulse > div');
        expect(skeletons.length).toBeGreaterThan(0);
    });

    it('renders status cards when data loads', async () => {
        vi.mocked(apiClient.getSystemStatus).mockResolvedValue(mockStatus);
        render(<StatusPanel />);

        await waitFor(() => {
            expect(screen.getByText('System Core')).toBeInTheDocument();
            expect(screen.getByText('Orchestrator')).toBeInTheDocument();
            expect(screen.getByText('Content Factory')).toBeInTheDocument();
            expect(screen.getByText('Image Gen')).toBeInTheDocument();
            expect(screen.getByText('Customer Svc')).toBeInTheDocument();
        });
    });

    it('displays ACTIVE for online services', async () => {
        vi.mocked(apiClient.getSystemStatus).mockResolvedValue(mockStatus);
        render(<StatusPanel />);

        await waitFor(() => {
            const activeLabels = screen.getAllByText('ACTIVE');
            expect(activeLabels.length).toBeGreaterThanOrEqual(2); // System Core and Orchestrator
        });
    });

    it('displays OFFLINE for offline services', async () => {
        vi.mocked(apiClient.getSystemStatus).mockResolvedValue(mockStatus);
        render(<StatusPanel />);

        await waitFor(() => {
            const offlineLabels = screen.getAllByText('OFFLINE');
            expect(offlineLabels.length).toBeGreaterThanOrEqual(1);
        });
    });

    it('shows error state when API fails', async () => {
        vi.mocked(apiClient.getSystemStatus).mockRejectedValue(new Error('Network error'));
        render(<StatusPanel />);

        await waitFor(() => {
            expect(screen.getByText('System Unreachable')).toBeInTheDocument();
        });
    });

    it('calls API on mount', async () => {
        vi.mocked(apiClient.getSystemStatus).mockResolvedValue(mockStatus);
        render(<StatusPanel />);

        await waitFor(() => {
            expect(apiClient.getSystemStatus).toHaveBeenCalledTimes(1);
        });
    });
});
