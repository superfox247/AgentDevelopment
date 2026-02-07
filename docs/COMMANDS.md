# Command Reference for Subagents

> **Last updated**: 2026-01-26  
> **Status**: Active

This document provides a comprehensive reference for all commands available to subagents. All commands should be executed via the Makefile (`make <target>`) for consistency.

## Quick Reference by Subagent

### Understanding Subagent
- `make dev-health` - Check service health and status
- `make dev-logs-recent` - View recent logs from all services

### Development Subagent
- `make dev-up` - Start Docker dev stack
- `make dev-down` - Stop Docker dev stack
- `make dev-build` - Build Docker services

### Code Quality Subagent
- `make lint` - Backend linting (ruff check + format)
- `make frontend-lint` - Frontend linting (ESLint)
- `make type-check` - All type checks (backend + frontend)
- `make type-check-backend` - Backend type checking (mypy)
- `make type-check-frontend` - Frontend type checking (TypeScript)
- `make frontend-build` - Build frontend (for verification)
- `make dev-build` - Build Docker services (for verification)

### Testing Subagent
- `make test` - Run all tests (smart order)
- `make test-fast` - Run unit tests (skip evals, faster)
- `make test-agent AGENT=name` - Run tests for specific agent
- `make test-pytest` - Run pytest directly (includes integration tests)
- `make frontend-test` - Frontend component tests
- `make frontend-e2e-docker` - E2E tests against Docker stack
- `make dev-up` - Start Docker stack (required for some tests)
- `make dev-health` - Verify services healthy
- `make dev-logs-recent` - Recent Docker logs
- `make dev-logs-service SERVICE=name` - Logs for specific service

### Verification Subagent
- `make dev-reset` - Full reset (stops, removes volumes, rebuilds, starts)
- `make dev-verify` - Complete verification (lint, build, test, e2e)
- `make verify` - System verification (containers, tests, lint)
- `make dev-health` - Check all services healthy
- `make frontend-e2e-docker` - Run E2E tests
- `make dev-logs-recent` - Docker logs

### Test Runner Subagent
- `make test-fast` - Unit tests
- `make test-agent AGENT=name` - Agent tests
- `make test-pytest` - Integration tests (pytest)
- `make frontend-test` - Component tests
- `make frontend-e2e-docker` - E2E tests

## Command Categories

### Installation & Setup
```bash
make install              # Install all dependencies (uv + frontend)
```

### Understanding Phase
```bash
make dev-health           # Check service health and status
make dev-logs-recent      # View recent logs from all services (last 50 lines)
```

### Development Phase
```bash
make dev-up               # Start Docker dev stack
make dev-down             # Stop Docker dev stack
make dev-build            # Build Docker services
```

### Code Quality Phase
```bash
make lint                 # Backend: ruff check + format
make frontend-lint        # Frontend: ESLint
make type-check           # All type checks (backend + frontend)
make type-check-backend   # Backend: mypy
make type-check-frontend  # Frontend: TypeScript compiler
make frontend-build       # Build frontend (for verification)
```

### Testing Phase
```bash
make test                 # Run all tests (smart order, exits on failure)
make test-fast            # Run unit tests (skip evals, faster)
make test-agent AGENT=name # Run tests for specific agent
make test-pytest          # Run pytest directly (legacy, includes integration)
make frontend-test        # Frontend component tests
make frontend-e2e-docker  # E2E tests against Docker stack
```

### Verification Phase
```bash
make dev-reset            # Full reset (stop, remove volumes, rebuild, start)
make dev-verify           # Complete verification (lint, build, test, e2e)
make verify               # System verification (containers, tests, lint)
```

### Docker/Dev Environment
```bash
make dev-up               # Start dev stack
make dev-down             # Stop dev stack
make dev-reset            # Full reset (nuclear option)
make dev-health           # Check service health
make dev-logs             # Follow logs from all services
make dev-logs-recent      # Recent logs (last 50 lines)
make dev-logs-service SERVICE=name  # Follow logs for specific service
make dev-logs-service-recent SERVICE=name  # Recent logs for service
make dev-build            # Build Docker services
make dev-up-adk           # Start ADK web UI (all_agents container)
make dev-wait-health      # Wait for services to be healthy
```

### Frontend Commands
```bash
make frontend-lint        # Lint frontend code
make frontend-build       # Build frontend
make frontend-test        # Run component tests
make frontend-e2e-docker  # Run E2E tests
```

### Agent/ADK Commands
```bash
make playground-base      # Start ADK web for base_agent (port 8501)
make playground-researcher # Start ADK web for researcher_agent (port 8501)
```

### Utility Commands
```bash
make clean                # Clean build artifacts and caches
make build                # Build everything (uv sync + Docker + frontend)
make start                # Start platform (Docker containers)
make stop                 # Stop platform
make reset                # Full system reset
make help                 # Show all available commands
```

### GCP CI/CD Commands
```bash
make gcp-bootstrap PROJECT=<gcp-project-id>  # Bootstrap APIs, Artifact Registry, Cloud Deploy
make gcp-setup-wif PROJECT=<gcp-project-id> REPO=<owner/repo>  # Configure GitHub OIDC WIF
make gcp-configure-github PROJECT=<gcp-project-id> REPO=<owner/repo>  # Set GitHub repo vars/secrets
```

PowerShell equivalents:
```powershell
.\make.ps1 gcp-bootstrap -Project <gcp-project-id>
.\make.ps1 gcp-setup-wif -Project <gcp-project-id> -Repo <owner/repo>
.\make.ps1 gcp-configure-github -Project <gcp-project-id> -Repo <owner/repo>
```

## Command Usage Examples

### Running Tests for a Specific Agent
```bash
make test-agent AGENT=researcher_agent
```

### Viewing Logs for a Specific Service
```bash
make dev-logs-service SERVICE=phoenix
make dev-logs-service-recent SERVICE=phoenix
```

### Full Development Workflow
```bash
# 1. Start environment
make dev-up

# 2. Run code quality checks
make lint
make frontend-lint
make type-check

# 3. Run tests
make test-fast
make frontend-test

# 4. Full verification
make dev-verify
```

## Notes for Subagents

1. **Always use Makefile commands**: Don't run raw commands like `docker compose` or `uv run pytest` directly. Use `make` targets instead.

2. **Command dependencies**: Some commands require others to run first:
   - `make frontend-e2e-docker` requires `make dev-up` first
   - `make dev-verify` runs a full suite of checks in order

3. **Service-specific commands**: When using `SERVICE` or `AGENT` parameters, always check available options first if unsure.

4. **Error handling**: Most Makefile commands will exit with error codes on failure. Subagents should check exit codes and handle failures appropriately.

5. **Help command**: Run `make help` to see all available commands organized by category.

## Related Documentation

- [Subagent System](SUBAGENT_SYSTEM.md) - Architecture overview
- [Development Guide](DEVELOPMENT.md) - Development workflow
- [Testing Guide](TESTING.md) - Testing strategies
- [Standards](STANDARDS.md) - Code standards and conventions

---

**Last Updated**: 2026-01-26  
**Status**: Active
