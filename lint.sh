#!/bin/bash
# ==============================================================================
# Lint Script - Code quality checks (linting, type checking, formatting)
# ==============================================================================
# Usage:
#   ./lint.sh check      - Check backend linting and type checks
#   ./lint.sh fix        - Fix backend linting issues
#   ./lint.sh fast       - Fast type check (backend only)
#   ./lint.sh full       - Full type check (entire repo)
#   ./lint.sh frontend   - Check frontend linting and types
#   ./lint.sh all        - Run all checks (backend + frontend)

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 {check|fix|fast|full|frontend|all}"
  exit 1
fi

case "$1" in
  check)
    echo "🔍 Running backend linting checks..."
    uv run ruff check .
    echo "🔍 Running backend type checking..."
    uv run mypy dashboard_api
    echo "✅ Backend linting and type checks complete."
    ;;

  fix)
    echo "🔍 Running backend linting (fix mode)..."
    uv run ruff check . --fix
    echo "🔍 Running backend formatting..."
    uv run ruff format .
    echo "✅ Backend linting complete."
    ;;

  fast)
    echo "🔍 Running backend type checking (fast scope)..."
    uv run mypy dashboard_api
    echo "✅ Fast type check complete."
    ;;

  full)
    echo "🔍 Running backend type checking (full scope)..."
    uv run mypy .
    echo "✅ Full type check complete."
    ;;

  frontend)
    echo "🔍 Running frontend linting..."
    cd frontend && pnpm lint && cd ..
    echo "🔍 Running frontend type checking..."
    cd frontend && pnpm exec tsc --noEmit && cd ..
    echo "✅ Frontend linting and type check complete."
    ;;

  all)
    echo "🔍 Running all linting and type checks..."
    echo ""
    echo "1. Backend linting (fix mode)..."
    uv run ruff check . --fix
    uv run ruff format .
    echo ""
    echo "2. Backend type checking..."
    uv run mypy dashboard_api
    echo ""
    echo "3. Frontend linting..."
    cd frontend && pnpm lint && cd ..
    echo ""
    echo "4. Frontend type checking..."
    cd frontend && pnpm exec tsc --noEmit && cd ..
    echo ""
    echo "✅ All linting and type checks complete."
    ;;

  *)
    echo "Unknown command: $1"
    echo "Usage: $0 {check|fix|fast|full|frontend|all}"
    exit 1
    ;;
esac
