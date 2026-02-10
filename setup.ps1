# ==============================================================================
# Setup Script (PowerShell) - Install dependencies
# ==============================================================================
# Usage: .\setup.ps1

Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan

# Check and install uv if needed
$uv = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uv) {
  Write-Host "Installing uv..." -ForegroundColor Yellow
  irm https://astral.sh/uv/install.ps1 | iex
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
uv sync --dev

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
Push-Location frontend
pnpm install
Pop-Location

Write-Host "✅ Installation complete." -ForegroundColor Green
