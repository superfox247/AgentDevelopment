# Development Guide (Compatibility)

This file is retained for link compatibility.

Canonical development workflow documentation now lives in:

- [Platform Guide](../PLATFORM_GUIDE.md)

Primary local flow:

1. `make install`
2. `make dev-up`
3. `uv run python dashboard_api/server.py`
4. `cd frontend && pnpm dev`
5. `make dev-verify`

For GCP setup and CI/CD bootstrap, also use [Platform Guide](../PLATFORM_GUIDE.md).
