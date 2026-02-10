# ==============================================================================
# Dev Script (PowerShell) - Docker & dev environment management
# ==============================================================================
# Usage:
#   .\dev.ps1 up      - Start Docker containers
#   .\dev.ps1 down    - Stop Docker containers
#   .\dev.ps1 reset   - Reset dev environment
#   .\dev.ps1 health  - Check service health
#   .\dev.ps1 logs    - Follow logs from all services
#   .\dev.ps1 logs-recent - Show recent logs (last 50 lines)
#   .\dev.ps1 logs-service <name> - Follow logs from specific service

param(
  [Parameter(Position = 0)]
  [string]$Command,
  
  [Parameter(Position = 1)]
  [string]$ServiceName
)

if ([string]::IsNullOrEmpty($Command)) {
  Write-Host "Usage: .\dev.ps1 {up|down|reset|build|health|logs|logs-recent|logs-service}" -ForegroundColor Yellow
  exit 1
}

function Wait-ForHealth {
  Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Cyan
  uv run python scripts/health_check.py --timeout 120
  if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Timeout or error waiting for services." -ForegroundColor Yellow
    docker compose logs --tail=50
    exit 1
  }
}

switch ($Command.ToLower()) {
  "up" {
    Write-Host "🚀 Starting dev stack..." -ForegroundColor Cyan
    docker compose up -d
    Write-Host "📋 Container status:" -ForegroundColor Cyan
    docker compose ps
    Write-Host ""
    Wait-ForHealth
    Write-Host ""
    Write-Host "✅ Docker services started." -ForegroundColor Green
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   Terminal 1: uv run python dashboard_api/server.py"
    Write-Host "   Terminal 2: cd frontend && pnpm dev"
  }

  "down" {
    Write-Host "🛑 Stopping dev stack..." -ForegroundColor Yellow
    docker compose down
    Write-Host "✅ Dev stack stopped." -ForegroundColor Green
  }

  "build" {
    Write-Host "🔨 Building Docker services..." -ForegroundColor Cyan
    docker compose build
    Write-Host "✅ Build complete." -ForegroundColor Green
  }

  "reset" {
    Write-Host "🔥 Resetting dev environment..." -ForegroundColor Red
    docker compose down -v --remove-orphans
    Write-Host "🔨 Building Docker services (this may take a while)..." -ForegroundColor Cyan
    docker compose build --no-cache
    Write-Host "🚀 Starting containers..." -ForegroundColor Cyan
    docker compose up -d
    Write-Host "📋 Container status:" -ForegroundColor Cyan
    docker compose ps
    Write-Host ""
    Wait-ForHealth
    Write-Host ""
    Write-Host "✅ Dev environment reset complete." -ForegroundColor Green
  }

  "health" {
    Write-Host "🏥 Checking service health..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Docker Containers:" -ForegroundColor Cyan
    docker compose ps
    Write-Host ""
    uv run python scripts/health_check.py
  }

  "logs" {
    Write-Host "📋 Following logs from all services (Ctrl+C to exit)..." -ForegroundColor Cyan
    docker compose logs -f
  }

  "logs-recent" {
    Write-Host "📋 Recent logs from all services (last 50 lines):" -ForegroundColor Cyan
    docker compose logs --tail=50
  }

  "logs-service" {
    if ([string]::IsNullOrEmpty($ServiceName)) {
      Write-Host "Usage: .\dev.ps1 logs-service <service-name>" -ForegroundColor Yellow
      Write-Host "Available services:" -ForegroundColor Cyan
      docker compose ps --format "table {{.Service}}" 2>$null
      exit 1
    }
    Write-Host "📋 Following logs for service: $ServiceName" -ForegroundColor Cyan
    docker compose logs -f $ServiceName
  }

  default {
    Write-Host "Unknown command: $Command" -ForegroundColor Red
    Write-Host "Usage: .\dev.ps1 {up|down|reset|build|health|logs|logs-recent|logs-service}" -ForegroundColor Yellow
    exit 1
  }
}
