import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatView } from '../../src/components/ChatView';

beforeEach(() => {
    vi.restoreAllMocks();
});

describe('ChatView', () => {
    it('renders baseline layout and initial assistant guidance', () => {
        render(<ChatView />);

        expect(screen.getByLabelText('Select agent')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
        expect(screen.getByText('Hello. Choose an agent and send a message.')).toBeInTheDocument();
    });

    it('disables send button when input is empty', () => {
        render(<ChatView />);

        expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled();
    });
});
