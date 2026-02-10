# ==============================================================================
# Lint Script (PowerShell) - Code quality checks (linting, type checking, formatting)
# ==============================================================================
# Usage:
#   .\lint.ps1 check      - Check backend linting and type checks
#   .\lint.ps1 fix        - Fix backend linting issues
#   .\lint.ps1 fast       - Fast type check (backend only)
#   .\lint.ps1 full       - Full type check (entire repo)
#   .\lint.ps1 frontend   - Check frontend linting and types
#   .\lint.ps1 all        - Run all checks (backend + frontend)

param(
  [Parameter(Position = 0)]
  [string]$Command
)

if ([string]::IsNullOrEmpty($Command)) {
  Write-Host "Usage: .\lint.ps1 {check|fix|fast|full|frontend|all}" -ForegroundColor Yellow
  exit 1
}

switch ($Command.ToLower()) {
  "check" {
    Write-Host "🔍 Running backend linting checks..." -ForegroundColor Cyan
    uv run ruff check .
    Write-Host "🔍 Running backend type checking..." -ForegroundColor Cyan
    uv run mypy dashboard_api
    Write-Host "✅ Backend linting and type checks complete." -ForegroundColor Green
  }

  "fix" {
    Write-Host "🔍 Running backend linting (fix mode)..." -ForegroundColor Cyan
    uv run ruff check . --fix
    Write-Host "🔍 Running backend formatting..." -ForegroundColor Cyan
    uv run ruff format .
    Write-Host "✅ Backend linting complete." -ForegroundColor Green
  }

  "fast" {
    Write-Host "🔍 Running backend type checking (fast scope)..." -ForegroundColor Cyan
    uv run mypy dashboard_api
    Write-Host "✅ Fast type check complete." -ForegroundColor Green
  }

  "full" {
    Write-Host "🔍 Running backend type checking (full scope)..." -ForegroundColor Cyan
    uv run mypy .
    Write-Host "✅ Full type check complete." -ForegroundColor Green
  }

  "frontend" {
    Write-Host "🔍 Running frontend linting..." -ForegroundColor Cyan
    Push-Location frontend
    pnpm lint
    Write-Host "🔍 Running frontend type checking..." -ForegroundColor Cyan
    pnpm exec tsc --noEmit
    Pop-Location
    Write-Host "✅ Frontend linting and type check complete." -ForegroundColor Green
  }

  "all" {
    Write-Host "🔍 Running all linting and type checks..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Backend linting (fix mode)..." -ForegroundColor Cyan
    uv run ruff check . --fix
    uv run ruff format .
    Write-Host ""
    Write-Host "2. Backend type checking..." -ForegroundColor Cyan
    uv run mypy dashboard_api
    Write-Host ""
    Write-Host "3. Frontend linting..." -ForegroundColor Cyan
    Push-Location frontend
    pnpm lint
    Write-Host ""
    Write-Host "4. Frontend type checking..." -ForegroundColor Cyan
    pnpm exec tsc --noEmit
    Pop-Location
    Write-Host ""
    Write-Host "✅ All linting and type checks complete." -ForegroundColor Green
  }

  default {
    Write-Host "Unknown command: $Command" -ForegroundColor Red
    Write-Host "Usage: .\lint.ps1 {check|fix|fast|full|frontend|all}" -ForegroundColor Yellow
    exit 1
  }
}
