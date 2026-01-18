# Tech Stack Patterns: Frontend

## 1. React v19
Standardized for the Agent Central Dashboard.

### Best Practices
- **React Compiler**: Trust the compiler for memoization. Avoid manual `useMemo`/`useCallback` unless profiling shows regression.
- **Actions**: Prefer `<form action={fn}>` for async data mutations.
- **Improved Hooks**:
    - `use(Context)`: Consume context conditionally.
    - `useOptimistic`: Immediate UI feedback for agent interactions.
- **Resilience**:
    - **Error Boundaries**: Every high-level view (Logs, Agents, Generator) MUST be wrapped in an `ErrorBoundary`.
    - **Suspense**: Use for async data fetching components.

### Anti-Patterns
- **useEffect for Data Fetching**: Prefer library-specific loaders or Server Components.
- **Index as Key**: Prohibited. Use `crypto.randomUUID()` (with fallback) or resource unique identifiers.

## 2. Tailwind CSS v4
Theme configuration is managed via CSS variables in `index.css`.

### Usage Standards
- **CSS-First**: Define theme variables in a `@theme` block.
- **Alpha Modifiers**: Use `bg-primary/50` (uses native `color-mix`).
- **Modern Gradients**: `bg-linear-to-*` instead of `bg-gradient-to-*`.
- **Space Rule**: Arbitrary values in `@apply` MUST NOT contain spaces (e.g., `shadow-[0_0_15px_... ]`).

## 3. Communication Standard
### A. Centralized API Client
All data fetching and command execution must use the centralized `apiClient`.
- **Implementation**: [Centralized API Client](./implementation/centralized_api_client.md)
- **Benefit**: Automatic response unwrapping, consistent error reporting, and simplified component code.

### B. Portability
- **Relative Port Awareness**: Avoid hardcoding ports (5173). Vite may shift ports if 5173 is locked. Use relative URLs or the `apiClient`'s base URL configuration.

## 4. Component Architecture
- **Prose Injection**: Use the `Component Injector` pattern in `react-markdown` to map documentation tags to standard Tailwind classes.
- **Race Condition Prevention**: Avoid calling `setState` synchronously within the body of a `useEffect` if it can be triggered by human interaction (e.g., expanding a card). Move these triggers to event handlers (`onClick`) to ensure a fresh render cycle.
