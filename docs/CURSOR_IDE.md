# Using Antigravity in Cursor IDE

This guide helps you run the project and verify UIs **inside Cursor**.

## Quick verification

1. **Open Terminal** in Cursor (`Ctrl+`` ` or **Terminal → New Terminal**).
2. **Install** (from repo root):
   ```powershell
   uv sync --dev
   cd frontend && pnpm install && cd ..
   ```
3. **Run dashboard** (two terminals):
   - **Terminal 1 – API**: `uv run python dashboard_api/server.py` (port 8010)
   - **Terminal 2 – UI**: `cd frontend && pnpm dev` (port 5173)
4. **Open** [http://localhost:5173](http://localhost:5173) in your browser.

## VS Code / Cursor tasks

Use **Terminal → Run Task** (or `Ctrl+Shift+P` → “Tasks: Run Task”):

| Task | What it does |
|------|----------------|
| **Install (backend + frontend)** | `uv sync --dev` at root |
| **Install frontend** | `pnpm install` in `frontend/` |
| **Frontend: dev** | `pnpm dev` (Vite) – keep running |
| **Dashboard API (FastAPI)** | `uv run python dashboard_api/server.py` – keep running |
| **Lint** / **Lint frontend** | Ruff + ESLint |
| **Test backend** / **Test frontend** | pytest + Vitest |
| **Verify (Cursor)** | Runs lint + tests |

For the full dashboard:

1. Run **Dashboard API (FastAPI)**.
2. Run **Frontend: dev**.
3. Open [http://localhost:5173](http://localhost:5173).

## Frontend config (Vite + esbuild)

The project uses:

- **`vite.config.js`** with **`--configLoader native`** so Vite loads config without bundling it via esbuild (avoids config-load issues on some setups).
- **`onlyBuiltDependencies: ["esbuild"]`** in `frontend/package.json` so pnpm runs esbuild’s postinstall and installs the native binary.

If you see **`spawn EPERM`** or **“Cannot find module 'debug'”**:

1. **Clean reinstall**:
   ```powershell
   cd frontend
   Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
   Remove-Item -Force pnpm-lock.yaml -ErrorAction SilentlyContinue
   pnpm install
   ```
2. Run **`pnpm dev`** from Cursor’s **integrated terminal** (not via an automated runner that might restrict `child_process`).
3. On Windows, exclude the project folder from **Windows Defender** real-time scanning if you suspect it’s blocking `esbuild.exe`.

## Backend (Python)

- Use **`uv`** for installs and runs: `uv sync --dev`, `uv run pytest`, `uv run python dashboard_api/server.py`.
- If `uv sync` fails (e.g. network), retry or use a VPN; the lockfile is committed.

## Summary

| Step | Command |
|------|---------|
| Backend deps | `uv sync --dev` |
| Frontend deps | `cd frontend && pnpm install` |
| Dashboard API | `uv run python dashboard_api/server.py` |
| Dashboard UI | `cd frontend && pnpm dev` |
| Lint + test | **Terminal → Run Task** → **Verify (Cursor)** |

Run **Verify (Cursor)** and the dev tasks from Cursor’s **integrated terminal** (not an automated runner). Once the API and frontend are running, open [http://localhost:5173](http://localhost:5173); the UI proxies `/api` to the FastAPI server.
