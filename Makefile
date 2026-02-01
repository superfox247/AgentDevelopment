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
	type-check type-check-backend type-check-frontend \
	playground playground-base playground-researcher

# ==============================================================================
# Help
# ==============================================================================

help:
	@echo "=============================================================================="
	@echo "Antigravity Agent Platform - Available Commands"
	@echo "=============================================================================="
	@echo ""
	@echo "📦 Installation & Setup:"
	@echo "  make install              Install all dependencies (uv + frontend)"
	@echo ""
	@echo "🔍 Understanding Phase (understanding subagent):"
	@echo "  make dev-health           Check service health and status"
	@echo "  make dev-logs-recent      View recent logs from all services"
	@echo ""
	@echo "💻 Development Phase (development subagent):"
	@echo "  make dev-up               Start Docker dev stack"
	@echo "  make dev-down             Stop Docker dev stack"
	@echo "  make dev-build            Build Docker services"
	@echo ""
	@echo "✅ Code Quality Phase (code-quality subagent):"
	@echo "  make lint                 Backend: ruff check + format"
	@echo "  make frontend-lint        Frontend: ESLint"
	@echo "  make type-check           Run all type checks (backend + frontend)"
	@echo "  make type-check-backend   Backend: mypy"
	@echo "  make type-check-frontend  Frontend: TypeScript compiler"
	@echo ""
	@echo "🧪 Testing Phase (testing subagent):"
	@echo "  make test                 Run all tests (smart order)"
	@echo "  make test-fast            Run unit tests (skip evals, faster)"
	@echo "  make test-agent AGENT=name Run tests for specific agent"
	@echo "  make test-pytest          Run pytest directly (legacy)"
	@echo "  make frontend-test        Frontend component tests"
	@echo "  make frontend-e2e-docker  E2E tests against Docker stack"
	@echo ""
	@echo "✓ Verification Phase (verification subagent):"
	@echo "  make dev-reset            Full reset (stop, remove volumes, rebuild, start)"
	@echo "  make dev-verify           Complete verification (lint, build, test, e2e)"
	@echo "  make verify               System verification (containers, tests, lint)"
	@echo ""
	@echo "🐳 Docker/Dev Environment:"
	@echo "  make dev-up               Start dev stack"
	@echo "  make dev-down             Stop dev stack"
	@echo "  make dev-reset            Full reset (nuclear option)"
	@echo "  make dev-health           Check service health"
	@echo "  make dev-logs             Follow logs from all services"
	@echo "  make dev-logs-recent      Recent logs (last 50 lines)"
	@echo "  make dev-logs-service SERVICE=name  Follow logs for specific service"
	@echo "  make dev-logs-service-recent SERVICE=name  Recent logs for service"
	@echo "  make dev-build            Build Docker services"
	@echo "  make dev-up-adk           Start ADK web UI (all_agents container)"
	@echo "  make dev-wait-health      Wait for services to be healthy"
	@echo ""
	@echo "🎨 Frontend Commands:"
	@echo "  make frontend-lint        Lint frontend code"
	@echo "  make frontend-build       Build frontend"
	@echo "  make frontend-test        Run component tests"
	@echo "  make frontend-e2e-docker  Run E2E tests"
	@echo ""
	@echo "🤖 Agent/ADK Commands:"
	@echo "  make playground-base      Start ADK web for base_agent (port 8501)"
	@echo "  make playground-researcher Start ADK web for researcher_agent (port 8501)"
	@echo ""
	@echo "🧹 Utility Commands:"
	@echo "  make clean                Clean build artifacts and caches"
	@echo "  make build                Build everything (uv sync + Docker + frontend)"
	@echo "  make start                Start platform (Docker containers)"
	@echo "  make stop                 Stop platform"
	@echo "  make reset                Full system reset"
	@echo ""
	@echo "=============================================================================="

# ==============================================================================
# Installation & Setup
# ==============================================================================

install:
	@echo "📦 Installing dependencies..."
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv sync --dev
	cd frontend && pnpm install
	@echo "✅ Installation complete."

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
type-check: type-check-backend type-check-frontend
	@echo "✅ All type checks complete."

# Type check backend
type-check-backend:
	@echo "🔍 Running backend type checking (mypy)..."
	uv run mypy .
	@echo "✅ Backend type checking complete."

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
# Utility Commands
# ==============================================================================
# General utility commands

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
