import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Simple smoke test to verify Vitest setup works
describe('Vitest Setup', () => {
    it('can render a basic React element', () => {
        render(<div data-testid="test-element">Hello World</div>);
        expect(screen.getByTestId('test-element')).toBeInTheDocument();
        expect(screen.getByText('Hello World')).toBeInTheDocument();
    });

    it('testing library matchers work', () => {
        render(<button disabled>Submit</button>);
        expect(screen.getByRole('button')).toBeDisabled();
        expect(screen.getByRole('button')).toHaveTextContent('Submit');
    });
});
