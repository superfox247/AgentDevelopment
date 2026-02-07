# Frontend Rewrite Plan

**Goal:** Rip out the current frontend and redo it in a simple, industry-standard way using **OpenAPI as the source of truth**, **Orval** for codegen (TypeScript + Zod + React Query + Axios), and a clear separation between generated API layer and UI.

**Baseline scope:** For a **minimal dashboard** (agent selector + chat only, researcher + customer service, no Docker/models/skills/usage UIs), see **[DASHBOARD_BASELINE.md](./DASHBOARD_BASELINE.md)** — diagram, removed features, and what we keep.

### Quick start (high level)

1. **Backend:** Use dashboard API as OpenAPI source. Export `openapi.json` from `GET http://localhost:8010/openapi.json` before codegen.
2. **Orval:** Add `orval` + `@orval/zod`, add `orval.config.ts`, implement `src/api/mutator.ts`, run `pnpm run generate:api`.
3. **Frontend:** Delete `src/api/client.ts` and `src/api/schemas.ts`. Update all views to use generated React Query hooks and Zod schemas.
4. **Fix:** `index.html` → `main.tsx`; log stream URL → `/api/logs/{id}/stream`.
5. **Optional:** React Router, backend tags for `tags-split`, CI script for export + generate.

---

## 1. Current State (What We’re Replacing)

| Item | Location | Issue |
|------|----------|--------|
| **OpenAPI spec** | `frontend/openapi.json` | Static, unused by frontend; missing `/api/telemetry/log`, `/api/agents/{name}/metadata`; chat/generate routes not in dashboard API |
| **Zod schemas** | `frontend/src/api/schemas.ts` | Hand-written, duplicated from backend models |
| **API client** | `frontend/src/api/client.ts` | Hand-written Axios client; custom retries, interceptors; calls `/logs/{id}` for stream (should be `/logs/{id}/stream`) |
| **UI** | Tab-based `App.tsx` + views | Uses `apiClient` + schemas; React Query for some fetches |
| **Entry** | `index.html` → `main.jsx` | References `main.jsx` but project uses `main.tsx` |

**Backend (dashboard API):** FastAPI with Pydantic models. Serves OpenAPI at `/openapi.json` (default). Routers: `docker`, `agents`, `system`, `usage`. No `/api/chat/*` or `/api/generate/*` in dashboard.

---

## 2. Target Architecture

```
frontend/
├── src/
│   ├── api/
│   │   ├── generated/          # Orval output (do not edit)
│   │   │   ├── endpoints/      # React Query hooks + fetchers
│   │   │   ├── model/          # TS types
│   │   │   └── *.zod.ts        # Zod schemas per tag
│   │   └── mutator.ts          # Custom Axios instance (base URL, retries, errors)
│   ├── hooks/                  # Optional thin wrappers over generated hooks
│   ├── components/             # UI components using generated API
│   ├── App.tsx
│   ├── main.tsx
│   └── ...
├── openapi.json                # Exported from backend (or URL in Orval config)
├── orval.config.ts
└── package.json                # + orval, ensure axios + @tanstack/react-query + zod
```

**Source of truth:** Backend FastAPI app → `/openapi.json`. No hand-written API types or client.

---

## 3. Phase 1: Backend & OpenAPI Alignment

### 3.1 Single source of truth

- **Use the live dashboard API** as the OpenAPI source.
- **Export spec:** Either:
  - **Option A (recommended):** Run dashboard (`uv run python dashboard_api/server.py`), then `curl http://localhost:8010/openapi.json > frontend/openapi.json` (or use a script). Run this before `pnpm run generate:api`.
  - **Option B:** Configure Orval `input.target` to `http://localhost:8010/openapi.json` (requires API running at generate time).

### 3.2 Spec completeness

The dashboard API already implements:

- `GET /api/status`, `POST /api/telemetry/log`, `POST /api/verify`, `GET /api/verify/stream`
- `GET /api/artifacts`, `GET /api/artifacts/{path}`, `GET /api/benchmark/stream`
- `GET /api/models`, `POST /api/system/fix`, `GET /api/diagnostics/models`
- `GET /api/docker`, `POST /api/docker/{id}/{action}`, `GET /api/logs/{name}`, `GET /api/logs/{name}/stream`
- `GET /api/agents`, `GET /api/agents/{name}/metadata`, `GET /api/agents/{name}`, `GET /api/agents/{domain}/{name}`
- `GET /api/skills`, `GET /api/skills/{name}`
- `GET /api/usage`, etc.

Ensure FastAPI exposes all of these in `/openapi.json` (it does by default). Remove or ignore `frontend/openapi.json` if it’s stale; replace with the exported spec from the running app.

**Tags (for Orval `tags-split`):** The `usage` router uses `tags=["usage"]`. Add `tags=["docker"]`, `tags=["agents"]`, `tags=["system"]` to the other routers so generated code is split into `docker`, `agents`, `system`, `usage` modules. If you skip this, Orval may put everything in a single default tag.

### 3.3 Optional backend tweaks

- **Verify stream:** Frontend sends `?test_name=`. Backend doesn’t use it. Either add `test_name` query param to `GET /api/verify/stream` and document in OpenAPI, or stop sending it.
- **Chat / Generator:** Dashboard has **no** `/api/chat/*` or `/api/generate/*`. Either:
  - **A)** Add those routes to the dashboard API, document in OpenAPI, and include in codegen; or  
  - **B)** Drop GeneratorView (and any generate UI) for the initial rewrite, and reintroduce when a dedicated service exists.

Recommendation: **Phase 1 scopes the rewrite to the existing dashboard API only.** Omit chat/generate from the first release unless you add them to the backend.

---

## 4. Phase 2: Orval Setup & Codegen

### 4.1 Dependencies

```bash
cd frontend
pnpm add orval @orval/zod
# Keep: axios, @tanstack/react-query, zod, existing UI deps
```

### 4.2 Orval config

- **Input:** `./openapi.json` (or `http://localhost:8010/openapi.json` if API always up during generate).
- **Output:**
  - **Client:** `react-query` with `httpClient: 'axios'`.
  - **Schemas:** Separate folder (e.g. `src/api/generated/model`).
  - **Zod:** Use `@orval/zod`; generate Zod schemas (e.g. `*.zod.ts`) for request/response validation.
- **Mode:** `tags-split` to group by OpenAPI tags (docker, agents, system, usage, etc.).
- **Base URL:** `''` or `/api`; actual base URL handled by **mutator** (see below).
- **Mutator:** Point to `src/api/mutator.ts` (custom Axios instance).

### 4.3 Mutator (custom Axios instance)

- Create `src/api/mutator.ts`.
- Export an Axios instance with:
  - `baseURL`: `import.meta.env.VITE_API_BASE_URL || '/api'` (dev proxy sends `/api` → `http://localhost:8010`; preview/prod can override).
  - `timeout`: from `VITE_API_TIMEOUT` or default (e.g. 30s).
  - **Interceptors:**
    - Response: unwrap `response.data?.data` if present, else `response.data`; on error, reject with a consistent `Error` (e.g. `detail` or `message`).
  - **Retries:** Optional retry logic (exponential backoff) for 408, 429, 5xx, or use a small retry wrapper around the mutator.
- Orval’s generated client will use this mutator for all requests.

### 4.4 Scripts

- `generate:api`: run Orval (e.g. `orval` or `pnpm exec orval`).
- Add `generate:api` to `package.json` scripts. Optionally add `prebuild` or a CI step to ensure spec is exported and generation runs.

### 4.5 Generated output

- **Endpoints:** Typed functions + React Query hooks (`useGetDockerStats`, `useListAgents`, etc.).
- **Models:** TypeScript types matching Pydantic models.
- **Zod:** Schemas for validating request bodies and responses where needed.

Do **not** commit generated files to Git if you prefer to generate in CI; otherwise, commit them so the app builds without running the API. Document the workflow in the README.

---

## 5. Phase 3: Remove Old API Layer & Wire UI

### 5.1 Delete

- `frontend/src/api/client.ts`
- `frontend/src/api/schemas.ts`

### 5.2 Replace usage

- **Queries:** Replace `apiClient.getDockerStats()` etc. with generated hooks, e.g. `useGetDockerStats()`.
- **Mutations:** Replace `apiClient.controlContainer(...)` etc. with generated mutation hooks.
- **Streaming:** Endpoints like `GET /api/logs/{name}/stream`, `GET /api/verify/stream`, `GET /api/benchmark/stream` return SSE or streaming responses. Orval generates typed fetchers; use them with `fetch` or a small streaming helper if the generated client doesn’t handle streams nicely. **Fix:** Use `/api/logs/{name}/stream` (not `/logs/{id}`) for log streaming.
- **Telemetry:** `POST /api/telemetry/log` — use generated mutation. Keep “log on error” behavior in `ErrorBoundary` or a shared hook.

### 5.3 Components to update

- `StatusPanel`, `DockerMonitor`, `InfrastructureView`, `LogsView`, `LogViewer`
- `SystemOperations`, `VerificationRunner`, `BenchmarkRunner`
- `AgentsView`, `ModelsView`, `SkillsView`, `ArtifactsView`, `UsageView`
- `GeneratorView`: remove or replace with a stub if chat/generate are dropped for now.
- `ErrorBoundary`: use generated telemetry mutation.

Update imports to use `@/api/generated/...` or whatever path Orval uses. Remove all imports of the old `apiClient` and `schemas`.

---

## 6. Phase 4: App Structure & UX

### 6.1 Routing

- **Option A (simplest):** Keep the current tab-based navigation in `App.tsx` (no React Router). Easiest drop-in.
- **Option B:** Add **React Router** and use routes like `/`, `/infrastructure`, `/agents`, `/models`, etc. Better for deep-linking and “industry standard” SPA structure.

Recommendation: **Option B** if you want a clean, scalable structure; **Option A** if you prefer minimal change.

### 6.2 Structure

- **Layout:** Keep the existing sidebar + main content layout if you like it; only replace data fetching and types.
- **Styling:** Keep Tailwind, `index.css`, and existing design tokens. No need to redo visuals unless you want a separate “visual refresh” phase.

### 6.3 Entrypoint

- Fix `index.html`: change `src="/src/main.jsx"` to `src="/src/main.tsx"` so it matches the real entry.

---

## 7. Phase 5: Testing & Quality

### 7.1 Unit / integration tests

- **Vitest + React Testing Library:** Keep; update tests to mock the **generated** API layer (e.g. MSW or vi.mock of the generated hooks/fetchers).
- **Orval MSW mocks:** Orval can generate MSW handlers. Use them in tests to avoid hitting the real API.

### 7.2 E2E

- **Playwright:** Keep `playwright.config.ts` and `playwright.docker.config.ts`. E2E runs against the real dashboard API (via proxy or deployed backend). No change to architecture; only update selectors if UI changes.

### 7.3 Linting & type-check

- **ESLint, TypeScript:** Keep. Ensure `tsconfig` includes `src/api/generated`. Fix any new lint issues from generated code (or adjust generator config).

---

## 8. Automation & CI

### 8.1 API spec export

- Add a small script (e.g. `scripts/export-openapi.sh` or `scripts/export-openapi.ps1`) that:
  1. Starts the dashboard API (or waits for it).
  2. Fetches `http://localhost:8010/openapi.json` and writes `frontend/openapi.json`.
- Run this before `pnpm run generate:api` when regenerating the client.

### 8.2 CI

- **Build:** Run `export-openapi` → `generate:api` → `pnpm build` (or equivalent). Fail if any step fails.
- **Optional:** Check that `openapi.json` and generated files are up to date (e.g. `generate:api` + `git diff --exit-code`).

---

## 9. Makefile & Docs

### 9.1 Makefile

- Ensure `frontend-build` still runs `pnpm build` (which assumes `generate:api` has run or generated files are committed).
- Add `frontend-generate-api` if you want an explicit target for codegen.
- `make dev` instructions: run dashboard API + `cd frontend && pnpm dev`. Document that `generate:api` may be needed after pulling or after API changes.

### 9.2 README

- **Frontend section:** Explain that the API layer is generated from OpenAPI via Orval. Document:
  - How to export the spec.
  - How to run `pnpm run generate:api`.
  - That generated files live under `src/api/generated/` and must not be edited manually.

---

## 10. Summary Checklist

| Step | Action |
|------|--------|
| 1 | Use dashboard API as OpenAPI source; export `openapi.json` (script or manual). |
| 2 | Add Orval + `@orval/zod`; add `orval.config.ts` and `generate:api` script. |
| 3 | Implement `src/api/mutator.ts` (Axios instance, base URL, retries, error handling). |
| 4 | Run `generate:api`; verify generated endpoints, models, and Zod schemas. |
| 5 | Delete `src/api/client.ts` and `src/api/schemas.ts`. |
| 6 | Update all components to use generated hooks/fetchers; fix log stream URL to `/logs/{id}/stream`. |
| 7 | Fix `index.html` entry to `main.tsx`. |
| 8 | (Optional) Add React Router and routes. |
| 9 | Update tests to mock generated API; ensure E2E still passes. |
| 10 | Add export-openapi + generate steps to CI/docs; update Makefile. |

---

## 11. Out of Scope (For Later)

- **Chat / Generator:** Reintroduce when backend exposes `/api/chat/*` and/or `/api/generate/*` and they’re in the OpenAPI spec.
- **Visual redesign:** This plan focuses on API layer and structure; keep current UI unless you explicitly decide to redo it.
- **Auth:** No change to auth in this plan; add later if required.

---

## 12. References

- [Orval](https://orval.dev/) — OpenAPI → TS client, React Query, Zod.
- [Orval – Client with Zod](https://orval.dev/guides/client-with-zod) — SWR/React Query + Zod.
- [Orval – Custom Axios](https://orval.dev/guides/custom-axios) — Mutator / custom instance.
- [Orval – React Query](https://orval.dev/guides/react-query) — Hooks, options, invalidation.

---

## Appendix A: Orval config sketch

```ts
// orval.config.ts
import { defineConfig } from 'orval';

export default defineConfig({
  dashboard: {
    input: {
      target: './openapi.json',
      // or: target: 'http://localhost:8010/openapi.json',
    },
    output: {
      mode: 'tags-split',
      client: 'react-query',
      httpClient: 'axios',
      target: 'src/api/generated/endpoints',
      schemas: 'src/api/generated/model',
      baseUrl: '',
      override: {
        mutator: {
          path: 'src/api/mutator.ts',
          name: 'customInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
        },
      },
    },
  },
  dashboardZod: {
    input: { target: './openapi.json' },
    output: {
      mode: 'tags-split',
      client: 'zod',
      target: 'src/api/generated/endpoints',
      fileExtension: '.zod.ts',
    },
  },
});
```

Run both `dashboard` and `dashboardZod` (two outputs in one config, or split into two configs). Adjust paths and naming to match your layout. See Orval “Client with Zod” for minimal duplication between client and Zod configs.
