import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ModelsView } from '../../src/components/ModelsView';
import { apiClient } from '../../src/api/client';

// Mock the API client
vi.mock('../../src/api/client', () => ({
    apiClient: {
        getModels: vi.fn(),
    },
}));

const mockModels = {
    models: [
        {
            name: 'models/gemini-2.0-flash',
            display_name: 'Gemini 2.0 Flash',
            description: 'Fast and efficient model for quick responses',
            input_token_limit: 1000000,
            output_token_limit: 8192,
            temperature: 0.7,
        },
        {
            name: 'models/gemini-2.5-pro',
            display_name: 'Gemini 2.5 Pro',
            description: 'Advanced reasoning and complex tasks',
            input_token_limit: 2000000,
            output_token_limit: 65536,
            temperature: 0.9,
        },
    ],
};

describe('ModelsView', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('shows loading state initially', () => {
        vi.mocked(apiClient.getModels).mockImplementation(() => new Promise(() => { }));
        render(<ModelsView />);

        expect(screen.getByText('Loading models...')).toBeInTheDocument();
    });

    it('renders header correctly', async () => {
        vi.mocked(apiClient.getModels).mockResolvedValue(mockModels);
        render(<ModelsView />);

        await waitFor(() => {
            expect(screen.getByText('Available Models')).toBeInTheDocument();
            expect(screen.getByText(/Discover the Gemini models/)).toBeInTheDocument();
        });
    });

    it('displays model cards with names', async () => {
        vi.mocked(apiClient.getModels).mockResolvedValue(mockModels);
        render(<ModelsView />);

        await waitFor(() => {
            expect(screen.getByText('Gemini 2.0 Flash')).toBeInTheDocument();
            expect(screen.getByText('Gemini 2.5 Pro')).toBeInTheDocument();
        });
    });

    it('displays model descriptions', async () => {
        vi.mocked(apiClient.getModels).mockResolvedValue(mockModels);
        render(<ModelsView />);

        await waitFor(() => {
            expect(screen.getByText(/Fast and efficient/)).toBeInTheDocument();
            expect(screen.getByText(/Advanced reasoning/)).toBeInTheDocument();
        });
    });

    it('displays token limits', async () => {
        vi.mocked(apiClient.getModels).mockResolvedValue(mockModels);
        render(<ModelsView />);

        await waitFor(() => {
            expect(screen.getByText('1,000,000')).toBeInTheDocument(); // Input limit
            expect(screen.getByText('8,192')).toBeInTheDocument(); // Output limit
        });
    });

    it('shows error message when API fails', async () => {
        vi.mocked(apiClient.getModels).mockRejectedValue(new Error('API Error'));
        render(<ModelsView />);

        await waitFor(() => {
            expect(screen.getByText(/Error:/)).toBeInTheDocument();
        });
    });

    it('calls API on mount', async () => {
        vi.mocked(apiClient.getModels).mockResolvedValue(mockModels);
        render(<ModelsView />);

        await waitFor(() => {
            expect(apiClient.getModels).toHaveBeenCalledTimes(1);
        });
    });
});
