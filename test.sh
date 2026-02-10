#!/bin/bash
# ==============================================================================
# Test Script - Run tests for backend and frontend
# ==============================================================================
# Usage:
#   ./test.sh backend     - Run backend tests (with evaluations)
#   ./test.sh backend-fast - Run backend tests (skip evals, faster)
#   ./test.sh backend-agent <agent-name> - Run tests for specific agent
#   ./test.sh frontend    - Run frontend component tests
#   ./test.sh e2e         - Run frontend e2e tests (requires dev stack running)
#   ./test.sh all         - Run all tests in order

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 {backend|backend-fast|backend-agent|frontend|e2e|all}"
  exit 1
fi

case "$1" in
  backend)
    echo "🧪 Running backend tests..."
    python run_tests.py
    ;;

  backend-fast)
    echo "🧪 Running backend tests (skip evals, faster)..."
    python run_tests.py --skip-evals
    ;;

  backend-agent)
    if [ -z "$2" ]; then
      echo "Usage: $0 backend-agent <agent-name>"
      exit 1
    fi
    echo "🧪 Running tests for agent: $2"
    python run_tests.py --agent "$2"
    ;;

  frontend)
    echo "🧪 Running frontend component tests..."
    cd frontend && pnpm test run && cd ..
    echo "✅ Frontend tests complete."
    ;;

  e2e)
    echo "🧪 Running frontend e2e tests..."
    echo "⚠️  Ensure dev stack is running: ./dev.sh up"
    cd frontend && pnpm exec playwright test --config=playwright.docker.config.ts && cd ..
    echo "✅ E2E tests complete."
    ;;

  all)
    echo "🧪 Running all tests..."
    echo ""
    echo "1. Backend tests (fast)..."
    python run_tests.py --skip-evals || {
      echo "❌ Backend tests failed"
      exit 1
    }
    echo ""
    echo "2. Frontend tests..."
    cd frontend && pnpm test run && cd ..
    echo ""
    echo "✅ All tests complete."
    ;;

  *)
    echo "Unknown command: $1"
    echo "Usage: $0 {backend|backend-fast|backend-agent|frontend|e2e|all}"
    exit 1
    ;;
esac
