---
description: Intelligent Environment Management
---

# Managing the Development Environment

We use `scripts/start_dev_env.ps1` to ensure the environment is healthy without unnecessary full restarts.

## 1. Start / Recover
This script is **idempotent**. Run it anytime.
- Checks if Docker is running (starts it if not).
- Checks if containers exist.
- Only rebuilds/restarts if configuration changed.

```powershell
.\scripts\start_dev_env.ps1
```

## 2. Viewing Logs
To check why a specific service failed:
```bash
docker-compose logs -f <service_name>
# Example:
docker-compose logs -f orchestrator
```

## 3. Full Reset (Nuclear Option)
Only use this if the environment is strictly corrupted.
```powershell
docker-compose down -v
.\scripts\start_dev_env.ps1
```
