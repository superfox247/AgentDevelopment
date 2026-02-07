# Configuration Files Guide

This document describes all configuration files in the codebase and their purposes.

## Root Level Config Files

### Python Project Configuration
- **`pyproject.toml`** - Main workspace configuration for Python dependencies, tooling (ruff, mypy, pytest), and build settings
- **`pytest.ini`** - Pytest-specific configuration (test paths, environment variables, warnings)
- **`uv.lock`** - Lock file for root workspace dependencies (managed by `uv`)

### Docker & Infrastructure
- **`docker-compose.yml`** - Docker services configuration (agents, phoenix, etc.)
- **`.dockerignore`** - Files to exclude from Docker builds

### Git & CI/CD
- **`.gitignore`** - Files and patterns to exclude from version control
- **`.pre-commit-config.yaml`** - Pre-commit hooks configuration
- **`.github/workflows/ci.yml`** - GitHub Actions CI/CD pipeline

### Environment
- **`.env`** (root) - Non-secret config only (e.g. `GOOGLE_GENAI_USE_VERTEXAI`). Do not store API keys here.
- **`.env.example`** (root) - Template for `.env`. Use system environment (e.g. Windows `GEMINI_API_KEY`) for secrets.
- **`frontend/.env`** - Frontend-specific environment variables

## Agent Platform Config

### `agent_platform/pyproject.toml`
- Package configuration for the shared platform layer
- Dependencies for observability, ADK, FastAPI
- Build configuration

### `agent_platform/uv.lock`
- Lock file for agent_platform package dependencies

### `agent_platform/Dockerfile.agent`
- Universal Dockerfile for building agent containers
- Used by docker-compose.yml with `AGENT_PATH` build arg

## Frontend Config

### TypeScript & Build
- **`frontend/tsconfig.json`** - TypeScript compiler configuration for source
- **`frontend/tsconfig.node.json`** - TypeScript config for Node.js tooling (vite, etc.)
- **`frontend/vite.config.ts`** - Vite build tool configuration (dev server, proxy, plugins)
- **`frontend/vitest.config.ts`** - Vitest test runner configuration

### Package Management
- **`frontend/package.json`** - Node.js dependencies and scripts
- **`frontend/pnpm-lock.yaml`** - Lock file for pnpm package manager

### Testing
- **`frontend/playwright.config.ts`** - Playwright E2E test configuration
- **`frontend/eslint.config.ts`** - ESLint linting rules

## Agent Config Files

### Agent Structure
Each agent in `agents/<agent_name>/` may have:
- **`agent.py`** - ADK agent definition with `root_agent` (model, tools, instructions)
- **`.env.example`** - Example environment variables template
- **`evaluations/test_config.json`** - Agent-specific evaluation configuration

## Configuration Best Practices

1. **Environment Variables**: Set `GEMINI_API_KEY` in **Windows** (User or System). **`.\make.ps1`** loads it automatically for Docker and ADK. Use `.env` only for non-secret config; use `.env.example` as a template.
2. **Lock Files**: Always commit lock files (`uv.lock`, `pnpm-lock.yaml`) for reproducible builds
3. **Config Consolidation**: Prefer `pyproject.toml` over separate config files when possible
4. **Agent Configs**: Keep agent-specific configs collocated with the agent code

## Notes

- **Duplicate Configs Removed**: `vite.config.js` and `vitest.config.js` were removed (use `.ts` versions)
- **Old Paths Cleaned**: References to `domains/` and `schemas/` directories have been removed
- **Multiple pyproject.toml**: Root and `agent_platform/` both have `pyproject.toml` - this is intentional (workspace vs package)
