---
description: Code quality workflow - ensure clean builds, no warnings, clean log outputs
---

# Code Quality Workflow

**Phase**: Post-Implementation  
**Purpose**: Ensure code quality, clean builds, and no warnings in any command output.

## Objectives

1. Run all linting and fix issues
2. Run type checking
3. Format code
4. Check for security issues
5. Verify clean build (no warnings)
6. Verify clean log outputs from all commands

## Steps

### Step 1: Linting

**Action**: Run linting and fix all issues

**Backend (Python)**:
```bash
# Run linting (checks and fixes)
make lint

# Or manually:
uv run ruff check . --fix
uv run ruff format .
```

**Frontend (TypeScript/React)**:
```bash
# Run linting
make frontend-lint

# Or manually:
cd frontend && pnpm lint
```

**Requirements**:
- ✅ No linting errors
- ✅ No linting warnings
- ✅ Code formatted correctly

**Output**: Clean linting results

---

### Step 2: Type Checking

**Action**: Run type checking and fix issues

**Backend (Python)**:
```bash
# Run type checking
uv run mypy .
```

**Frontend (TypeScript)**:
```bash
# Run type checking
cd frontend && pnpm exec tsc --noEmit
```

**Requirements**:
- ✅ No type errors
- ✅ No type warnings
- ✅ All types properly defined

**Output**: Clean type checking results

---

### Step 3: Security Checks

**Action**: Check for security issues

**Tasks**:
1. Review code for common vulnerabilities
2. Check dependency versions
3. Review authentication/authorization
4. Check input validation
5. Review error handling (no information leakage)

**Tools**:
- Manual code review
- Dependency scanning (if available)
- Security best practices checklist

**Output**: Security review complete, no issues found

---

### Step 4: Build Verification

**Action**: Verify clean build with no warnings

**Backend Build**:
```bash
# Sync dependencies
uv sync

# Verify no warnings
uv sync --dev 2>&1 | grep -i warning
# Should produce no output
```

**Frontend Build**:
```bash
# Build frontend
make frontend-build

# Or manually:
cd frontend && pnpm build
# Check for warnings in output
```

**Docker Build**:
```bash
# Build Docker services
make dev-build

# Check for warnings
docker compose build 2>&1 | grep -i warning
# Should produce no output
```

**Requirements**:
- ✅ All builds complete successfully
- ✅ No warnings in build output
- ✅ No errors in build output

**Output**: Clean builds verified

---

### Step 5: Command Output Verification

**Action**: Verify all commands produce clean output

**Test All Commands**:
```bash
# Health check - should show clean status
make dev-health

# Container status - should show clean output
docker compose ps

# Test commands - should show clean output
make test-fast

# Lint commands - should show clean output
make lint
make frontend-lint

# Build commands - should show clean output
make dev-build
make frontend-build
```

**Requirements**:
- ✅ No warnings in command output
- ✅ No errors in command output (unless expected)
- ✅ Clean, readable output
- ✅ Exit codes correct (0 for success)

**Output**: All commands verified with clean output

---

### Step 6: Log Output Verification

**Action**: Verify log outputs are clean

**Docker Logs**:
```bash
# Check Docker logs
make dev-logs-recent

# Should show:
# - No error messages (unless expected)
# - No warning messages
# - Clean, readable log format
```

**Application Logs**:
```bash
# Start services and check logs
make dev-up

# Check logs from each service
make dev-logs-service SERVICE=phoenix
```

**Requirements**:
- ✅ No unexpected errors in logs
- ✅ No warnings in logs (unless expected and documented)
- ✅ Clean log format
- ✅ Appropriate log levels

**Output**: Clean log outputs verified

---

## Quality Checklist

Run through this checklist:

- [ ] Backend linting: No errors, no warnings
- [ ] Frontend linting: No errors, no warnings
- [ ] Backend type checking: No errors, no warnings
- [ ] Frontend type checking: No errors, no warnings
- [ ] Security review: No issues found
- [ ] Backend build: Clean, no warnings
- [ ] Frontend build: Clean, no warnings
- [ ] Docker build: Clean, no warnings
- [ ] All commands: Clean output, no warnings
- [ ] All logs: Clean, no unexpected errors/warnings

---

## Handling Quality Issues

**If Issues Found**:

1. **Fix Immediately**:
   - Don't proceed until all issues fixed
   - Fix warnings, not just errors
   - Ensure clean output from all commands

2. **Document in Issues** (if needed):
   - If issue indicates wider problem
   - If fix requires refactoring
   - Document in `.agent/issues.md`

3. **Re-run Quality Checks**:
   - After fixes, re-run all checks
   - Verify all issues resolved

---

## Exit Criteria

Code quality phase is complete when:

- ✅ All linting passes (no errors, no warnings)
- ✅ All type checking passes (no errors, no warnings)
- ✅ Security review complete (no issues)
- ✅ All builds clean (no warnings)
- ✅ All commands produce clean output (no warnings)
- ✅ All logs clean (no unexpected errors/warnings)
- ✅ Ready for testing phase

---

## Next Phase

After Code Quality, proceed to: **[Testing Workflow](testing-workflow.md)**
