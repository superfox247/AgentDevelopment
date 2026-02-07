# ==============================================================================
# Antigravity Agent Platform - Developer Commands
# ==============================================================================
# Organized by Subagent Workflow Phases
# Run any command with: make <target>
# Example: make test, make dev-up, make verify
# ==============================================================================

.PHONY: help install test lint build start stop reset verify clean \
	dev-reset dev-up dev-up-adk dev-down dev-health dev-logs dev-logs-recent \
	dev-logs-service dev-logs-service-recent dev-build dev-verify dev-wait-health \
	frontend-lint frontend-build frontend-test frontend-e2e-docker \
	test-fast test-agent test-pytest \
	type-check type-check-fast type-check-full type-check-backend type-check-frontend \
	playground playground-base playground-researcher codex-preflight codex-preflight-full \
	gcp-bootstrap gcp-setup-wif gcp-configure-github docs-generate docs-check command-catalog-check

ifeq ($(OS),Windows_NT)
GCP_BOOTSTRAP_CMD = powershell -ExecutionPolicy Bypass -File .\infra\gcp\bootstrap.ps1 -ProjectId "$(PROJECT)" -Region "$(if $(REGION),$(REGION),us-central1)" -ArtifactLocation "$(if $(ARTIFACT_LOCATION),$(ARTIFACT_LOCATION),us)" -ArtifactRepository "$(if $(ARTIFACT_REPO),$(ARTIFACT_REPO),antigravity)" -PipelineName "$(if $(PIPELINE),$(PIPELINE),dashboard-api)" -StagingService "$(if $(STAGING_SERVICE),$(STAGING_SERVICE),dashboard-api-staging)" -ProductionService "$(if $(PRODUCTION_SERVICE),$(PRODUCTION_SERVICE),dashboard-api-production)"
GCP_SETUP_WIF_CMD = powershell -ExecutionPolicy Bypass -File .\infra\gcp\setup_wif.ps1 -ProjectId "$(PROJECT)" -Repo "$(REPO)" -PoolId "$(if $(POOL),$(POOL),github-pool)" -ProviderId "$(if $(PROVIDER),$(PROVIDER),github-provider)" -ServiceAccountId "$(if $(SERVICE_ACCOUNT),$(SERVICE_ACCOUNT),github-actions-cicd)"
GCP_CONFIGURE_GITHUB_CMD = powershell -ExecutionPolicy Bypass -File .\infra\gcp\configure_github.ps1 -Repo "$(REPO)" -ProjectId "$(PROJECT)" -Region "$(if $(REGION),$(REGION),us-central1)" -ArtifactHost "$(if $(ARTIFACT_HOST),$(ARTIFACT_HOST),us-docker.pkg.dev)" -ArtifactRepo "$(if $(ARTIFACT_REPO),$(ARTIFACT_REPO),antigravity)" -ImageName "$(if $(IMAGE_NAME),$(IMAGE_NAME),dashboard-api)" -Pipeline "$(if $(PIPELINE),$(PIPELINE),dashboard-api)" -StagingService "$(if $(STAGING_SERVICE),$(STAGING_SERVICE),dashboard-api-staging)" -ProductionService "$(if $(PRODUCTION_SERVICE),$(PRODUCTION_SERVICE),dashboard-api-production)" -WifProvider "$(WIF_PROVIDER)" -ServiceAccount "$(SERVICE_ACCOUNT_EMAIL)"
else
GCP_BOOTSTRAP_CMD = bash infra/gcp/bootstrap.sh --project "$(PROJECT)" --region "$(if $(REGION),$(REGION),us-central1)" --artifact-location "$(if $(ARTIFACT_LOCATION),$(ARTIFACT_LOCATION),us)" --artifact-repo "$(if $(ARTIFACT_REPO),$(ARTIFACT_REPO),antigravity)" --pipeline "$(if $(PIPELINE),$(PIPELINE),dashboard-api)" --staging-service "$(if $(STAGING_SERVICE),$(STAGING_SERVICE),dashboard-api-staging)" --production-service "$(if $(PRODUCTION_SERVICE),$(PRODUCTION_SERVICE),dashboard-api-production)"
GCP_SETUP_WIF_CMD = bash infra/gcp/setup_wif.sh --project "$(PROJECT)" --repo "$(REPO)" --pool "$(if $(POOL),$(POOL),github-pool)" --provider "$(if $(PROVIDER),$(PROVIDER),github-provider)" --service-account "$(if $(SERVICE_ACCOUNT),$(SERVICE_ACCOUNT),github-actions-cicd)"
GCP_CONFIGURE_GITHUB_CMD = bash infra/gcp/configure_github.sh --repo "$(REPO)" --project "$(PROJECT)" --region "$(if $(REGION),$(REGION),us-central1)" --artifact-host "$(if $(ARTIFACT_HOST),$(ARTIFACT_HOST),us-docker.pkg.dev)" --artifact-repo "$(if $(ARTIFACT_REPO),$(ARTIFACT_REPO),antigravity)" --image-name "$(if $(IMAGE_NAME),$(IMAGE_NAME),dashboard-api)" --pipeline "$(if $(PIPELINE),$(PIPELINE),dashboard-api)" --staging-service "$(if $(STAGING_SERVICE),$(STAGING_SERVICE),dashboard-api-staging)" --production-service "$(if $(PRODUCTION_SERVICE),$(PRODUCTION_SERVICE),dashboard-api-production)" $(if $(WIF_PROVIDER),--wif-provider "$(WIF_PROVIDER)") $(if $(SERVICE_ACCOUNT_EMAIL),--service-account "$(SERVICE_ACCOUNT_EMAIL)")
endif

# ==============================================================================
# Help
# ==============================================================================

help:
	@python scripts/render_command_help.py --shell make

# ==============================================================================
# Installation & Setup
# ==============================================================================

install:
	@echo "📦 Installing dependencies..."
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv sync --dev
	cd frontend && pnpm install
	@echo "✅ Installation complete."

codex-preflight:
	@echo "🧭 Running Codex preflight checks..."
	@bash scripts/codex_preflight.sh

# Strict preflight for full-stack development (Docker + Playwright required)
codex-preflight-full:
	@echo "🧭 Running strict Codex preflight checks for full dev..."
	@bash scripts/codex_preflight.sh --require-docker --require-playwright

# ==============================================================================
# Understanding Phase Commands (understanding subagent)
# ==============================================================================
# Commands for exploring and understanding the codebase state

# Check service health and status
dev-health:
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "Docker Containers:"
	@docker compose ps
	@echo ""
	@uv run python scripts/health_check.py

# View recent logs from all services
dev-logs-recent:
	@echo "📋 Recent logs from all services (last 50 lines):"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@docker compose logs --tail=50
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "💡 For live logs, run: make dev-logs"

# ==============================================================================
# Development Phase Commands (development subagent)
# ==============================================================================
# Commands for development work

# Start full dev stack (Docker containers + dashboard)
# Note: This starts Docker containers. You still need to run API and frontend separately:
# Terminal 1: uv run python dashboard_api/server.py
# Terminal 2: cd frontend && pnpm dev
dev-up:
	@echo "🚀 Starting dev stack..."
	docker compose up -d
	@echo "📋 Container status:"
	@docker compose ps
	@echo ""
	@echo "⏳ Waiting for services to be healthy..."
	@$(MAKE) dev-wait-health
	@echo ""
	@echo "📋 Final container status:"
	@docker compose ps
	@echo ""
	@echo "✅ Docker services started."
	@echo "📝 Next steps:"
	@echo "   Terminal 1: uv run python dashboard_api/server.py"
	@echo "   Terminal 2: cd frontend && pnpm dev"

# Stop dev stack
dev-down:
	@echo "🛑 Stopping dev stack..."
	docker compose down
	@echo "✅ Dev stack stopped."

# Build all Docker services
dev-build:
	@echo "🔨 Building Docker services..."
	docker compose build
	@echo "✅ Build complete."

# ==============================================================================
# Code Quality Phase Commands (code-quality subagent)
# ==============================================================================
# Commands for code quality checks

# Run linting and formatting (backend)
lint:
	@echo "🔍 Running backend linting..."
	uv run ruff check . --fix
	uv run ruff format .
	@echo "✅ Backend linting complete."

# Lint frontend
frontend-lint:
	@echo "🔍 Running frontend linting..."
	cd frontend && pnpm lint
	@echo "✅ Frontend linting complete."

# Run all type checks (backend + frontend)
type-check: type-check-fast type-check-frontend
	@echo "✅ All type checks complete."

# Type check backend (fast scope, aligned with CI)
type-check-fast:
	@echo "🔍 Running backend type checking (mypy, fast scope)..."
	uv run mypy dashboard_api
	@echo "✅ Backend fast type checking complete."

# Type check backend (full repo scope)
type-check-full:
	@echo "🔍 Running backend type checking (mypy, full scope)..."
	uv run mypy .
	@echo "✅ Backend full type checking complete."

# Backward-compatible backend target
type-check-backend: type-check-fast

# Type check frontend
type-check-frontend:
	@echo "🔍 Running frontend type checking (TypeScript)..."
	cd frontend && pnpm exec tsc --noEmit
	@echo "✅ Frontend type checking complete."

# Build frontend (for verification)
frontend-build:
	@echo "🔨 Building frontend..."
	cd frontend && pnpm build
	@echo "✅ Frontend build complete."

# ==============================================================================
# Testing Phase Commands (testing subagent)
# ==============================================================================
# Commands for running tests

# Run all tests (smart order, exits on failure)
test:
	@echo "🧪 Running all tests..."
	python run_tests.py

# Run all tests without evaluations (faster, no API keys needed)
test-fast:
	@echo "🧪 Running unit tests (skip evals)..."
	python run_tests.py --skip-evals

# Run all tests for a specific agent
test-agent:
	@if [ -z "$(AGENT)" ]; then \
		echo "Usage: make test-agent AGENT=researcher_agent"; \
		exit 1; \
	fi
	@echo "🧪 Running tests for agent: $(AGENT)"
	python run_tests.py --agent $(AGENT)

# Run all tests with pytest directly (legacy)
test-pytest:
	@echo "🧪 Running pytest..."
	uv run pytest

# Run frontend component tests
frontend-test:
	@echo "🧪 Running frontend component tests..."
	cd frontend && pnpm test run
	@echo "✅ Frontend tests complete."

# Run e2e tests against Docker stack (requires dev stack to be running)
frontend-e2e-docker:
	@echo "🧪 Running e2e tests against Docker stack..."
	@echo "⚠️  Ensure dev stack is running: make dev-up"
	cd frontend && pnpm exec playwright test --config=playwright.docker.config.ts
	@echo "✅ E2E tests complete."

# ==============================================================================
# Verification Phase Commands (verification subagent)
# ==============================================================================
# Commands for verifying completed work

# Reset dev environment: stop, remove volumes, rebuild, and start
dev-reset:
	@echo "🔥 Resetting dev environment..."
	docker compose down -v --remove-orphans
	@echo "🔨 Building Docker services (this may take a while)..."
	docker compose build --no-cache
	@echo "🚀 Starting containers..."
	docker compose up -d
	@echo "📋 Container status:"
	@docker compose ps
	@echo ""
	@echo "⏳ Waiting for services to be healthy..."
	@$(MAKE) dev-wait-health
	@echo ""
	@echo "📋 Final container status:"
	@docker compose ps
	@echo ""
	@echo "✅ Dev environment reset complete."

# Full dev verification: lint, build, test, e2e
dev-verify:
	@echo "🔍 Running full dev verification..."
	@echo ""
	@echo "1. Linting backend..."
	@$(MAKE) lint || (echo "❌ Backend linting failed"; exit 1)
	@echo ""
	@echo "2. Linting frontend..."
	@$(MAKE) frontend-lint || (echo "❌ Frontend linting failed"; exit 1)
	@echo ""
	@echo "3. Building Docker services..."
	@$(MAKE) dev-build || (echo "❌ Docker build failed"; exit 1)
	@echo ""
	@echo "4. Starting dev stack..."
	@$(MAKE) dev-up || (echo "❌ Failed to start dev stack"; exit 1)
	@echo ""
	@echo "5. Running backend tests..."
	@$(MAKE) test-fast || (echo "❌ Backend tests failed"; exit 1)
	@echo ""
	@echo "6. Running frontend tests..."
	@$(MAKE) frontend-test || (echo "❌ Frontend tests failed"; exit 1)
	@echo ""
	@echo "7. Running e2e tests against Docker stack..."
	@$(MAKE) frontend-e2e-docker || ( \
		echo ""; \
		echo "❌ E2E tests failed. Showing recent logs:"; \
		$(MAKE) dev-logs-recent; \
		exit 1 \
	)
	@echo ""
	@echo "✅ Full verification complete!"

# Run full system verification (no agent involvement)
verify:
	@echo "=== System Verification ==="
	@echo "1. Checking containers..."
	@docker ps -a --format "table {{.Names}}\t{{.Status}}"
	@echo ""
	@echo "2. Running tests..."
	@uv run pytest -v
	@echo ""
	@echo "3. Checking lint..."
	@uv run ruff check . --fix
	@echo ""
	@echo "✅ Verification complete."

# ==============================================================================
# Docker/Dev Environment Commands
# ==============================================================================
# Commands for managing Docker containers and dev environment

# Start the platform (Docker containers + dashboard)
start:
	@echo "🚀 Starting platform..."
	docker compose up -d
	@echo "✅ Containers started. Run 'cd frontend && pnpm dev' for dashboard."

# Stop the platform
stop:
	@echo "🛑 Stopping platform..."
	docker compose down
	@echo "✅ Platform stopped."

# View logs from all services (follow mode)
dev-logs:
	@echo "📋 Following logs from all services (Ctrl+C to exit)..."
	docker compose logs -f

# View logs from a specific service
dev-logs-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Usage: make dev-logs-service SERVICE=phoenix"; \
		echo "Available services:"; \
		docker compose ps --format "table {{.Service}}"; \
		exit 1; \
	fi
	@echo "📋 Logs for service: $(SERVICE)"
	@docker compose logs -f $(SERVICE)

# View recent logs from a specific service
dev-logs-service-recent:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Usage: make dev-logs-service-recent SERVICE=phoenix"; \
		echo "Available services:"; \
		docker compose ps --format "table {{.Service}}"; \
		exit 1; \
	fi
	@echo "📋 Recent logs for service: $(SERVICE) (last 50 lines)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@docker compose logs --tail=50 $(SERVICE)
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start ADK web UI (all_agents container)
dev-up-adk:
	@echo "🚀 Starting all_agents (ADK web at http://localhost:8501)..."
	@echo "   Uses GEMINI_API_KEY from environment or .env."
	docker compose up -d --force-recreate all_agents
	@echo "✅ Done. Open http://localhost:8501 and select researcher_agent."

# Wait for services to be healthy (with timeout)
dev-wait-health:
	@echo "⏳ Waiting for services to be ready (max 120s)..."
	@uv run python scripts/health_check.py --timeout 120 || ( \
		echo ""; \
		echo "⚠️  Timeout waiting for services."; \
		echo "📋 Showing recent logs from all services:"; \
		docker compose logs --tail=50; \
		echo ""; \
		echo "💡 For live logs, run: make dev-logs"; \
		exit 1 \
	)

# ==============================================================================
# Agent/ADK Commands
# ==============================================================================
# Commands for running agents with ADK

# Start ADK Web for base_agent (no Docker required)
playground-base:
	@echo "🎮 Starting ADK Web for base_agent on port 8501 (no Docker required)."
	@echo "Set GOOGLE_API_KEY or use agents/base_agent/.env (see .env.example)."
	uv run adk web agents/base_agent --port 8501 --reload_agents

# Start ADK Web for researcher_agent (no Docker required)
playground-researcher:
	@echo "🎮 Starting ADK Web for researcher_agent on port 8501 (no Docker required)."
	uv run adk web agents/researcher_agent --port 8501 --reload_agents

# Generic playground (placeholder - update to point to orchestrator agent)
playground:
	@echo "🎮 Starting ADK Playground..."
	@echo "⚠️  Note: Update this command to point to your orchestrator agent in agents/ directory."
	@echo "Example: uv run adk web agents/<orchestrator_agent> --port 8501 --reload_agents"
	# uv run adk web agents/<orchestrator_agent> --port 8501 --reload_agents

# ==============================================================================
# GCP CI/CD Commands
# ==============================================================================

gcp-bootstrap:
	@$(GCP_BOOTSTRAP_CMD)

gcp-setup-wif:
	@$(GCP_SETUP_WIF_CMD)

gcp-configure-github:
	@$(GCP_CONFIGURE_GITHUB_CMD)

# ==============================================================================
# Utility Commands
# ==============================================================================
# General utility commands

# Generate docs from command help + API routes
docs-generate:
	@echo "📝 Generating docs artifacts..."
	uv run python scripts/generate_reference_docs.py
	@echo "✅ Generated docs artifacts updated."

# Check generated docs are up to date
docs-check:
	@echo "📝 Checking generated docs artifacts..."
	uv run python scripts/generate_reference_docs.py --check
	@echo "✅ Generated docs artifacts are up to date."

# Check shared command catalog is in sync with wrappers
command-catalog-check:
	@echo "🧭 Checking command catalog sync..."
	uv run python scripts/validate_command_catalog_sync.py
	@echo "✅ Command catalog is in sync."

# Full system reset (nuclear option)
reset:
	@echo "🔥 Full system reset starting..."
	docker compose down -v --remove-orphans
	docker compose build --no-cache
	docker compose up -d
	@echo "✅ System reset complete. All containers rebuilt and started."

# Clean up build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	docker compose down --remove-orphans
	@echo "✅ Cleaned."

# Build everything
build:
	@echo "🔨 Building project..."
	uv sync
	docker compose build
	cd frontend && pnpm install && pnpm build
	@echo "✅ Build complete."
