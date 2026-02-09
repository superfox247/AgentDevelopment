# ==============================================================================
# Antigravity Agent Platform - Developer Commands (PowerShell)
# ==============================================================================
# Run any command with: .\make.ps1 <target>
# Example: .\make.ps1 test, .\make.ps1 reset, .\make.ps1 verify
# ==============================================================================

param(
    [Parameter(Position = 0)]
    [string]$Target = "",
    
    [Parameter()]
    [string]$Service = "",
    
    [Parameter()]
    [string]$Agent = "",

    [Parameter()]
    [string]$Project = "",

    [Parameter()]
    [string]$Repo = "",

    [Parameter()]
    [string]$Region = "us-central1",

    [Parameter()]
    [string]$ArtifactLocation = "us",

    [Parameter()]
    [string]$ArtifactRepo = "antigravity",

    [Parameter()]
    [string]$ImageName = "dashboard-api",

    [Parameter()]
    [string]$Pipeline = "dashboard-api",

    [Parameter()]
    [string]$StagingService = "dashboard-api-staging",

    [Parameter()]
    [string]$ProductionService = "dashboard-api-production",

    [Parameter()]
    [string]$Pool = "github-pool",

    [Parameter()]
    [string]$Provider = "github-provider",

    [Parameter()]
    [string]$ServiceAccount = "github-actions-cicd",

    [Parameter()]
    [string]$ServiceAccountEmail = "",

    [Parameter()]
    [string]$WifProvider = ""
)

$ErrorActionPreference = "Stop"

# Ensure we run from project root (where docker-compose.yml lives)
if ($PSScriptRoot) { Set-Location $PSScriptRoot }

# Load GEMINI_API_KEY from Windows (User, then Machine) so Docker Compose and ADK use it.
# Set it in Windows env vars; make.ps1 uses it everywhere automatically.
function Ensure-GeminiApiKey {
    if ([string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) {
        $env:GEMINI_API_KEY = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY", "User")
    }
    if ([string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) {
        $env:GEMINI_API_KEY = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY", "Machine")
    }
}
Ensure-GeminiApiKey | Out-Null

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Test-DockerRunning {
    """Check if Docker is running and accessible."""
    try {
        $result = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
}

function Ensure-DockerRunning {
    """Ensure Docker is running, provide helpful error if not."""
    if (-not (Test-DockerRunning)) {
        Write-Error "[ERROR] Docker is not running or not accessible."
        Write-Info ""
        Write-Info "Please ensure Docker Desktop is:"
        Write-Info "  1. Installed and running"
        Write-Info "  2. Started (check system tray for Docker icon)"
        Write-Info "  3. Fully initialized (wait for 'Docker Desktop is running' message)"
        Write-Info ""
        Write-Info "To start Docker Desktop:"
        Write-Info "  - Search for 'Docker Desktop' in Start menu and launch it"
        Write-Info "  - Or run: Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'"
        Write-Info ""
        Write-Info "After starting Docker Desktop, wait 10-30 seconds for it to fully initialize,"
        Write-Info "then run this command again."
        exit 1
    }
}

# ==============================================================================
# Installation & Setup
# ==============================================================================

function Invoke-Install {
    Write-Info "Installing dependencies..."
    
    # Check if uv is installed
    if (-not (Test-Command "uv")) {
        Write-Info "Installing uv..."
        $installScript = "https://astral.sh/uv/install.sh"
        try {
            # For Windows, we need to use PowerShell to install uv
            # uv installer for Windows uses a different method
            Write-Warning "uv installation on Windows requires manual setup."
            Write-Info "Please install uv from: https://github.com/astral-sh/uv"
            Write-Info "Or run: powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`""
            return
        }
        catch {
            Write-Error "Failed to install uv. Please install manually."
            exit 1
        }
    }
    
    uv sync --dev
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Push-Location frontend
    pnpm install
    if ($LASTEXITCODE -ne 0) { 
        Pop-Location
        exit 1 
    }
    Pop-Location
    
    Write-Success "[OK] Installation complete."
}

function Invoke-CodexPreflight {
    Write-Info "Running Codex preflight checks..."
    bash scripts/codex_preflight.sh
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-CodexPreflightFull {
    Write-Info "Running strict Codex preflight checks for full dev..."
    bash scripts/codex_preflight.sh --require-docker --require-playwright
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# ==============================================================================
# Development Commands
# ==============================================================================

function Invoke-Start {
    Ensure-DockerRunning
    Write-Info "Starting platform..."
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Containers started. Run 'cd frontend; pnpm dev' for dashboard."
}

function Invoke-Stop {
    Ensure-DockerRunning
    Write-Info "Stopping platform..."
    docker compose down
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Platform stopped."
}

# ==============================================================================
# Docker Development Workflow
# ==============================================================================

function Invoke-DevReset {
    Ensure-DockerRunning
    Write-Info "[RESET] Resetting dev environment..."
    docker compose down -v --remove-orphans
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Info "[BUILD] Building Docker services (this may take a while)..."
    docker compose build --no-cache
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Info "[START] Starting containers..."
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Info "[STATUS] Container status:"
    docker compose ps
    
    Write-Info ""
    Write-Info "[WAIT] Waiting for services to be healthy..."
    Invoke-DevWaitHealth
    
    Write-Info ""
    Write-Info "[STATUS] Final container status:"
    docker compose ps
    
    Write-Info ""
    Write-Success "[OK] Dev environment reset complete."
}

function Invoke-DevUp {
    Ensure-DockerRunning
    Write-Info "[START] Starting dev stack..."
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Info "[STATUS] Container status:"
    docker compose ps
    
    Write-Info ""
    Write-Info "[WAIT] Waiting for services to be healthy..."
    Invoke-DevWaitHealth
    
    Write-Info ""
    Write-Info "[STATUS] Final container status:"
    docker compose ps
    
    Write-Info ""
    Write-Success "[OK] Docker services started."
    Write-Info "[INFO] Next steps:"
    Write-Info "   Terminal 1: uv run python dashboard_api/server.py"
    Write-Info "   Terminal 2: cd frontend; pnpm dev"
}

function Invoke-DevDown {
    Ensure-DockerRunning
    Write-Info "[STOP] Stopping dev stack..."
    docker compose down
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Dev stack stopped."
}

function Invoke-DevHealth {
    Ensure-DockerRunning
    Write-Info "[HEALTH] Checking service health..."
    Write-Info ""
    Write-Info "Docker Containers:"
    docker compose ps
    
    Write-Info ""
    uv run python scripts/health_check.py
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-DevLogs {
    docker compose logs -f
}

function Invoke-DevLogsRecent {
    Write-Info "[LOGS] Recent logs from all services (last 50 lines):"
    Write-Info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker compose logs --tail=50
    Write-Info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Info "For live logs, run: .\make.ps1 dev-logs"
}

function Invoke-DevLogsService {
    if ([string]::IsNullOrWhiteSpace($Service)) {
        Write-Error "Usage: .\make.ps1 dev-logs-service -Service phoenix"
        Write-Info "Available services:"
        docker compose ps --format "table {{.Service}}"
        exit 1
    }
    Write-Info "[LOGS] Logs for service: $Service"
    docker compose logs -f $Service
}

function Invoke-DevLogsServiceRecent {
    if ([string]::IsNullOrWhiteSpace($Service)) {
        Write-Error "Usage: .\make.ps1 dev-logs-service-recent -Service phoenix"
        Write-Info "Available services:"
        docker compose ps --format "table {{.Service}}"
        exit 1
    }
    Write-Info "[LOGS] Recent logs for service: $Service (last 50 lines)"
    Write-Info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker compose logs --tail=50 $Service
    Write-Info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

function Invoke-DevBuild {
    Ensure-DockerRunning
    Write-Info "[BUILD] Building Docker services..."
    docker compose build
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Build complete."
}

function Invoke-DevUpAdk {
    Ensure-DockerRunning
    Write-Info "[START] Starting all_agents (ADK web at http://localhost:8501)..."
    Write-Info "[INFO] Uses GEMINI_API_KEY from Windows."
    docker compose up -d --force-recreate all_agents
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Done. Open http://localhost:8501 and select researcher_agent."
}

function Invoke-DevDockerStatus {
    """Check Docker status and provide helpful information."""
    Write-Info "[DOCKER] Checking Docker status..."
    Write-Info ""
    
    if (Test-DockerRunning) {
        Write-Success "[OK] Docker is running"
        Write-Info ""
        Write-Info "Docker version:"
        docker --version
        Write-Info ""
        Write-Info "Docker Compose version:"
        docker compose version
        Write-Info ""
        Write-Info "Running containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        Write-Info ""
        Write-Info "All containers (including stopped):"
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    }
    else {
        Write-Error "[ERROR] Docker is not running or not accessible."
        Write-Info ""
        Write-Info "Please ensure Docker Desktop is:"
        Write-Info "  1. Installed and running"
        Write-Info "  2. Started (check system tray for Docker icon)"
        Write-Info "  3. Fully initialized (wait for 'Docker Desktop is running' message)"
        Write-Info ""
        Write-Info "To start Docker Desktop:"
        Write-Info "  - Search for 'Docker Desktop' in Start menu and launch it"
        Write-Info "  - Or run: Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'"
        exit 1
    }
}

function Invoke-DevWaitHealth {
    Ensure-DockerRunning
    Write-Info "[WAIT] Waiting for services to be ready (max 120s)..."
    uv run python scripts/health_check.py --timeout 120
    if ($LASTEXITCODE -ne 0) {
        Write-Info ""
        Write-Warning "[WARN] Timeout waiting for services."
        Write-Info "[LOGS] Showing recent logs from all services:"
        docker compose logs --tail=50
        Write-Info ""
        Write-Info "For live logs, run: .\make.ps1 dev-logs"
        exit 1
    }
}

function Invoke-DevVerify {
    Write-Info "[VERIFY] Running full dev verification..."
    Write-Info ""
    
    Write-Info "1. Linting backend..."
    Invoke-Lint
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ERROR] Backend linting failed"
        exit 1
    }
    
    Write-Info ""
    Write-Info "2. Linting frontend..."
    Invoke-FrontendLint
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ERROR] Frontend linting failed"
        exit 1
    }
    
    Write-Info ""
    Write-Info "3. Building Docker services..."
    Invoke-DevBuild
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ERROR] Docker build failed"
        exit 1
    }
    
    Write-Info ""
    Write-Info "4. Starting dev stack..."
    Invoke-DevUp
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ERROR] Failed to start dev stack"
        exit 1
    }
    
    Write-Info ""
    Write-Info "5. Running backend tests..."
    Invoke-TestFast
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ERROR] Backend tests failed"
        exit 1
    }
    
    Write-Info ""
    Write-Info "6. Running frontend tests..."
    Invoke-FrontendTest
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ERROR] Frontend tests failed"
        exit 1
    }
    
    Write-Info ""
    Write-Info "7. Running e2e tests against Docker stack..."
    Invoke-FrontendE2EDocker
    if ($LASTEXITCODE -ne 0) {
        Write-Info ""
        Write-Error "[ERROR] E2E tests failed. Showing recent logs:"
        Invoke-DevLogsRecent
        exit 1
    }
    
    Write-Info ""
    Write-Success "[OK] Full verification complete!"
}

# ==============================================================================
# Testing & Verification
# ==============================================================================

function Invoke-Test {
    python run_tests.py
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-TestAgent {
    if ([string]::IsNullOrWhiteSpace($Agent)) {
        Write-Error "Usage: .\make.ps1 test-agent -Agent researcher_agent"
        exit 1
    }
    python run_tests.py --agent $Agent
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-TestFast {
    python run_tests.py --skip-evals
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-TestPytest {
    uv run pytest
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-Verify {
    Write-Info "=== System Verification ==="
    Write-Info "1. Checking containers..."
    docker ps -a --format "table {{.Names}}`t{{.Status}}"
    
    Write-Info ""
    Write-Info "2. Running tests..."
    uv run pytest -v
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Info ""
    Write-Info "3. Checking lint..."
    uv run ruff check . --fix
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Info ""
    Write-Success "[OK] Verification complete."
}

function Invoke-Lint {
    Write-Info "[LINT] Running backend linting..."
    uv run ruff check . --fix
    if ($LASTEXITCODE -ne 0) { exit 1 }
    uv run ruff format .
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Backend linting complete."
}

function Invoke-TypeCheck {
    Write-Info "[TYPE] Running all type checks..."
    Invoke-TypeCheckFast
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Invoke-TypeCheckFrontend
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] All type checks complete."
}

function Invoke-TypeCheckFast {
    Write-Info "[TYPE] Running backend type checking (mypy, fast scope)..."
    uv run mypy dashboard_api
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Backend fast type checking complete."
}

function Invoke-TypeCheckFull {
    Write-Info "[TYPE] Running backend type checking (mypy, full scope)..."
    uv run mypy .
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Backend full type checking complete."
}

function Invoke-TypeCheckBackend {
    Invoke-TypeCheckFast
}

function Invoke-TypeCheckFrontend {
    Write-Info "[TYPE] Running frontend type checking (TypeScript)..."
    Push-Location frontend
    pnpm exec tsc --noEmit
    $result = $LASTEXITCODE
    Pop-Location
    if ($result -ne 0) { exit 1 }
    Write-Success "[OK] Frontend type checking complete."
}

# ==============================================================================
# Frontend Commands
# ==============================================================================

function Invoke-FrontendLint {
    Write-Info "[LINT] Running frontend linting..."
    Push-Location frontend
    pnpm lint
    $result = $LASTEXITCODE
    Pop-Location
    if ($result -ne 0) { exit 1 }
    Write-Success "[OK] Frontend linting complete."
}

function Invoke-FrontendBuild {
    Push-Location frontend
    pnpm build
    $result = $LASTEXITCODE
    Pop-Location
    if ($result -ne 0) { exit 1 }
}

function Invoke-FrontendTest {
    Push-Location frontend
    pnpm test run
    $result = $LASTEXITCODE
    Pop-Location
    if ($result -ne 0) { exit 1 }
}

function Invoke-FrontendE2EDocker {
    Write-Info "[TEST] Running e2e tests against Docker stack..."
    Write-Warning "[WARN] Ensure dev stack is running: .\make.ps1 dev-up"
    Push-Location frontend
    pnpm exec playwright test --config=playwright.docker.config.ts
    $result = $LASTEXITCODE
    Pop-Location
    if ($result -ne 0) { exit 1 }
}

# ==============================================================================
# Reset Operations
# ==============================================================================

function Invoke-Reset {
    Write-Info "[RESET] Full system reset starting..."
    docker compose down -v --remove-orphans
    if ($LASTEXITCODE -ne 0) { exit 1 }
    docker compose build --no-cache
    if ($LASTEXITCODE -ne 0) { exit 1 }
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] System reset complete. All containers rebuilt and started."
}

function Invoke-Clean {
    Write-Info "Cleaning build artifacts..."
    
    # Remove cache directories
    $cacheDirs = @(".pytest_cache", ".ruff_cache", ".mypy_cache")
    foreach ($dir in $cacheDirs) {
        if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir
        }
    }
    
    # Remove __pycache__ directories
    Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue | 
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    docker compose down --remove-orphans
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Success "[OK] Cleaned."
}

function Invoke-Build {
    Write-Info "Building project..."
    uv sync
    if ($LASTEXITCODE -ne 0) { exit 1 }
    docker compose build
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Push-Location frontend
    pnpm install
    if ($LASTEXITCODE -ne 0) { 
        Pop-Location
        exit 1 
    }
    pnpm build
    if ($LASTEXITCODE -ne 0) { 
        Pop-Location
        exit 1 
    }
    Pop-Location
    Write-Success "[OK] Build complete."
}

function Invoke-DocsGenerate {
    Write-Info "Generating docs artifacts..."
    uv run python scripts/generate_reference_docs.py
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Generated docs artifacts updated."
}

function Invoke-DocsCheck {
    Write-Info "Checking generated docs artifacts..."
    uv run python scripts/generate_reference_docs.py --check
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Generated docs artifacts are up to date."
}

function Invoke-CommandCatalogCheck {
    Write-Info "Checking command catalog sync..."
    uv run python scripts/validate_command_catalog_sync.py
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Success "[OK] Command catalog is in sync."
}

# ==============================================================================
# Playground (ADK Web UI)
# ==============================================================================

function Invoke-Playground {
    Write-Info "Starting ADK Playground..."
    Write-Warning "[WARN] Note: Update this command to point to your orchestrator agent in agents/ directory."
    Write-Info "Example: uv run adk web agents/<orchestrator_agent> --port 8501 --reload_agents"
    # uv run adk web agents/<orchestrator_agent> --port 8501 --reload_agents
}

function Invoke-PlaygroundBase {
    Write-Info "Starting ADK Web for base_agent on port 8501 (no Docker required)."
    Write-Info "Uses GEMINI_API_KEY from Windows (or .env)."
    uv run adk web agents/base_agent --port 8501 --reload_agents
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-PlaygroundResearcher {
    Write-Info "Starting ADK Web for researcher_agent on port 8501 (no Docker required)."
    Write-Info "Uses GEMINI_API_KEY from Windows (or .env)."
    uv run adk web agents/researcher_agent --port 8501 --reload_agents
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# ==============================================================================
# GCP CI/CD Commands
# ==============================================================================

function Invoke-GcpBootstrap {
    if ([string]::IsNullOrWhiteSpace($Project)) {
        Write-Error "Usage: .\make.ps1 gcp-bootstrap -Project <gcp-project-id> [-Region us-central1] [-ArtifactLocation us] [-ArtifactRepo antigravity] [-Pipeline dashboard-api] [-StagingService dashboard-api-staging] [-ProductionService dashboard-api-production]"
        exit 1
    }

    & "$PSScriptRoot\infra\gcp\bootstrap.ps1" `
        -ProjectId $Project `
        -Region $Region `
        -ArtifactLocation $ArtifactLocation `
        -ArtifactRepository $ArtifactRepo `
        -PipelineName $Pipeline `
        -StagingService $StagingService `
        -ProductionService $ProductionService

    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-GcpSetupWif {
    if ([string]::IsNullOrWhiteSpace($Project) -or [string]::IsNullOrWhiteSpace($Repo)) {
        Write-Error "Usage: .\make.ps1 gcp-setup-wif -Project <gcp-project-id> -Repo <owner/repo> [-Pool github-pool] [-Provider github-provider] [-ServiceAccount github-actions-cicd]"
        exit 1
    }

    & "$PSScriptRoot\infra\gcp\setup_wif.ps1" `
        -ProjectId $Project `
        -Repo $Repo `
        -PoolId $Pool `
        -ProviderId $Provider `
        -ServiceAccountId $ServiceAccount

    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-GcpConfigureGithub {
    if ([string]::IsNullOrWhiteSpace($Project) -or [string]::IsNullOrWhiteSpace($Repo)) {
        Write-Error "Usage: .\make.ps1 gcp-configure-github -Project <gcp-project-id> -Repo <owner/repo> [-Region us-central1] [-ArtifactLocation us] [-ArtifactRepo antigravity] [-Pipeline dashboard-api] [-StagingService dashboard-api-staging] [-ProductionService dashboard-api-production] [-WifProvider <provider>] [-ServiceAccountEmail <email>]"
        exit 1
    }

    $args = @(
        '-Repo', $Repo,
        '-ProjectId', $Project,
        '-Region', $Region,
        '-ArtifactHost', "$ArtifactLocation-docker.pkg.dev",
        '-ArtifactRepo', $ArtifactRepo,
        '-ImageName', $ImageName,
        '-Pipeline', $Pipeline,
        '-StagingService', $StagingService,
        '-ProductionService', $ProductionService
    )

    if (-not [string]::IsNullOrWhiteSpace($WifProvider)) {
        $args += @('-WifProvider', $WifProvider)
    }
    if (-not [string]::IsNullOrWhiteSpace($ServiceAccountEmail)) {
        $args += @('-ServiceAccount', $ServiceAccountEmail)
    }

    & "$PSScriptRoot\infra\gcp\configure_github.ps1" @args

    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-GcpProxy {
    if ([string]::IsNullOrWhiteSpace($Project)) {
        Write-Error "Usage: .\make.ps1 gcp-proxy -Project <gcp-project-id> [-Service dashboard-api-staging] [-Region us-central1]"
        exit 1
    }

    $svc = if ([string]::IsNullOrWhiteSpace($Service)) { $StagingService } else { $Service }

    Write-Info "[PROXY] Opening local proxy to Cloud Run service: $svc"
    Write-Info "[INFO] Project: $Project  Region: $Region"
    Write-Info "[INFO] Press Ctrl+C to stop the proxy."
    Write-Info ""
    gcloud run services proxy $svc --project $Project --region $Region
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-GcpProxyFrontend {
    if ([string]::IsNullOrWhiteSpace($Project)) {
        Write-Error "Usage: .\make.ps1 gcp-proxy-frontend -Project <gcp-project-id> [-Service agent-dashboard-staging] [-Region us-central1]"
        exit 1
    }

    $svc = if ([string]::IsNullOrWhiteSpace($Service)) { "agent-dashboard-staging" } else { $Service }

    Write-Info "[PROXY] Opening local proxy to frontend dashboard: $svc"
    Write-Info "[INFO] Project: $Project  Region: $Region"
    Write-Info "[INFO] Press Ctrl+C to stop the proxy."
    Write-Info ""
    gcloud run services proxy $svc --project $Project --region $Region
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

function Invoke-Help {
    python scripts/render_command_help.py --shell powershell
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# ==============================================================================
# Main Command Router
# ==============================================================================

$targetMap = @{
    "help"                    = { Invoke-Help }
    "install"                 = { Invoke-Install }
    "codex-preflight"         = { Invoke-CodexPreflight }
    "codex-preflight-full"    = { Invoke-CodexPreflightFull }
    "start"                   = { Invoke-Start }
    "stop"                    = { Invoke-Stop }
    "dev-reset"               = { Invoke-DevReset }
    "dev-up"                  = { Invoke-DevUp }
    "dev-down"                = { Invoke-DevDown }
    "dev-health"              = { Invoke-DevHealth }
    "dev-logs"                = { Invoke-DevLogs }
    "dev-logs-recent"         = { Invoke-DevLogsRecent }
    "dev-logs-service"        = { Invoke-DevLogsService }
    "dev-logs-service-recent" = { Invoke-DevLogsServiceRecent }
    "dev-build"               = { Invoke-DevBuild }
    "dev-up-adk"              = { Invoke-DevUpAdk }
    "dev-wait-health"         = { Invoke-DevWaitHealth }
    "dev-docker-status"       = { Invoke-DevDockerStatus }
    "dev-verify"              = { Invoke-DevVerify }
    "test"                    = { Invoke-Test }
    "test-agent"              = { Invoke-TestAgent }
    "test-fast"               = { Invoke-TestFast }
    "test-pytest"             = { Invoke-TestPytest }
    "verify"                  = { Invoke-Verify }
    "lint"                    = { Invoke-Lint }
    "type-check"              = { Invoke-TypeCheck }
    "type-check-fast"         = { Invoke-TypeCheckFast }
    "type-check-full"         = { Invoke-TypeCheckFull }
    "type-check-backend"      = { Invoke-TypeCheckBackend }
    "type-check-frontend"     = { Invoke-TypeCheckFrontend }
    "frontend-lint"           = { Invoke-FrontendLint }
    "frontend-build"          = { Invoke-FrontendBuild }
    "frontend-test"           = { Invoke-FrontendTest }
    "frontend-e2e-docker"     = { Invoke-FrontendE2EDocker }
    "reset"                   = { Invoke-Reset }
    "clean"                   = { Invoke-Clean }
    "build"                   = { Invoke-Build }
    "docs-generate"           = { Invoke-DocsGenerate }
    "docs-check"              = { Invoke-DocsCheck }
    "command-catalog-check"   = { Invoke-CommandCatalogCheck }
    "playground"              = { Invoke-Playground }
    "playground-base"         = { Invoke-PlaygroundBase }
    "playground-researcher"   = { Invoke-PlaygroundResearcher }
    "gcp-bootstrap"           = { Invoke-GcpBootstrap }
    "gcp-setup-wif"           = { Invoke-GcpSetupWif }
    "gcp-configure-github"    = { Invoke-GcpConfigureGithub }
    "gcp-proxy"               = { Invoke-GcpProxy }
    "gcp-proxy-frontend"      = { Invoke-GcpProxyFrontend }
}

if ([string]::IsNullOrWhiteSpace($Target)) {
    Write-Error "No target specified."
    Write-Info ""
    Write-Info "Available targets:"
    $targetMap.Keys | Sort-Object | ForEach-Object { Write-Info "  $_" }
    Write-Info ""
    Write-Info "Usage: .\make.ps1 <target> [options]"
    Write-Info "Examples:"
    Write-Info "  .\make.ps1 install"
    Write-Info "  .\make.ps1 dev-up"
    Write-Info "  .\make.ps1 test-agent -Agent researcher_agent"
    Write-Info "  .\make.ps1 dev-logs-service -Service phoenix"
    exit 1
}

if ($targetMap.ContainsKey($Target)) {
    & $targetMap[$Target]
}
else {
    Write-Error "Unknown target: $Target"
    Write-Info ""
    Write-Info "Available targets:"
    $targetMap.Keys | Sort-Object | ForEach-Object { Write-Info "  $_" }
    exit 1
}
