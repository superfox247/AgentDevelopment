# ==============================================================================
# Installation & Setup
# ==============================================================================

# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev

# ==============================================================================
# Playground Targets
# ==============================================================================

# Launch local dev playground (points to orchestrator)
# IMPORTANT: Ensure 'make run-local' is running in another terminal first!
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground for the Orchestrator...                   |"
	@echo "|                                                                             |"
	@echo "| ⚠️  IMPORTANT: Ensure 'make run-local' is running in another terminal!       |"
	@echo "|    The orchestrator needs the other agents to be online.                    |"
	@echo "|                                                                             |"
	@echo "| 🔍 Select 'orchestrator/app' if prompted.                                   |"
	@echo "==============================================================================="
	# We rely on .env file for configuration
	uv run adk web domains/course_creator/orchestrator --port 8501 --reload_agents

# ==============================================================================
# Local Development Commands
# ==============================================================================







# ==============================================================================
# Testing & Code Quality
# ==============================================================================

# Run unit and integration tests
test:
	uv run pytest tests/unit && uv run pytest tests/integration

# Run code quality checks (codespell, ruff, mypy)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check .
	uv run ruff format . --check
	uv run mypy .

# ==============================================================================
# Build & Deploy
# ==============================================================================

# Build all Docker containers
build:
	docker-compose build

# Clean up artifacts and containers
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	docker-compose down --remove-orphans
