# API Standards & Security

This guide codifies the communication protocols and security requirements for the Agent Central API layer.

## 1. Response Architecture: The Envelope Pattern
To ensure extensibility and security, all API responses must return a top-level JSON object rather than a naked array.

### A. Pattern
- **Requirement**: `{"items": [...], "count": N, "metadata": {...}}`
- **Security**: Mitigates legacy Cross-Site Script Inclusion (JSON Hijacking) vulnerabilities (OWASP standard).
- **Stability**: Allows adding fields (e.g., pagination) without breaking legacy clients.
- **Standard Client**: Handled automatically by the [Centralized API Client](./implementation/centralized_api_client.md).

### B. Implementation (FastAPI/Pydantic)
```python
class GenericEnvelope(BaseModel, Generic[T]):
    items: list[T]
    count: int | None = None
```

## 2. Real-time Telemetry: SSE Protocol
Server-Sent Events (SSE) is the project standard for unidirectional telemetry (logs, status).

### A. Requirements
- **Format**: `data: {payload}\n\n` (Always JSON-encoded strings).
- **Status Events**: Use `event: status` for connection lifecycle metadata.
- **Heartbeat**: Yield periodic empty data or comments to prevent proxy timeouts.
- **Cleanup**: Frontend must explicitly call `es.close()` on component unmount to prevent leaked connections.

## 3. Security & OWASP Standards
Under the 2026 Fleet Standard, the API layer implements the following defenses:

### A. Security Headers
The FastAPI application enforces headers via a dedicated middleware.
- **Reference**: [Implementation: Security Middleware](./implementation/security_middleware.md)
- **Key Headers**: `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`.

### B. Input Validation
- All inputs must be strictly validated via Pydantic models.
- **Zero-Any Policy**: Use of `Any` in API models is prohibited.

### C. CORS Management
- Production: Strict origin allow-listing.
- Development: Proxied via Vite (`localhost:5173 -> localhost:8010`) to maintain secure-context headers.

## 4. Resilience
- **Async Threadpool**: Wrap blocking calls (Docker SDK, File I/O) in `run_in_threadpool` to prevent event loop stalls.
- **Response Model Safety**: Use `@app.get(..., response_model=None)` and `fastapi.Response` return hints for multi-modal or streaming endpoints to avoid Pydantic union validation crashes during startup.
