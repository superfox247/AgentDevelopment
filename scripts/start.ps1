# Universal Project Startup Script
# Usage: .\scripts\start.ps1
# This script ensures a clean environment, checks dependencies, and starts the full application stack.

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location "$PSScriptRoot/.."

# --- Phase 1: Clean System State ---
Write-Host "1. Cleaning System State..." -ForegroundColor Cyan

# Define ports to clear (Dashboard Frontend, Dev Server, Backend API, Metrics)
$ports = 4173, 5173, 8010, 8011

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            try {
                $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
                if ($proc) {
                    Write-Host "   Killing process '$($proc.ProcessName)' (PID: $($proc.Id)) on port $port" -ForegroundColor Yellow
                    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                }
            }
            catch {
                Write-Host "   Could not kill process on port $port. It might already be gone." -ForegroundColor DarkGray
            }
        }
    }
}

# --- Phase 2: Docker Environment ---
Write-Host "`n2. Checking Infrastructure..." -ForegroundColor Cyan

# Check Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH."
    exit 1
}

# Check/Start Docker Daemon
$dockerInfo = docker info 2>&1
if ($LastExitCode -ne 0) {
    Write-Host "   Docker Daemon is NOT running." -ForegroundColor Yellow
    Write-Host "   Attempting to start Docker Desktop..." -ForegroundColor Cyan
    
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-Host "   Waiting for Docker to start..." -ForegroundColor Yellow
        
        # Poll for Docker readiness
        $retries = 24 # 2 minutes
        $started = $false
        for ($i = 0; $i -lt $retries; $i++) {
            Start-Sleep -Seconds 5
            docker info > $null 2>&1
            if ($LastExitCode -eq 0) {
                $started = $true
                break
            }
            Write-Host "." -NoNewline
        }
        Write-Host ""
        
        if (-not $started) {
            Write-Error "Timed out waiting for Docker. Please start it manually."
            exit 1
        }
        Write-Host "   Docker Daemon is now running!" -ForegroundColor Green
    }
    else {
        Write-Error "Docker Desktop not found at standard path. Please start it manually."
        exit 1
    }
}
else {
    Write-Host "   Docker Daemon is active." -ForegroundColor Green
}

# Start Containers
Write-Host "   Ensuring backend services are running..." -ForegroundColor Cyan
docker-compose up -d --remove-orphans

if ($LastExitCode -ne 0) {
    Write-Error "Docker Compose failed."
    exit 1
}

# Check for specific containers to ensure they are actually running
Write-Host "   Verifying container health..." -ForegroundColor Cyan
$criticalServices = @("course_creator-orchestrator", "course_creator-image_generator", "course_creator-content_builder")
$failed = $false

Start-Sleep -Seconds 5 # Give them a moment to crash if they are going to crash

foreach ($service in $criticalServices) {
    $state = docker inspect --format="{{.State.Status}}" $service 2>$null
    if ($state -ne "running") {
        Write-Host "   [ERROR] Service '$service' is not running (State: $state). Check logs: docker logs $service" -ForegroundColor Red
        $failed = $true
    } else {
        Write-Host "   [OK] $service is running." -ForegroundColor Gray
    }
}

if ($failed) {
    Write-Warning "Some services failed to start correctly. The system may be unstable."
    # We don't exit here so the user can still debug, but we make it noisy.
}

# --- Phase 3: Application Application ---
Write-Host "`n3. Starting Application Stack..." -ForegroundColor Cyan

# 1. Start Backend (FastAPI) in a new standalone window
Write-Host "   Launching Backend API (Port 8010)..." -ForegroundColor Green
# We use 'cmd /c start' to ensure it pops a visible window so the user can see logs/errors easily
# Using 'uv run' to ensure dependencies are available
Start-Process "cmd" -ArgumentList "/c start uv run uvicorn tools.dashboard.server:app --port 8010 --reload" -WindowStyle Normal

# 2. Start Frontend (Vite) in the current window (or new if preferred, but existing window is good for 'preview')
Write-Host "   Launching Dashboard Frontend..." -ForegroundColor Green
Set-Location "tools/dashboard"

Write-Host "`n[SUCCESS] System Starting! Backend logs are in the new window." -ForegroundColor Green
Write-Host "Access Dashboard at: http://localhost:4173 (once started below)`n" -ForegroundColor Green

# Use 'cmd /c' to allow npm to run properly in PS context if needed, but direct execution is usually fine.
# We run this in the foreground so the script ends with the running server.
npm run preview
