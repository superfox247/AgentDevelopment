---
description: Testing workflow - run comprehensive tests with easy-to-view logs
---

# Testing Workflow

**Phase**: Post-Implementation  
**Purpose**: Run comprehensive tests with easy-to-view logs for debugging.

## Objectives

1. Run all test layers in logical order
2. Review logs for any failures
3. Determine if failures indicate wider issues
4. Fix issues or plan refactoring
5. Verify all tests pass

## Test Layers

Follow the 5-layer testing pyramid (from `docs/TESTING.md`):

1. **Layer 1: Unit Tests** - Fastest, most critical
2. **Layer 2: Agent Structure Tests** - Agent configuration
3. **Layer 3: Integration Tests** - Service boundaries
4. **Layer 4: Component Tests** - Frontend components
5. **Layer 5: E2E Tests** - Full system (slowest)

## Steps

### Step 1: Prepare Testing Environment

**Action**: Ensure testing environment is ready

**Tasks**:
1. Reset dev environment (if needed)
2. Start Docker stack
3. Verify services are healthy
4. Check logs are accessible

**Commands**:
```bash
# Reset environment (if needed)
make dev-reset

# Or just start if already clean
make dev-up

# Verify health
make dev-health
```

**Output**: Clean testing environment ready

---

### Step 2: Run Layer 1 - Unit Tests

**Action**: Run unit tests (fastest, most critical)

**Location**: Colocated with source files (`test_*.py`)

**Commands**:
```bash
# Run all unit tests
uv run pytest agent_platform/ -v
uv run pytest dashboard_api/ -v
uv run pytest agents/*/tests/ -v

# Or use smart test runner
make test-fast
```

**Log Viewing**:
```bash
# View test output (pytest shows logs)
# Check for any failures or warnings
```

**Requirements**:
- ✅ All unit tests pass
- ✅ No warnings
- ✅ Clean output

**If Failures**:
- Review test output
- Check logs: `make dev-logs-recent`
- Fix issue or document in `.agent/issues.md`

**Output**: All unit tests passing

---

### Step 3: Run Layer 2 - Agent Structure Tests

**Action**: Run agent configuration and structure tests

**Location**: `agents/<agent>/tests/`

**Commands**:
```bash
# Run agent tests
make test-agent AGENT=agent_name

# Or specific agent tests
uv run pytest agents/agent_name/tests/ -v
```

**Log Viewing**:
```bash
# View test output
# Check Docker logs if agent uses Docker
make dev-logs-recent
```

**Requirements**:
- ✅ All agent tests pass
- ✅ Agent discovery works
- ✅ Agent metadata correct

**If Failures**:
- Review agent configuration
- Check agent registry
- Fix issue or document

**Output**: All agent structure tests passing

---

### Step 4: Run Layer 3 - Integration Tests

**Action**: Run integration tests (if applicable)

**Location**: `tests/integration/`

**Commands**:
```bash
# Run integration tests
uv run pytest tests/integration/ -v

# Or via test runner
make test-fast
```

**Log Viewing**:
```bash
# View test output
# Check service logs
make dev-logs-recent
```

**Requirements**:
- ✅ All integration tests pass
- ✅ Services integrate correctly

**If Failures**:
- Review service interactions
- Check API endpoints
- Check Docker services
- Fix issue or document

**Output**: All integration tests passing

---

### Step 5: Run Layer 4 - Component Tests

**Action**: Run frontend component tests

**Location**: `frontend/tests/components/`

**Commands**:
```bash
# Run component tests
make frontend-test

# Or manually
cd frontend && pnpm test run
```

**Log Viewing**:
```bash
# View test output (Vitest shows logs)
# Check for any failures
```

**Requirements**:
- ✅ All component tests pass
- ✅ No warnings
- ✅ Clean output

**If Failures**:
- Review component code
- Check test setup
- Fix issue or document

**Output**: All component tests passing

---

### Step 6: Run Layer 5 - E2E Tests

**Action**: Run end-to-end tests against Docker stack

**Location**: `frontend/tests/e2e/`

**Prerequisites**:
- Docker stack running
- API server running
- Frontend server running (or built)

**Commands**:
```bash
# Run E2E tests against Docker stack
make frontend-e2e-docker

# Or manually
cd frontend && pnpm exec playwright test --config=playwright.docker.config.ts
```

**Log Viewing**:
```bash
# View E2E test output
# Check Docker logs
make dev-logs-recent

# Check specific service logs
make dev-logs-service SERVICE=phoenix

# Check API logs (from API server terminal)
# Check frontend logs (from frontend server terminal)
```

**Requirements**:
- ✅ All E2E tests pass
- ✅ Full user journeys work
- ✅ System integration verified

**If Failures**:
- Review E2E test output
- Check all service logs
- Check network connectivity
- Fix issue or document

**Output**: All E2E tests passing

---

### Step 7: Failure Analysis

**Action**: Analyze any test failures

**For Each Failure**:

1. **Review Logs**:
   ```bash
   # View recent logs
   make dev-logs-recent
   
   # View specific service logs
   make dev-logs-service SERVICE=service_name
   
   # View health status
   make dev-health
   ```

2. **Understand Failure**:
   - What failed?
   - Why did it fail?
   - What logs show?
   - Is it isolated or systemic?

3. **Assess Impact**:
   - Is this a wider architectural issue?
   - Does it indicate need for refactoring?
   - Is it an isolated bug?

4. **Take Action**:
   - **If wider issue**: Document in `.agent/issues.md`, plan refactor
   - **If isolated issue**: Fix and retry test
   - **If test issue**: Fix test and retry

**Output**: All failures analyzed and addressed

---

### Step 8: Verify Clean Logs

**Action**: Verify all logs are clean after tests

**Check**:
```bash
# Check Docker logs
make dev-logs-recent

# Check service health
make dev-health

# Verify no unexpected errors
# Verify no warnings (unless expected and documented)
```

**Requirements**:
- ✅ No unexpected errors in logs
- ✅ No warnings in logs (unless expected)
- ✅ Services healthy
- ✅ Clean log output

**Output**: Clean logs verified

---

## Testing Checklist

Run through this checklist:

- [ ] Testing environment prepared
- [ ] Layer 1 (Unit Tests): All passing
- [ ] Layer 2 (Agent Tests): All passing
- [ ] Layer 3 (Integration Tests): All passing (if applicable)
- [ ] Layer 4 (Component Tests): All passing
- [ ] Layer 5 (E2E Tests): All passing
- [ ] All failures analyzed
- [ ] All issues fixed or documented
- [ ] All logs clean
- [ ] Services healthy

---

## Exit Criteria

Testing phase is complete when:

- ✅ All test layers pass
- ✅ All failures analyzed and addressed
- ✅ No unresolved issues
- ✅ All logs clean
- ✅ Services healthy
- ✅ Ready for verification phase

---

## Next Phase

After Testing, proceed to: **[Verification Workflow](verification-workflow.md)**
