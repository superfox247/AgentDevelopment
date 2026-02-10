# ==============================================================================
# Test Script (PowerShell) - Run tests for backend and frontend
# ==============================================================================
# Usage:
#   .\test.ps1 backend     - Run backend tests (with evaluations)
#   .\test.ps1 backend-fast - Run backend tests (skip evals, faster)
#   .\test.ps1 backend-agent <agent-name> - Run tests for specific agent
#   .\test.ps1 frontend    - Run frontend component tests
#   .\test.ps1 e2e         - Run frontend e2e tests (requires dev stack running)
#   .\test.ps1 all         - Run all tests in order

param(
  [Parameter(Position = 0)]
  [string]$Command,
  
  [Parameter(Position = 1)]
  [string]$AgentName
)

if ([string]::IsNullOrEmpty($Command)) {
  Write-Host "Usage: .\test.ps1 {backend|backend-fast|backend-agent|frontend|e2e|all}" -ForegroundColor Yellow
  exit 1
}

switch ($Command.ToLower()) {
  "backend" {
    Write-Host "🧪 Running backend tests..." -ForegroundColor Cyan
    python run_tests.py
  }

  "backend-fast" {
    Write-Host "🧪 Running backend tests (skip evals, faster)..." -ForegroundColor Cyan
    python run_tests.py --skip-evals
  }

  "backend-agent" {
    if ([string]::IsNullOrEmpty($AgentName)) {
      Write-Host "Usage: .\test.ps1 backend-agent <agent-name>" -ForegroundColor Yellow
      exit 1
    }
    Write-Host "🧪 Running tests for agent: $AgentName" -ForegroundColor Cyan
    python run_tests.py --agent $AgentName
  }

  "frontend" {
    Write-Host "🧪 Running frontend component tests..." -ForegroundColor Cyan
    Push-Location frontend
    pnpm test run
    Pop-Location
    Write-Host "✅ Frontend tests complete." -ForegroundColor Green
  }

  "e2e" {
    Write-Host "🧪 Running frontend e2e tests..." -ForegroundColor Cyan
    Write-Host "⚠️  Ensure dev stack is running: .\dev.ps1 up" -ForegroundColor Yellow
    Push-Location frontend
    pnpm exec playwright test --config=playwright.docker.config.ts
    Pop-Location
    Write-Host "✅ E2E tests complete." -ForegroundColor Green
  }

  "all" {
    Write-Host "🧪 Running all tests..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Backend tests (fast)..." -ForegroundColor Cyan
    python run_tests.py --skip-evals
    if ($LASTEXITCODE -ne 0) {
      Write-Host "❌ Backend tests failed" -ForegroundColor Red
      exit 1
    }
    Write-Host ""
    Write-Host "2. Frontend tests..." -ForegroundColor Cyan
    Push-Location frontend
    pnpm test run
    Pop-Location
    Write-Host ""
    Write-Host "✅ All tests complete." -ForegroundColor Green
  }

  default {
    Write-Host "Unknown command: $Command" -ForegroundColor Red
    Write-Host "Usage: .\test.ps1 {backend|backend-fast|backend-agent|frontend|e2e|all}" -ForegroundColor Yellow
    exit 1
  }
}
