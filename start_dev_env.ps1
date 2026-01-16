# Intelligent Environment Start Script
# Usage: .\start_dev_env.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Checking Docker Environment..." -ForegroundColor Cyan

# 1. Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH."
    exit 1
}

# 2. Check if Docker Daemon is running
$dockerInfo = docker info 2>&1
if ($LastExitCode -ne 0) {
    Write-Host "Docker Daemon is NOT running." -ForegroundColor Yellow
    Write-Host "Attempting to start Docker Desktop..." -ForegroundColor Cyan
    
    # Try standard paths for Docker Desktop
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-Host "Waiting for Docker to start (may take up to 2 mins)..." -ForegroundColor Yellow
        
        # Loop until docker info succeeds
        $retries = 24 # 2 minutes (5s interval)
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
        Write-Host "" # Newline
        
        if (-not $started) {
            Write-Error "Timed out waiting for Docker to start. Please start it manually."
            exit 1
        }
        Write-Host "Docker Daemon is now running!" -ForegroundColor Green
    }
    else {
        Write-Error "Docker Desktop not found at standard path. Please start it manually."
        exit 1
    }
}
else {
    Write-Host "Docker Daemon is active." -ForegroundColor Green
}

# 3. Intelligent Container Startup
Write-Host "Checking containers..." -ForegroundColor Cyan

# Check if containers are already running to avoid "Recreating" if not needed
$running = docker-compose ps --services --filter "status=running"
if ($running) {
    Write-Host "Active services: $running"
}

# Run up -d (Docker Compose handles idempotency)
Write-Host "Ensuring configuration is applied..." -ForegroundColor Cyan
docker-compose up -d --remove-orphans

if ($LastExitCode -ne 0) {
    Write-Error "Docker Compose failed."
    exit 1
}

# 4. Final Health Check
Write-Host "Verifying services..." -ForegroundColor Cyan
$services = "orchestrator", "researcher", "judge", "content_builder", "phoenix"
foreach ($svc in $services) {
    $containerName = "course-creation-ai-agent-architecture-$svc-1"
    $state = docker inspect --format '{{.State.Status}}' $containerName 2>$null
    if ($state -eq "running") {
        Write-Host "   $svc is running" -ForegroundColor Green
    }
    else {
        $msg = "   $svc is $state (Check logs: docker logs $containerName)"
        Write-Host $msg -ForegroundColor Red
    }
}

Write-Host "Environment Ready!" -ForegroundColor Green
Write-Host "   Orchestrator: http://localhost:8000"
Write-Host "   Phoenix UI:   http://localhost:6006"
