import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DockerMonitor from '../../src/components/DockerMonitor';
import { apiClient } from '../../src/api/client';

// Mock the API client
vi.mock('../../src/api/client', () => ({
    apiClient: {
        getDockerStats: vi.fn(),
        controlContainer: vi.fn(),
        getContainerLogs: vi.fn(),
    },
}));

const mockContainers = {
    containers: [
        {
            id: 'abc123',
            name: 'content_creation-orchestrator',
            status: 'Up 2 hours',
            image: 'orchestrator:latest',
        },
        {
            id: 'def456',
            name: 'content_creation-image_gen',
            status: 'Exited (0)',
            image: 'image_gen:latest',
        },
    ],
};

describe('DockerMonitor', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it.skip('renders loading state then containers', async () => {
        vi.mocked(apiClient.getDockerStats).mockResolvedValue(mockContainers);
        render(<DockerMonitor />);

        await waitFor(() => {
            expect(screen.getByText(/orchestrator/i)).toBeInTheDocument();
        });
    });

    it('displays container names', async () => {
        vi.mocked(apiClient.getDockerStats).mockResolvedValue(mockContainers);
        render(<DockerMonitor />);

        await waitFor(() => {
            expect(screen.getByText(/content_creation-orchestrator/i)).toBeInTheDocument();
            expect(screen.getByText(/content_creation-image_gen/i)).toBeInTheDocument();
        });
    });

    it('shows Up status for running containers', async () => {
        vi.mocked(apiClient.getDockerStats).mockResolvedValue(mockContainers);
        render(<DockerMonitor />);

        await waitFor(() => {
            expect(screen.getByText('Up')).toBeInTheDocument();
        });
    });

    it('shows Exited status for stopped containers', async () => {
        vi.mocked(apiClient.getDockerStats).mockResolvedValue(mockContainers);
        render(<DockerMonitor />);

        await waitFor(() => {
            expect(screen.getByText('Exited')).toBeInTheDocument();
        });
    });

    it('fetches docker stats on mount', async () => {
        vi.mocked(apiClient.getDockerStats).mockResolvedValue(mockContainers);
        render(<DockerMonitor />);

        await waitFor(() => {
            expect(apiClient.getDockerStats).toHaveBeenCalled();
        });
    });

    it('handles empty container list', async () => {
        vi.mocked(apiClient.getDockerStats).mockResolvedValue({ containers: [] });
        render(<DockerMonitor />);

        await waitFor(() => {
            expect(screen.getByText(/No active containers/i)).toBeInTheDocument();
        });
    });
});
