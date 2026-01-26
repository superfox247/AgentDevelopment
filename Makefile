# ==============================================================================
# Antigravity Agent Platform - Developer Commands
# ==============================================================================
# Run any command with: make <target>
# Example: make test, make reset, make verify
# ==============================================================================

.PHONY: install test lint build start stop reset verify clean playground playground-base playground-researcher \
	dev-reset dev-up dev-down dev-health dev-logs dev-logs-recent dev-logs-service dev-logs-service-recent \
	dev-build dev-verify dev-wait-health \
	frontend-lint frontend-build frontend-test frontend-e2e-docker

# ==============================================================================
# Installation & Setup
# ==============================================================================

install:
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv sync --dev
	cd frontend && pnpm install

# ==============================================================================
# Development Commands
# ==============================================================================

# Start the platform (Docker containers + dashboard)
start:
	docker compose up -d
	@echo "✅ Containers started. Run 'cd frontend && pnpm dev' for dashboard."

# Stop the platform
stop:
	docker compose down
	@echo "✅ Platform stopped."

# ==============================================================================
# Docker Development Workflow
# ==============================================================================

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

# Start full dev stack (Docker + API + Frontend)
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

# Check health of all services
dev-health:
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "Docker Containers:"
	@docker compose ps
	@echo ""
	@uv run python scripts/health_check.py

# View logs from all services (follow mode)
dev-logs:
	docker compose logs -f

# View recent logs from all services (last 50 lines)
dev-logs-recent:
	@echo "📋 Recent logs from all services (last 50 lines):"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@docker compose logs --tail=50
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "💡 For live logs, run: make dev-logs"

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

# Build all Docker services
dev-build:
	@echo "🔨 Building Docker services..."
	docker compose build
	@echo "✅ Build complete."

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

# ==============================================================================
# Testing & Verification
# ==============================================================================

# Run all tests (smart order, exits on failure)
test:
	python run_tests.py

# Run all tests for a specific agent
test-agent:
	@if [ -z "$(AGENT)" ]; then \
		echo "Usage: make test-agent AGENT=researcher_agent"; \
		exit 1; \
	fi
	python run_tests.py --agent $(AGENT)

# Run tests without evaluations (faster, no API keys needed)
test-fast:
	python run_tests.py --skip-evals

# Run all tests with pytest directly (legacy)
test-pytest:
	uv run pytest

# Run full system verification (no agent involvement)
verify:
	@echo "=== System Verification ==="
	@echo "1. Checking containers..."
	docker ps -a --format "table {{.Names}}\t{{.Status}}"
	@echo ""
	@echo "2. Running tests..."
	uv run pytest -v
	@echo ""
	@echo "3. Checking lint..."
	uv run ruff check . --fix
	@echo ""
	@echo "✅ Verification complete."

# Run linting and formatting
lint:
	uv run ruff check . --fix
	uv run ruff format .

# ==============================================================================
# Frontend Commands
# ==============================================================================

# Lint frontend
frontend-lint:
	cd frontend && pnpm lint

# Build frontend
frontend-build:
	cd frontend && pnpm build

# Run frontend component tests
frontend-test:
	cd frontend && pnpm test run

# Run e2e tests against Docker stack (requires dev stack to be running)
frontend-e2e-docker:
	@echo "🧪 Running e2e tests against Docker stack..."
	@echo "⚠️  Ensure dev stack is running: make dev-up"
	cd frontend && pnpm exec playwright test --config=playwright.docker.config.ts

# ==============================================================================
# Reset Operations
# ==============================================================================

# Full system reset (nuclear option)
reset:
	@echo "🔥 Full system reset starting..."
	docker compose down -v --remove-orphans
	docker compose build --no-cache
	docker compose up -d
	@echo "✅ System reset complete. All containers rebuilt and started."

# Clean up build artifacts
clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	docker compose down --remove-orphans
	@echo "✅ Cleaned."

# ==============================================================================
# Build
# ==============================================================================

build:
	uv sync
	docker compose build
	cd frontend && pnpm install && pnpm build
	@echo "✅ Build complete."

# ==============================================================================
# Playground (ADK Web UI)
# ==============================================================================
# playground: full Docker stack (orchestrator + agents). Requires agents/ directory.
# playground-base: local base_agent only (baseline). GOOGLE_API_KEY or base_agent/.env required.
# playground-researcher: local researcher_agent only, no Docker.

playground:
	@echo "Starting ADK Playground..."
	@echo "⚠️  Note: Update this command to point to your orchestrator agent in agents/ directory."
	@echo "Example: uv run adk web agents/<orchestrator_agent> --port 8501 --reload_agents"
	# uv run adk web agents/<orchestrator_agent> --port 8501 --reload_agents

playground-base:
	@echo "Starting ADK Web for base_agent on port 8501 (no Docker required)."
	@echo "Set GOOGLE_API_KEY or use agents/base_agent/.env (see .env.example)."
	uv run adk web agents/base_agent --port 8501 --reload_agents

playground-researcher:
	@echo "Starting ADK Web for researcher_agent on port 8501 (no Docker required)."
	uv run adk web agents/researcher_agent --port 8501 --reload_agents
