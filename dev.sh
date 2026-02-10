#!/bin/bash
# ==============================================================================
# Dev Script - Docker & dev environment management
# ==============================================================================
# Usage:
#   ./dev.sh up      - Start Docker containers
#   ./dev.sh down    - Stop Docker containers
#   ./dev.sh reset   - Reset dev environment (clean, rebuild, start)
#   ./dev.sh health  - Check service health
#   ./dev.sh logs    - Follow logs from all services
#   ./dev.sh logs-recent - Show recent logs (last 50 lines)
#   ./dev.sh logs-service <name> - Follow logs from specific service

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 {up|down|reset|build|health|logs|logs-recent|logs-service}"
  exit 1
fi

case "$1" in
  up)
    echo "🚀 Starting dev stack..."
    docker compose up -d
    echo "📋 Container status:"
    docker compose ps
    echo ""
    echo "⏳ Waiting for services to be healthy..."
    uv run python scripts/health_check.py --timeout 120 || {
      echo ""
      echo "⚠️  Timeout or error waiting for services."
      docker compose logs --tail=50
      exit 1
    }
    echo ""
    echo "✅ Docker services started."
    echo "📝 Next steps:"
    echo "   Terminal 1: uv run python dashboard_api/server.py"
    echo "   Terminal 2: cd frontend && pnpm dev"
    ;;

  down)
    echo "🛑 Stopping dev stack..."
    docker compose down
    echo "✅ Dev stack stopped."
    ;;

  build)
    echo "🔨 Building Docker services..."
    docker compose build
    echo "✅ Build complete."
    ;;

  reset)
    echo "🔥 Resetting dev environment..."
    docker compose down -v --remove-orphans
    echo "🔨 Building Docker services (this may take a while)..."
    docker compose build --no-cache
    echo "🚀 Starting containers..."
    docker compose up -d
    echo "📋 Container status:"
    docker compose ps
    echo ""
    echo "⏳ Waiting for services to be healthy..."
    uv run python scripts/health_check.py --timeout 120 || {
      echo ""
      echo "⚠️  Timeout or error waiting for services."
      docker compose logs --tail=50
      exit 1
    }
    echo ""
    echo "✅ Dev environment reset complete."
    ;;

  health)
    echo "🏥 Checking service health..."
    echo ""
    echo "Docker Containers:"
    docker compose ps
    echo ""
    uv run python scripts/health_check.py
    ;;

  logs)
    echo "📋 Following logs from all services (Ctrl+C to exit)..."
    docker compose logs -f
    ;;

  logs-recent)
    echo "📋 Recent logs from all services (last 50 lines):"
    docker compose logs --tail=50
    ;;

  logs-service)
    if [ -z "$2" ]; then
      echo "Usage: $0 logs-service <service-name>"
      echo "Available services:"
      docker compose ps --format "table {{.Service}}" 2>/dev/null || echo "No services running"
      exit 1
    fi
    echo "📋 Following logs for service: $2"
    docker compose logs -f "$2"
    ;;

  *)
    echo "Unknown command: $1"
    echo "Usage: $0 {up|down|reset|build|health|logs|logs-recent|logs-service}"
    exit 1
    ;;
esac
