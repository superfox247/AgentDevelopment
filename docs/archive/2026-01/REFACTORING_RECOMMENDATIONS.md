# Refactoring & Improvement Recommendations

This document outlines recommended improvements and refactorings for the Antigravity codebase, organized by priority and category.

## 🔴 High Priority

### 1. Extract CORS Configuration to Shared Module
**Issue**: CORS configuration is duplicated in `agent_platform/server.py` and `frontend/server.py` with identical logic.

**Impact**: Code duplication, maintenance burden, risk of configuration drift.

**Solution**:
- Create `agent_platform/middleware/cors.py` with a shared `setup_cors(app: FastAPI)` function
- Both servers import and use the shared function
- Centralizes CORS logic for easier updates

**Files Affected**:
- `agent_platform/server.py` (lines 89-102)
- `frontend/server.py` (lines 33-48)

---

### 2. Replace `dict` Return Types with Pydantic Models
**Issue**: Several endpoints return `dict` instead of proper Pydantic response models, reducing type safety and API documentation quality.

**Impact**: Loss of type safety, no automatic OpenAPI schema generation, harder to maintain.

**Solution**: Create Pydantic models for all endpoint responses.

**Endpoints to Fix**:
- `frontend/routers/docker.py`:
  - `control_container()` → `ContainerControlResponse` (already exists in models.py but not used)
  - `get_container_logs()` → `ContainerLogsResponse` (already exists in models.py but not used)
- `frontend/routers/agents.py`:
  - `generate_image()` → `ImageGenerationResponse` (needs to be created)
- `frontend/routers/system.py`:
  - `_test_single_model()` → `ModelTestResponse` (internal helper, but should still be typed)
  - `get_quota_detail()` → `QuotaDetailResponse` (needs to be created)
  - `get_metric_timeseries()` → `MetricTimeseriesResponse` (needs to be created)

**Files Affected**:
- `frontend/routers/docker.py` (lines 67, 120)
- `frontend/routers/agents.py` (line 184)
- `frontend/routers/system.py` (lines 337, 387)
- `frontend/routers/usage.py` (lines 200, 240)
- `frontend/models.py` (add missing models)

---

### 3. Remove Hardcoded Model Names
**Issue**: Hardcoded model names like `"gemini-1.5-flash"` appear in multiple places.

**Impact**: Difficult to change defaults, inconsistent with config system.

**Solution**: Use `PlatformConfig.default_model` and `PlatformConfig.default_image_model` consistently.

**Locations**:
- `frontend/routers/agents.py` line 194: `model_to_use = "gemini-1.5-flash"`
- Check for other hardcoded model references

**Files Affected**:
- `frontend/routers/agents.py`
- Potentially other router files

---

### 4. Standardize Error Response Format
**Issue**: Error responses are inconsistent - some use `{"error": "message"}`, others use `{"detail": "message"}`.

**Impact**: Frontend must handle multiple error formats, inconsistent API experience.

**Solution**: 
- Use FastAPI's standard `HTTPException` with `detail` field consistently
- Create a custom exception handler if needed for standardized error envelope
- Update frontend client to expect consistent format

**Files Affected**:
- `frontend/routers/docker.py` (line 41, 56, 59 use `{"error": ...}`)
- All router files should use `HTTPException` consistently

---

## 🟡 Medium Priority

### 5. Extract Docker Error Handling to Shared Utility
**Issue**: Docker error handling logic is repeated across multiple endpoints in `docker.py`.

**Impact**: Code duplication, harder to maintain consistent error handling.

**Solution**: Create `frontend/utils/docker_utils.py` with helper functions:
- `get_container_safe(client, container_id)` - handles NotFound/APIError
- `execute_container_action(container, action)` - handles action execution errors

**Files Affected**:
- `frontend/routers/docker.py`

---

### 6. Improve Type Safety in Event Processing
**Issue**: `_extract_event_data()` in `agents.py` returns `dict | None` with manual type checking.

**Impact**: Loss of type safety, potential runtime errors.

**Solution**: Create Pydantic models for event data types:
- `ToolUseEvent`
- `AgentThoughtEvent`
- `UserMessageEvent`
- `SystemSignalEvent`

Use discriminated unions or a base class with type field.

**Files Affected**:
- `frontend/routers/agents.py`
- `frontend/models.py` (add event models)

---

### 7. Consolidate Configuration Access
**Issue**: Some code accesses `os.environ` directly instead of using `PlatformConfig`.

**Impact**: Inconsistent configuration access, harder to validate and test.

**Solution**: 
- Ensure all configuration goes through `PlatformConfig` or `get_config()`
- Create a configuration module for frontend if needed
- Document all environment variables in one place

**Files Affected**:
- `frontend/server.py` (lines 34-40 access `os.environ` directly)
- Check other files for direct `os.environ` usage

---

### 8. Add Missing Response Models
**Issue**: Several endpoints return responses that aren't properly modeled.

**Solution**: Create Pydantic models for:
- `ImageGenerationResponse` (for `/api/generate/image`)
- `ContainerControlResponse` (already exists but not used)
- `ContainerLogsResponse` (for log endpoints)
- `QuotaDetailResponse` (for usage endpoints)
- `MetricTimeseriesResponse` (for metrics endpoints)

**Files Affected**:
- `frontend/models.py`
- All router files using these responses

---

### 9. Improve Test Coverage
**Issue**: Limited test files found (only 4 test files in codebase).

**Impact**: Risk of regressions, harder to refactor safely.

**Solution**: 
- Add unit tests for router endpoints
- Add integration tests for Docker operations
- Add tests for configuration validation
- Add tests for error handling paths

**Priority Areas**:
- `frontend/routers/docker.py` - critical infrastructure code
- `agent_platform/config.py` - configuration validation
- `agent_platform/auth/dependencies.py` - authentication logic
- `frontend/routers/system.py` - system status logic

---

### 10. Extract Hardcoded Service Names
**Issue**: Service names like `"orchestrator"`, `"content_builder"` are hardcoded in multiple places.

**Impact**: Difficult to add new services, inconsistent naming.

**Solution**: 
- Create a `ServiceRegistry` or constants file
- Use enum or constants for service names
- Make service discovery more dynamic

**Files Affected**:
- `frontend/routers/system.py` (service status checks)
- `docker-compose.yml` (container names)

---

## 🟢 Low Priority / Nice to Have

### 11. Improve Logging Consistency
**Issue**: Some modules use `logger.info()`, others use `logger.error()` inconsistently.

**Solution**: 
- Define logging levels consistently
- Use structured logging with context
- Consider adding request ID tracking

**Files Affected**: All router and service files

---

### 12. Add Request Validation Middleware
**Issue**: Some endpoints don't validate request size or rate limits consistently.

**Solution**: 
- Add request size limits
- Ensure rate limiting is applied consistently
- Add request ID middleware for tracing

**Files Affected**:
- `agent_platform/middleware.py`
- `frontend/server.py`

---

### 13. Improve Documentation
**Issue**: Some complex functions lack docstrings or have incomplete ones.

**Solution**: 
- Add comprehensive docstrings to all public functions
- Document complex algorithms (e.g., event extraction)
- Add examples to API documentation

**Files Affected**: All router and service files

---

### 14. Refactor Large Functions
**Issue**: Some functions are doing too much (e.g., `get_status()` in `system.py`).

**Solution**: 
- Break down large functions into smaller, testable units
- Extract helper functions
- Use composition over large conditional blocks

**Files Affected**:
- `frontend/routers/system.py` (`get_status()` and helpers)
- `frontend/routers/agents.py` (`_customer_service_event_generator()`)

---

### 15. Add Input Validation
**Issue**: Some endpoints accept string parameters without validation (e.g., `action` in `control_container`).

**Solution**: 
- Use Pydantic models for path/query parameters where possible
- Add enum types for constrained values (e.g., `ContainerAction` enum)
- Validate string lengths and formats

**Files Affected**:
- `frontend/routers/docker.py` (action parameter)
- Other routers with string parameters

---

### 16. Improve Async Error Handling
**Issue**: Some async functions don't properly handle cancellation or timeout errors.

**Solution**: 
- Add timeout handling for long-running operations
- Properly handle `asyncio.CancelledError`
- Add context managers for resource cleanup

**Files Affected**:
- `frontend/routers/agents.py` (streaming endpoints)
- `frontend/routers/system.py` (async operations)

---

### 17. Add Health Check Improvements
**Issue**: Health checks are basic and don't verify dependencies.

**Solution**: 
- Add dependency health checks (Docker, database, external APIs)
- Add readiness vs liveness probes
- Return detailed health status

**Files Affected**:
- `agent_platform/server.py` (`/health` endpoint)
- `frontend/server.py` (`/health` endpoint)

---

### 18. Consolidate Import Organization
**Issue**: Some files have imports in inconsistent order or locations.

**Solution**: 
- Use `ruff` to organize imports automatically
- Follow PEP 8 import ordering
- Group imports: stdlib, third-party, local

**Files Affected**: All Python files

---

## 📊 Summary Statistics

- **High Priority**: 4 items
- **Medium Priority**: 6 items  
- **Low Priority**: 8 items
- **Total**: 18 recommendations

## 🎯 Quick Wins (Can be done in < 1 hour each)

1. Extract CORS configuration (#1)
2. Replace `dict` return types with existing models (#2 - partial)
3. Remove hardcoded model names (#3)
4. Standardize error responses (#4)
5. Add missing response models (#8)

## 🔄 Refactoring Order Recommendation

1. **Week 1**: High priority items (#1-4)
2. **Week 2**: Medium priority items (#5-9)
3. **Week 3**: Low priority items (#10-18)

## 📝 Notes

- All changes should maintain backward compatibility where possible
- Add tests before refactoring when possible (TDD approach)
- Update documentation as you go
- Consider creating ADRs (Architecture Decision Records) for significant changes
