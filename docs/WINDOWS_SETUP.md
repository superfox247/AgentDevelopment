# Windows Setup Guide

> **Last verified**: 2026-01-26

This guide covers setting up the Antigravity Agent Platform on Windows.

## 📋 Prerequisites

### Required Software

1. **Docker Desktop for Windows**
   - Download from [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Enable WSL 2 backend (recommended) or Hyper-V
   - Ensure Docker Desktop is running before proceeding

2. **Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Or use Windows Store version
   - Ensure Python is added to PATH during installation

3. **Node.js 20+**
   - Download from [nodejs.org](https://nodejs.org/)
   - Includes npm (pnpm will be installed via npm)

4. **PowerShell 5.1+ or PowerShell 7+**
   - Windows 10/11 includes PowerShell 5.1
   - PowerShell 7+ recommended: [PowerShell GitHub](https://github.com/PowerShell/PowerShell/releases)

### Package Managers

1. **uv** (Python package manager)
   - Install via PowerShell:
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - Or download from [uv GitHub](https://github.com/astral-sh/uv)

2. **pnpm** (Node.js package manager)
   - Install via npm:
     ```powershell
     npm install -g pnpm
     ```

## 🚀 Installation Steps

### 1. Clone the Repository

```powershell
git clone <repository-url>
cd ai-agent-architecture
```

### 2. Set Up API Keys

**Important**: Set `GEMINI_API_KEY` in Windows environment variables (not in `.env` file).

#### Option A: Via Windows GUI
1. Open **System Properties** → **Environment Variables**
2. Under **User variables** (or **System variables**), click **New**
3. Variable name: `GEMINI_API_KEY`
4. Variable value: Your Gemini API key
5. Click **OK** to save

#### Option B: Via PowerShell (User-level)
```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your_api_key_here', [System.EnvironmentVariableTarget]::User)
```

#### Option C: Via PowerShell (System-level - requires admin)
```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your_api_key_here', [System.EnvironmentVariableTarget]::Machine)
```

**Note**: After setting the variable, restart your PowerShell terminal for changes to take effect.

### 3. Set Python UTF-8 Mode (Recommended)

To avoid UnicodeDecodeError issues with LiteLLM on Windows:

```powershell
# Set for current session
$env:PYTHONUTF8 = "1"

# Set persistently for the user
[System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
```

### 4. Install Dependencies

```powershell
# Install Python dependencies (uv will be used automatically)
.\make.ps1 install

# Or manually:
uv sync --dev
cd frontend
pnpm install
cd ..
```

### 5. Verify Installation

```powershell
# Check Docker is running
docker --version
docker compose version

# Check Python and uv
python --version
uv --version

# Check Node.js and pnpm
node --version
pnpm --version

# Verify API key is loaded
.\make.ps1 dev-health
```

## 🐳 Docker Setup

### Starting the Development Stack

```powershell
# Start all Docker services
.\make.ps1 dev-up

# Or full reset (stop, rebuild, start)
.\make.ps1 dev-reset
```

### Viewing Logs

```powershell
# View all logs (live)
.\make.ps1 dev-logs

# View recent logs (last 50 lines)
.\make.ps1 dev-logs-recent

# View logs for specific service
.\make.ps1 dev-logs-service -Service phoenix
```

### Stopping Services

```powershell
# Stop all services
.\make.ps1 dev-down
```

## 🖥 Running the Dashboard

The Dashboard consists of two components that need to run separately:

### Terminal 1: Dashboard API

```powershell
uv run python dashboard_api/server.py
```

The API will run on `http://localhost:8010`

### Terminal 2: Frontend Dev Server

```powershell
cd frontend
pnpm dev
```

The frontend will run on `http://localhost:5173` and proxy `/api` requests to the backend.

## 🔧 Common Windows-Specific Issues

### Issue: "Execution Policy" Error

If you see an execution policy error when running `.\make.ps1`:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set execution policy for current user (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Docker Not Starting

1. Ensure Docker Desktop is running
2. Check WSL 2 is enabled (if using WSL 2 backend)
3. Restart Docker Desktop
4. Verify Docker is accessible: `docker ps`

### Issue: API Key Not Found

1. Verify the key is set: `$env:GEMINI_API_KEY` (should show your key)
2. If empty, restart PowerShell terminal after setting the variable
3. Check both User and Machine-level variables
4. Verify `.\make.ps1` loads it: Check output when running `.\make.ps1 dev-up`

### Issue: Path Issues with Spaces

If your project path contains spaces, use quotes:

```powershell
cd "C:\Users\Your Name\Workspace\ai-agent-architecture"
```

### Issue: Line Ending Differences

Git should handle this automatically, but if you see issues:

```powershell
# Configure Git to handle line endings
git config core.autocrlf true
```

## 📚 Next Steps

- Read [WINDOWS_COMPATIBILITY.md](WINDOWS_COMPATIBILITY.md) for Windows-specific compatibility notes
- See [DEVELOPMENT.md](DEVELOPMENT.md) for development workflow
- See [OPERATIONS.md](OPERATIONS.md) for operations and troubleshooting

## 🔗 Quick Reference

| Task | Command |
|------|---------|
| Start dev stack | `.\make.ps1 dev-up` |
| Stop dev stack | `.\make.ps1 dev-down` |
| Reset environment | `.\make.ps1 dev-reset` |
| Check health | `.\make.ps1 dev-health` |
| View logs | `.\make.ps1 dev-logs` |
| Run tests | `.\make.ps1 test` |
| Lint code | `.\make.ps1 lint` |
