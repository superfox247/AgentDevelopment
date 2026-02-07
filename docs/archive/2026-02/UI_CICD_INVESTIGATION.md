# UI CI/CD Investigation Report

Date: 2026-02-06
Scope: Reproduce UI pipeline status, get UI running locally, verify key UI checks, and identify blockers.

## What was verified

### UI runs locally
- Installed dependencies successfully with `make install`.
- Started Vite dev server with `pnpm dev --host 0.0.0.0 --port 4173`.
- Confirmed server readiness and HTTP 200 response at `http://127.0.0.1:4173/`.
- Verified page render using Playwright automation (`title=dashboard`) and captured screenshot artifact (`artifacts/ui-home.png`).

### Frontend quality/build/tests
- `make frontend-lint` passed.
- `make type-check-frontend` passed.
- `make frontend-build` passed.
- `make frontend-test` (Vitest component tests) passed.

## Reproduced issues

### 1) Docker-dependent verification cannot run in this environment
- `make dev-up` fails because Docker CLI is unavailable (`make: docker: No such file or directory`).
- Any CI step depending on Docker Compose or `make frontend-e2e-docker` will fail in an environment missing Docker.

### 2) E2E tests initially failed due to missing Playwright browsers
- `pnpm test:e2e` first failed with missing Chromium executable (`playwright install` required).

### 3) E2E tests still fail due to missing OS shared libraries
- After installing Playwright Chromium, `pnpm test:e2e` fails to launch browser:
  - Missing `libatk-1.0.so.0` (and likely related GTK/X11 runtime dependencies).
- This indicates CI runners (or this environment) need Playwright system deps installed.

### 4) Non-blocking warning noise
- Repeated warning during E2E run: `NO_COLOR is ignored due to FORCE_COLOR`.
- Not a functional blocker, but adds noise to logs.

## Recommended investigation and fix plan

### Phase 1: Stabilize CI runtime prerequisites
1. Ensure CI images include Docker when running docker-compose based jobs, or split jobs so non-Docker checks can still run.
2. For Playwright jobs, explicitly install browsers and system dependencies:
   - `pnpm exec playwright install --with-deps chromium` (or distro-specific apt packages).
3. Add a preflight check step to fail fast with actionable errors when Docker or required libs are missing.

### Phase 2: Harden frontend verification strategy
1. Keep `frontend-lint`, `type-check-frontend`, `frontend-build`, and `frontend-test` as required fast checks.
2. Separate E2E into:
   - lightweight smoke E2E against Vite app;
   - full-stack E2E against docker stack.
3. Mark full-stack E2E as required only on runners that satisfy Docker + browser deps.

### Phase 3: Improve observability and triage speed
1. Add a CI artifact upload for Playwright traces/screenshots/videos on failure.
2. Add a short troubleshooting doc section for common runner issues (missing Docker, missing Playwright libs).
3. Normalize color env flags (`FORCE_COLOR`/`NO_COLOR`) to reduce warning noise.

## Immediate next actions
1. Update CI workflow to install Playwright dependencies in E2E jobs.
2. Validate E2E pass on a runner with required system libraries.
3. Re-run full pipeline and compare against this baseline report.
