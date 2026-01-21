---
name: React Stack
description: React-specific component patterns
---

# React Stack

## Testing
- Library: `@testing-library/react`
- Matchers: `@testing-library/jest-dom`
- Framework: Vitest

---

## Component Patterns

### Typed Props
```tsx
interface Props {
  readonly value: string;
  readonly onChange?: (value: string) => void;
}

export function MyComponent({ value, onChange }: Props) {
  return (
    <input
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
    />
  );
}
```

### Error Boundaries (Mandatory)
All views **must** be wrapped in `<ErrorBoundary>`.

```tsx
import { Component, type ReactNode, type ErrorInfo } from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<
  { children: ReactNode; fallback?: ReactNode },
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('ErrorBoundary caught:', error, info);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback ?? <div>Something went wrong.</div>;
    }
    return this.props.children;
  }
}
```

---

## Hooks Patterns

### useEffect Cleanup
```tsx
useEffect(() => {
  const controller = new AbortController();
  
  fetchData({ signal: controller.signal })
    .then(setData)
    .catch((err) => {
      if (err.name !== 'AbortError') setError(err);
    });
  
  // ✅ Always return cleanup function
  return () => controller.abort();
}, [dependency]);
```

### useMemo / useCallback
```tsx
// ✅ Memoize expensive computations
const filtered = useMemo(
  () => items.filter((i) => i.active),
  [items]
);

// ✅ Memoize callbacks passed to children
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);
```

### Custom Hooks
```tsx
function useApi<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    
    fetch(url, { signal: controller.signal })
      .then((res) => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [url]);

  return { data, loading, error };
}
```

---

## Data Fetching Pattern

```tsx
function UserList() {
  const { data, loading, error } = useApi<User[]>('/api/users');

  if (loading) return <Spinner />;
  if (error) return <ErrorDisplay error={error} />;
  if (!data) return null;

  return (
    <ul>
      {data.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

---

## Testing

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

describe('MyComponent', () => {
  it('renders value', () => {
    render(<MyComponent value="test" />);
    expect(screen.getByDisplayValue('test')).toBeInTheDocument();
  });

  it('calls onChange', () => {
    const onChange = vi.fn();
    render(<MyComponent value="" onChange={onChange} />);
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'new' },
    });
    expect(onChange).toHaveBeenCalledWith('new');
  });
});
```

---

## State Management

| Scope | Tool |
|-------|------|
| Local | `useState` |
| Component tree | `useContext` |
| Complex | Zustand or useReducer |
