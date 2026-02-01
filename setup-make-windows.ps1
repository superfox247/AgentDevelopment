# Quick Setup Script for make on Windows
# This script helps you install make on Windows

Write-Host "=== Make Installation Helper for Windows ===" -ForegroundColor Cyan
Write-Host ""

# Check if make is already installed
if (Get-Command make -ErrorAction SilentlyContinue) {
    Write-Host "✓ make is already installed!" -ForegroundColor Green
    make --version
    exit 0
}

Write-Host "make is not installed. Choose an installation method:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Install via Scoop (Recommended - No admin required)" -ForegroundColor Cyan
Write-Host "2. Install via Chocolatey (Requires admin)" -ForegroundColor Cyan
Write-Host "3. Manual installation instructions" -ForegroundColor Cyan
Write-Host "4. Exit" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Installing Scoop and make..." -ForegroundColor Yellow
        
        # Check if Scoop is installed
        if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
            Write-Host "Installing Scoop..." -ForegroundColor Yellow
            Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
            try {
                Invoke-RestMethod get.scoop.sh | Invoke-Expression
                Write-Host "✓ Scoop installed successfully!" -ForegroundColor Green
            } catch {
                Write-Host "✗ Failed to install Scoop: $_" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "✓ Scoop is already installed" -ForegroundColor Green
        }
        
        # Install make
        Write-Host "Installing make..." -ForegroundColor Yellow
        try {
            scoop install make
            Write-Host ""
            Write-Host "✓ make installed successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "You can now use 'make' commands:" -ForegroundColor Cyan
            Write-Host "  make install" -ForegroundColor White
            Write-Host "  make dev-up" -ForegroundColor White
            Write-Host "  make test" -ForegroundColor White
        } catch {
            Write-Host "✗ Failed to install make: $_" -ForegroundColor Red
            exit 1
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Installing via Chocolatey (requires admin)..." -ForegroundColor Yellow
        
        # Check if Chocolatey is installed
        if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
            Write-Host "Chocolatey is not installed." -ForegroundColor Yellow
            Write-Host "To install Chocolatey, run PowerShell as Administrator and execute:" -ForegroundColor Cyan
            Write-Host 'Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(''https://community.chocolatey.org/install.ps1''))' -ForegroundColor White
            Write-Host ""
            Write-Host "Then run this script again and choose option 2." -ForegroundColor Yellow
            exit 1
        }
        
        # Install make
        Write-Host "Installing make..." -ForegroundColor Yellow
        try {
            choco install make -y
            Write-Host ""
            Write-Host "✓ make installed successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "You can now use 'make' commands:" -ForegroundColor Cyan
            Write-Host "  make install" -ForegroundColor White
            Write-Host "  make dev-up" -ForegroundColor White
            Write-Host "  make test" -ForegroundColor White
        } catch {
            Write-Host "✗ Failed to install make: $_" -ForegroundColor Red
            exit 1
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "=== Manual Installation Options ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Option A: Download from GNUWin32" -ForegroundColor Yellow
        Write-Host "  1. Visit: https://gnuwin32.sourceforge.net/packages/make.htm" -ForegroundColor White
        Write-Host "  2. Download and install make" -ForegroundColor White
        Write-Host "  3. Add installation directory to PATH" -ForegroundColor White
        Write-Host ""
        Write-Host "Option B: Use WSL (Windows Subsystem for Linux)" -ForegroundColor Yellow
        Write-Host "  1. Run: wsl --install (as Administrator)" -ForegroundColor White
        Write-Host "  2. Use make in WSL terminal" -ForegroundColor White
        Write-Host ""
        Write-Host "Option C: Use MSYS2" -ForegroundColor Yellow
        Write-Host "  1. Download from: https://www.msys2.org/" -ForegroundColor White
        Write-Host "  2. Install and run: pacman -S make" -ForegroundColor White
        Write-Host ""
        Write-Host "For more details, see: docs/WINDOWS_SETUP.md" -ForegroundColor Cyan
    }
    
    "4" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
