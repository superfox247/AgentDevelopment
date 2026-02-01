# Dashboard (Baseline)

Minimal React + Vite SPA to **chat with agents** (Researcher, Customer Service). No Docker UI, agent lists, models, skills, artifacts, or usage views.

## Structure

- `src/components/`: `ChatView` (agent selector + chat), `ErrorBoundary`
- `src/api/client.ts`: Baseline API client (chat stream only)
- `src/App.tsx`: Single-page layout

## Run

1. **Install**: `pnpm install`
2. **Dev**: Dashboard API at repo root → `uv run python dashboard_api/server.py` (port 8010). Then `pnpm dev` (port 5173, proxies `/api` to 8010).
3. Open `http://localhost:5173`.

## Scripts

- `pnpm dev` – dev server
- `pnpm build` – production build
- `pnpm test` – Vitest (unit/component)
- `pnpm test:e2e` – Playwright E2E (`tests/e2e/`)

## Notes

- Chat requires `POST /api/chat/{agent}` on the dashboard API. See [DASHBOARD_BASELINE](../docs/DASHBOARD_BASELINE.md) and [FRONTEND_REWRITE_PLAN](../docs/FRONTEND_REWRITE_PLAN.md).
