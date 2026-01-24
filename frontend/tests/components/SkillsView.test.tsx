import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SkillsView } from '../../src/components/SkillsView';
import { apiClient } from '../../src/api/client';

// Mock the API client
vi.mock('../../src/api/client', () => ({
    apiClient: {
        getSkills: vi.fn(),
        getSkillDetails: vi.fn(),
    },
}));

// Mock react-markdown
vi.mock('react-markdown', () => ({
    default: ({ children }: { children: string }) => <div data-testid="markdown">{children}</div>,
}));

const mockSkills = {
    skills: [
        { name: 'review_code' },
        { name: 'search_web' },
        { name: 'manage_git' },
    ],
};

describe('SkillsView', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('shows loading state initially', () => {
        vi.mocked(apiClient.getSkills).mockImplementation(() => new Promise(() => { }));
        render(<SkillsView />);

        expect(screen.getByText('Loading skills...')).toBeInTheDocument();
    });

    it('renders skills library header', async () => {
        vi.mocked(apiClient.getSkills).mockResolvedValue(mockSkills);
        render(<SkillsView />);

        await waitFor(() => {
            expect(screen.getByText('Skills Library')).toBeInTheDocument();
        });
    });

    it('displays skill list', async () => {
        vi.mocked(apiClient.getSkills).mockResolvedValue(mockSkills);
        render(<SkillsView />);

        await waitFor(() => {
            expect(screen.getByText('review_code')).toBeInTheDocument();
            expect(screen.getByText('search_web')).toBeInTheDocument();
            expect(screen.getByText('manage_git')).toBeInTheDocument();
        });
    });

    it('fetches skill content when clicked', async () => {
        vi.mocked(apiClient.getSkills).mockResolvedValue(mockSkills);
        vi.mocked(apiClient.getSkillDetails).mockResolvedValue('# Review Code\n\nA skill for reviewing code quality.');
        render(<SkillsView />);

        await waitFor(() => {
            expect(screen.getByText('review_code')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('review_code'));

        await waitFor(() => {
            expect(apiClient.getSkillDetails).toHaveBeenCalledWith('review_code');
        });
    });

    it('shows placeholder when no skill selected', async () => {
        vi.mocked(apiClient.getSkills).mockResolvedValue(mockSkills);
        render(<SkillsView />);

        await waitFor(() => {
            expect(screen.getByText('Select a skill from the list to view its documentation.')).toBeInTheDocument();
        });
    });

    it('shows error when API fails', async () => {
        vi.mocked(apiClient.getSkills).mockRejectedValue(new Error('Failed'));
        render(<SkillsView />);

        await waitFor(() => {
            expect(screen.getByText(/Error:/)).toBeInTheDocument();
        });
    });

    it('calls API on mount', async () => {
        vi.mocked(apiClient.getSkills).mockResolvedValue(mockSkills);
        render(<SkillsView />);

        await waitFor(() => {
            expect(apiClient.getSkills).toHaveBeenCalledTimes(1);
        });
    });
});
