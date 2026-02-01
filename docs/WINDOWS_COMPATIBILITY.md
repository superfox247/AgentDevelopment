# Windows Compatibility Guide

> **Last verified**: 2026-01-26

This document covers Windows-specific compatibility considerations and differences from Unix/Linux/Mac environments.

## 🔑 Key Differences

### Command Execution

- **Use `.\make.ps1` instead of `make`**
  - All Makefile commands have PowerShell equivalents
  - Example: `.\make.ps1 dev-up` instead of `make dev-up`

### Environment Variables

- **Windows Environment Variables**: Set `GEMINI_API_KEY` in Windows (User or System), not in `.env`
- **Automatic Loading**: `.\make.ps1` automatically loads `GEMINI_API_KEY` from Windows environment variables
- **No Manual Steps**: Unlike Unix systems, you don't need to export variables in each terminal session

### File Paths

- **Use Backslashes**: Windows uses `\` for paths (though PowerShell accepts `/`)
- **Case Sensitivity**: Windows file system is case-insensitive (unlike Linux/Mac)
- **Spaces in Paths**: Use quotes around paths with spaces

## 🐍 Python-Specific Considerations

### UTF-8 Encoding

Windows may use `cp1252` encoding by default, which can cause issues with LiteLLM:

**Solution**: Set `PYTHONUTF8=1` environment variable:

```powershell
# Set for current session
$env:PYTHONUTF8 = "1"

# Set persistently
[System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
```

This prevents `UnicodeDecodeError` when LiteLLM reads cached files.

### Virtual Environments

- **Activation**: Use `.venv\Scripts\Activate.ps1` (PowerShell) or `.venv\Scripts\activate.bat` (CMD)
- **uv**: Handles virtual environments automatically, no manual activation needed

### Python Path

- Ensure Python is in your PATH
- Use `python --version` to verify
- If multiple Python versions exist, use full path or py launcher: `py -3.11`

## 🐳 Docker Considerations

### Docker Desktop

- **WSL 2 Backend**: Recommended for better performance
- **Hyper-V Backend**: Alternative if WSL 2 is not available
- **File Sharing**: Ensure project directory is shared with Docker Desktop

### Volume Mounts

- **Path Format**: Docker Compose handles Windows paths automatically
- **Case Sensitivity**: Docker containers are Linux-based (case-sensitive), but Windows mounts handle this

### Networking

- **Port Binding**: Same as Linux/Mac (`localhost:8000`, etc.)
- **Firewall**: Windows Firewall may prompt for Docker Desktop access - allow it

## 📝 PowerShell vs CMD

### Recommended: PowerShell

- **Better Scripting**: `make.ps1` is optimized for PowerShell
- **Modern Features**: Better error handling and object support
- **Cross-Platform**: PowerShell Core works on Linux/Mac too

### CMD Alternative

If you must use CMD:
- Use `docker compose` commands directly
- Set environment variables: `set GEMINI_API_KEY=your_key`
- Use `.venv\Scripts\activate.bat` for virtual environments

## 🔧 make.ps1 Features

The `make.ps1` script provides Windows-optimized equivalents of all Makefile commands:

### Automatic API Key Loading

```powershell
# make.ps1 automatically loads GEMINI_API_KEY from Windows
# Checks User-level first, then Machine-level
.\make.ps1 dev-up  # API key loaded automatically
```

### Error Handling

- **Stops on Error**: `$ErrorActionPreference = "Stop"` ensures failures are caught
- **Clear Messages**: Color-coded output (Cyan=info, Green=success, Red=error, Yellow=warning)

### Command Equivalents

| Unix/Mac | Windows PowerShell |
|----------|-------------------|
| `make dev-up` | `.\make.ps1 dev-up` |
| `make dev-down` | `.\make.ps1 dev-down` |
| `make dev-reset` | `.\make.ps1 dev-reset` |
| `make test` | `.\make.ps1 test` |
| `make lint` | `.\make.ps1 lint` |

## 🚨 Known Issues & Workarounds

### Issue: Execution Policy Restrictions

**Symptom**: "cannot be loaded because running scripts is disabled"

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Long Path Names

**Symptom**: File path too long errors

**Solution**: Enable long path support in Windows:
1. Open Group Policy Editor (`gpedit.msc`)
2. Navigate to: Computer Configuration → Administrative Templates → System → Filesystem
3. Enable "Enable Win32 long paths"

Or set registry key:
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Issue: Line Endings in Scripts

**Symptom**: Scripts fail with syntax errors

**Solution**: Git should handle this, but if issues occur:
```powershell
git config core.autocrlf true
```

### Issue: Docker Desktop WSL 2 Integration

**Symptom**: Docker commands fail or containers don't start

**Solution**:
1. Ensure WSL 2 is installed: `wsl --install`
2. Update WSL 2: `wsl --update`
3. Restart Docker Desktop
4. Verify: `docker info` should show WSL 2 backend

## 📊 Performance Considerations

### File System Performance

- **WSL 2**: Better performance than Hyper-V for file operations
- **Volume Mounts**: Project files should be in WSL 2 filesystem (`\\wsl$\`) for best performance
- **Docker Volumes**: Use named volumes for databases (Qdrant, Neo4j) for better performance

### Resource Usage

- **Memory**: Docker Desktop defaults to 2GB - increase if running multiple agents
- **CPU**: Allocate more CPUs in Docker Desktop settings if available
- **Disk**: Docker images and volumes can use significant space - monitor with `docker system df`

## 🔗 Related Documentation

- [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Complete Windows setup guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development workflow (includes Windows notes)
- [OPERATIONS.md](OPERATIONS.md) - Operations and troubleshooting
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide

## 💡 Tips for Windows Users

1. **Use PowerShell**: Better experience than CMD
2. **Set Environment Variables Once**: Use Windows GUI or PowerShell, then forget about it
3. **Keep Docker Desktop Running**: Start it before development sessions
4. **Use WSL 2**: Better performance and compatibility
5. **Monitor Resources**: Docker Desktop can be resource-intensive
6. **Check Logs**: Use `.\make.ps1 dev-logs-recent` when things go wrong
