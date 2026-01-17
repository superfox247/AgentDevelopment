# Factor Reset Script
# Usage: .\reset_dev_env.ps1


[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
# Adjusted path since we are now deeper in the folder structure (.agent/skills/reset_environment)
Set-Location "$PSScriptRoot/../../.."


Write-Host "⚠️  INITIATING FACTORY RESET ⚠️" -ForegroundColor Red
Write-Host "This will delete all containers, volumes (telemetry data), and local artifacts."
Write-Host "Stopping Services..." -ForegroundColor Cyan

# 1. Deep Docker Clean
# -v: Remove named volumes declared in the `volumes` section of the Compose file.
# --remove-orphans: Remove containers for services not defined in the Compose file.
# --rmi local: Remove images that don't have a custom tag (local builds).
# This will now include the new 'course-creation-ai-agent-architecture-webapp' image
docker-compose down -v --remove-orphans --rmi local

if ($LastExitCode -ne 0) {
    Write-Error "Failed to stop docker services."
    exit 1
}

# 2. Clean Local Artifacts
Write-Host "Cleaning local Python artifacts..." -ForegroundColor Cyan
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue }
if (Test-Path .pytest_cache) { Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue }
if (Test-Path .ruff_cache) { Remove-Item -Recurse -Force .ruff_cache -ErrorAction SilentlyContinue }
if (Test-Path .mypy_cache) { Remove-Item -Recurse -Force .mypy_cache -ErrorAction SilentlyContinue }
Get-ChildItem -Path . -Recurse -Include "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 3. Re-Install Dependencies
Write-Host "Re-installing dependencies..." -ForegroundColor Cyan
uv sync --dev

# 4. Fresh Build & Start
Write-Host "Building and Starting Fresh..." -ForegroundColor Cyan
# --build: Build images before starting containers.
# --force-recreate: Recreate containers even if their configuration and image haven't changed.
docker-compose up -d --build --force-recreate

if ($LastExitCode -ne 0) {
    Write-Error "Failed to start services."
    exit 1
}

Write-Host "✅ Factory Reset Complete!" -ForegroundColor Green
Write-Host "   Orchestrator: http://localhost:8000"
Write-Host "   Phoenix UI:   http://localhost:6006"
