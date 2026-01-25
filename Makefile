# ==============================================================================
# Antigravity Agent Platform - Developer Commands
# ==============================================================================
# Run any command with: make <target>
# Example: make test, make reset, make verify
# ==============================================================================

.PHONY: install test lint build start stop reset verify clean playground playground-researcher

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
# playground-researcher: local researcher_agent only, no Docker.

playground:
	@echo "Starting ADK Playground..."
	@echo "⚠️  Note: Update this command to point to your orchestrator agent in agents/ directory."
	@echo "Example: uv run adk web agents/<orchestrator_agent> --port 8501 --reload_agents"
	# uv run adk web agents/<orchestrator_agent> --port 8501 --reload_agents

playground-researcher:
	@echo "Starting ADK Web for researcher_agent on port 8501 (no Docker required)."
	uv run adk web agents/researcher_agent --port 8501 --reload_agents
