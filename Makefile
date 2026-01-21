# ==============================================================================
# Antigravity Agent Platform - Developer Commands
# ==============================================================================
# Run any command with: make <target>
# Example: make test, make reset, make verify
# ==============================================================================

.PHONY: install test lint build start stop reset verify clean playground

# ==============================================================================
# Installation & Setup
# ==============================================================================

install:
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv sync --dev
	cd tools/dashboard && pnpm install

# ==============================================================================
# Development Commands
# ==============================================================================

# Start the platform (Docker containers + dashboard)
start:
	docker compose up -d
	@echo "✅ Containers started. Run 'cd tools/dashboard && pnpm dev' for dashboard."

# Stop the platform
stop:
	docker compose down
	@echo "✅ Platform stopped."

# ==============================================================================
# Testing & Verification
# ==============================================================================

# Run all tests
test:
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
	cd tools/dashboard && pnpm install && pnpm build
	@echo "✅ Build complete."

# ==============================================================================
# Playground (ADK Web UI)
# ==============================================================================

playground:
	@echo "Starting ADK Playground on port 8501..."
	@echo "⚠️  Make sure 'make start' has been run first!"
	uv run adk web domains/course_creator/orchestrator --port 8501 --reload_agents
