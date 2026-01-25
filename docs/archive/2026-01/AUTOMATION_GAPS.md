# Automation Gaps & Missing Tests

**Date**: January 25, 2026  
**Purpose**: Identify gaps in automated testing and verification mechanisms

## 🔴 Critical Gaps - New Code Not Tested

### 1. Agent Registry (`frontend/utils/agent_registry.py`)
**Status**: ❌ **NO TESTS**

Missing tests for:
- `extract_agent_metadata()` - AST parsing logic
- `discover_agents()` - Directory scanning
- `AgentRegistry` class - Caching and refresh logic
- Edge cases: malformed agent.py, missing files, invalid AST

**Impact**: Registry failures won't be caught until runtime

### 2. Metadata API Endpoint (`frontend/routers/agents.py`)
**Status**: ❌ **NO TESTS**

Missing tests for:
- `GET /api/agents/{name}/metadata` endpoint
- Response schema validation
- 404 handling for non-existent agents
- Integration with AgentRegistry

**Impact**: API changes could break without detection

### 3. AgentMetadata Model (`frontend/models.py`)
**Status**: ❌ **NO TESTS**

Missing tests for:
- Pydantic validation
- Default values
- Type coercion

**Impact**: Invalid data could pass through

### 4. Frontend Component - Metadata Features
**Status**: ⚠️ **PARTIAL COVERAGE**

`AgentsView.test.tsx` exists but:
- ❌ Doesn't test `getAgentMetadata()` API call
- ❌ Doesn't test metadata display in UI
- ❌ Doesn't test metadata loading states
- ❌ Doesn't test server status indicator
- ❌ Doesn't test model name display

**Impact**: UI regressions won't be caught

## 🟡 CI/CD Pipeline Gaps

### Current CI Jobs
1. ✅ `quality` - Ruff linting, MyPy type checking
2. ✅ `test` - Backend unit tests with coverage
3. ✅ `frontend` - TypeScript check, ESLint, component tests, E2E

### Missing CI Checks

#### Backend API Tests
- ❌ **No FastAPI router tests** - Endpoints not tested in CI
- ❌ **No agent registry tests** - Discovery logic not verified
- ❌ **No integration tests** - Registry + API not tested together

#### Agent Discovery Verification
- ❌ **No automated agent discovery check** - CI doesn't verify agents are discoverable
- ❌ **No metadata extraction validation** - CI doesn't verify AST parsing works
- ❌ **No server.py validation** - CI doesn't check server entry points

#### Schema Validation
- ❌ **No API response schema validation** - Responses not validated against Pydantic models
- ❌ **No OpenAPI spec validation** - API docs not verified

#### End-to-End API Tests
- ❌ **No API smoke tests** - Basic endpoints not tested
- ❌ **No metadata endpoint tests** - New endpoint not in CI

## 🟠 Pre-commit Hook Gaps

### Current Hooks
- ✅ Trailing whitespace, EOF, YAML check
- ✅ Ruff linting and formatting
- ✅ MyPy type checking
- ✅ Codespell
- ✅ ESLint and TypeScript check for frontend

### Missing Hooks
- ❌ **No test execution** - Tests not run before commit
- ❌ **No agent registry validation** - Registry not checked
- ❌ **No API endpoint validation** - FastAPI routes not verified

## 🔵 Test Infrastructure Gaps

### Missing Test Utilities
- ❌ **No FastAPI test client fixtures** - Can't easily test routers
- ❌ **No agent registry test fixtures** - Can't mock agent directories
- ❌ **No API response validators** - Can't validate Pydantic schemas in tests

### Missing Test Coverage
- ❌ **No integration test suite** - Components not tested together
- ❌ **No API contract tests** - Request/response contracts not verified
- ❌ **No agent discovery tests** - Discovery workflow not tested

## 📊 Coverage Analysis

### Backend Coverage
- ✅ `agent_platform/test_config.py` - Config tested
- ✅ `agent_platform/test_observability.py` - Observability tested
- ✅ `agents/researcher_agent/tests/test_tools.py` - Tools tested
- ❌ `frontend/utils/agent_registry.py` - **0% coverage**
- ❌ `frontend/routers/agents.py` - **0% coverage**
- ❌ `frontend/models.py` (AgentMetadata) - **0% coverage**

### Frontend Coverage
- ✅ Component tests exist for AgentsView (partial)
- ❌ Missing tests for metadata features
- ❌ Missing tests for API client `getAgentMetadata()`

## 🎯 Recommended Actions

### Priority 1: Critical Tests (Do First)
1. **Add agent registry unit tests**
   - Test `extract_agent_metadata()` with various agent.py formats
   - Test `discover_agents()` with mock directories
   - Test `AgentRegistry` caching and refresh

2. **Add API endpoint tests**
   - Test `GET /api/agents/{name}/metadata` with FastAPI test client
   - Test 404 handling
   - Test response schema validation

3. **Add AgentMetadata model tests**
   - Test Pydantic validation
   - Test default values

4. **Update AgentsView component tests**
   - Test metadata fetching
   - Test metadata display
   - Test loading states

### Priority 2: CI/CD Integration
1. **Add FastAPI router tests to CI**
   - Create test suite for all router endpoints
   - Add to `test` job in CI

2. **Add agent discovery verification**
   - Create CI job that verifies researcher_agent is discoverable
   - Validates metadata extraction works

3. **Add API contract tests**
   - Validate all API responses match Pydantic schemas
   - Validate OpenAPI spec is up to date

### Priority 3: Pre-commit Enhancements
1. **Add quick test run**
   - Run critical tests before commit (registry, API endpoints)
   - Fast enough to not block development

2. **Add agent registry validation**
   - Verify agents directory structure
   - Check agent.py files are parseable

### Priority 4: Test Infrastructure
1. **Create test fixtures**
   - FastAPI test client fixture
   - Mock agent directory fixture
   - API response validator utility

2. **Add integration test suite**
   - Test registry + API together
   - Test full discovery workflow

## 📝 Implementation Plan

### Phase 1: Unit Tests (Immediate)
- [ ] `test_agent_registry.py` - Registry unit tests
- [ ] `test_agents_router.py` - API endpoint tests
- [ ] `test_models.py` - AgentMetadata model tests
- [ ] Update `AgentsView.test.tsx` - Metadata UI tests

### Phase 2: CI Integration
- [ ] Add router tests to CI `test` job
- [ ] Add agent discovery verification to CI
- [ ] Add API schema validation to CI

### Phase 3: Pre-commit
- [ ] Add registry validation hook
- [ ] Add quick API test hook (optional, fast tests only)

### Phase 4: Infrastructure
- [ ] Create test fixtures module
- [ ] Add integration test suite
- [ ] Add API contract test utilities

## 🔍 Verification Commands

### Current Verification
```bash
# Linting
uv run ruff check .
pnpm lint

# Type checking
uv run mypy .
pnpm exec tsc --noEmit

# Tests
uv run pytest
pnpm test run
```

### Missing Verification
```bash
# Agent registry tests (doesn't exist)
uv run pytest frontend/utils/test_agent_registry.py

# API endpoint tests (doesn't exist)
uv run pytest frontend/routers/test_agents.py

# Agent discovery verification (doesn't exist)
uv run pytest tests/integration/test_agent_discovery.py
```

## 📈 Success Metrics

After implementing fixes:
- ✅ 100% of new code has tests
- ✅ All API endpoints tested in CI
- ✅ Agent registry tested and verified
- ✅ Frontend metadata features tested
- ✅ Pre-commit catches critical issues
- ✅ CI fails on broken agent discovery
