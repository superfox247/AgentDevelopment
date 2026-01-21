---
name: TypeScript Stack
description: TypeScript-specific patterns and tools
---

# TypeScript Stack

## Package Management
- Tool: `pnpm`
- Lock: `pnpm-lock.yaml`
- Run scripts: `pnpm <script>`

## Compilation
- Config: `tsconfig.json`, `tsconfig.node.json`
- Check: `pnpm exec tsc --noEmit`

## Linting
- ESLint: `pnpm lint`
- Config: `eslint.config.ts`

## Testing
- Vitest: `pnpm test`
- Playwright: `pnpm test:smoke`

---

## Patterns

### Module Imports
```typescript
// ✅ Use node: prefix for builtins
import { readFile } from 'node:fs/promises';

// ✅ Use explicit .js extensions for local imports (ESM)
import { utils } from './utils.js';

// ✅ Named exports preferred
export function doThing() {}
```

### Type Safety
```typescript
// ✅ Strict typing — never use 'any'
interface User {
  readonly id: string;
  name: string;
  email?: string;  // explicitly optional
}

// ✅ Use 'unknown' for dynamic data, then narrow
function process(data: unknown): void {
  if (typeof data === 'string') {
    console.log(data.toUpperCase());
  }
}

// ✅ Use 'as const' for literal types
const STATUS = { OK: 200, ERROR: 500 } as const;
```

### Error Handling
```typescript
// ✅ Custom error classes
class ApiError extends Error {
  constructor(
    message: string,
    public readonly statusCode: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// ✅ Handle errors explicitly
async function fetchData(url: string): Promise<Data> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new ApiError('Fetch failed', response.status);
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      // handle known error
    }
    throw error; // re-throw unknown
  }
}
```

### Async Patterns
```typescript
// ✅ Parallel execution
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
]);

// ✅ Error handling in parallel
const results = await Promise.allSettled([
  riskyOperation1(),
  riskyOperation2(),
]);

// ✅ Cleanup with try-finally
async function withConnection<T>(fn: (conn: Connection) => Promise<T>): Promise<T> {
  const conn = await connect();
  try {
    return await fn(conn);
  } finally {
    await conn.close();
  }
}
```

---

## Common Gotchas

| Issue | Solution |
|-------|----------|
| `null` vs `undefined` | Use `undefined` for optional values, `null` for intentional absence |
| Missing `readonly` | Always use `readonly` for object properties that shouldn't change |
| Object equality | Use deep comparison or `JSON.stringify` for objects |
| Array methods mutating | `sort()` mutates, use `toSorted()` or spread first |
| `this` in callbacks | Use arrow functions or `.bind()` |

---

## Project Structure

```
src/
├── api/           # API client, endpoints
├── components/    # React components
├── hooks/         # Custom hooks
├── types/         # Shared type definitions
├── utils/         # Utility functions
└── index.tsx      # Entry point
```
