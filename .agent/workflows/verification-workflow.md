---
description: Verification workflow - final verification in deployed environment
---

# Verification Workflow

**Phase**: Final Verification  
**Purpose**: Final verification that everything works in the deployed environment.

## Objectives

1. Reset dev environment to clean state
2. Start full stack (Docker + API + Frontend)
3. Verify all services healthy
4. Run E2E tests against deployed stack
5. Manual UI verification (if applicable)
6. Verify clean logs from all services

## Steps

### Step 1: Reset Development Environment

**Action**: Reset environment to clean state

**Commands**:
```bash
# Full reset (stops, removes volumes, rebuilds, starts)
make dev-reset
```

**This will**:
- Stop all containers
- Remove volumes (clean state)
- Rebuild all images (no cache)
- Start containers
- Wait for services to be healthy
- Show logs during process

**Verify**:
- Check output for any errors
- Verify containers started
- Check initial logs

**Output**: Clean environment reset and started

---

### Step 2: Verify Docker Services

**Action**: Verify all Docker services are healthy

**Commands**:
```bash
# Check health of all services
make dev-health

# View container status
docker compose ps

# View recent logs
make dev-logs-recent
```

**Verify**:
- ✅ All containers running
- ✅ Health checks passing
- ✅ No errors in logs
- ✅ No warnings in logs

**Output**: All Docker services healthy

---

### Step 3: Start API and Frontend Servers

**Action**: Start API and frontend servers (separate terminals)

**Terminal 1 - Dashboard API**:
```bash
uv run python dashboard_api/server.py
```

**Terminal 2 - Frontend**:
```bash
cd frontend && pnpm dev
```

**Verify**:
- ✅ API server starts without errors
- ✅ Frontend server starts without errors
- ✅ No warnings in startup logs
- ✅ Services accessible (API on 8010, Frontend on 5173)

**Output**: API and frontend servers running

---

### Step 4: Verify Service Health

**Action**: Verify all services are healthy and accessible

**Commands**:
```bash
# Check health endpoints
curl http://localhost:8010/health
curl http://localhost:6006/health

# Or use health check script
uv run python scripts/health_check.py
```

**Verify**:
- ✅ Dashboard API healthy
- ✅ Phoenix healthy
- ✅ All Docker services healthy
- ✅ All services accessible

**Output**: All services verified healthy

---

### Step 5: Run E2E Tests Against Deployed Stack

**Action**: Run E2E tests against the actual deployed stack

**Commands**:
```bash
# Run E2E tests
make frontend-e2e-docker

# Or manually
cd frontend && pnpm exec playwright test --config=playwright.docker.config.ts
```

**Verify**:
- ✅ All E2E tests pass
- ✅ Tests run against deployed stack
- ✅ No test failures
- ✅ Clean test output

**Log Viewing**:
```bash
# View logs during/after tests
make dev-logs-recent
make dev-logs-service SERVICE=phoenix
```

**If Failures**:
- Review E2E test output
- Check all service logs
- Fix issues and retry

**Output**: All E2E tests passing

---

### Step 6: Manual UI Verification (if applicable)

**Action**: Manually verify UI if needed

**Tasks**:
1. Open browser to `http://localhost:5173`
2. Navigate through key features
3. Verify functionality works
4. Check for console errors
5. Verify API calls work

**Verify**:
- ✅ UI loads correctly
- ✅ Features work as expected
- ✅ No console errors
- ✅ API integration works

**Output**: UI verified manually

---

### Step 7: Verify Clean Logs

**Action**: Verify all logs are clean

**Check All Log Sources**:

1. **Docker Logs**:
   ```bash
   make dev-logs-recent
   ```

2. **API Server Logs**:
   - Check terminal where API server is running
   - Should show clean startup, no errors

3. **Frontend Server Logs**:
   - Check terminal where frontend server is running
   - Should show clean startup, no errors

4. **Service Health Logs**:
   ```bash
   make dev-health
   ```

**Verify**:
- ✅ No unexpected errors
- ✅ No warnings (unless expected and documented)
- ✅ Clean, readable log format
- ✅ Appropriate log levels

**Output**: All logs verified clean

---

### Step 8: Final System Check

**Action**: Final comprehensive system check

**Commands**:
```bash
# Full verification (includes everything)
make dev-verify
```

**This runs**:
- Linting
- Building
- Testing
- E2E tests
- Health checks

**Verify**:
- ✅ All checks pass
- ✅ Clean output
- ✅ No warnings
- ✅ System fully operational

**Output**: Complete system verified

---

## Verification Checklist

Run through this checklist:

- [ ] Environment reset successfully
- [ ] All Docker services healthy
- [ ] API server running and healthy
- [ ] Frontend server running and healthy
- [ ] All health checks passing
- [ ] E2E tests passing against deployed stack
- [ ] Manual UI verification complete (if applicable)
- [ ] All Docker logs clean
- [ ] API server logs clean
- [ ] Frontend server logs clean
- [ ] Final system check passes

---

## Exit Criteria

Verification is complete when:

- ✅ Environment reset and clean
- ✅ All services running and healthy
- ✅ All E2E tests passing
- ✅ Manual verification complete (if applicable)
- ✅ All logs clean
- ✅ System fully operational
- ✅ Ready for completion

---

## Completion

After verification completes:

1. **Update Documentation** (if needed):
   - Update any docs that changed
   - Add usage examples if new features

2. **Update Issue Tracking**:
   - Close resolved issues in `.agent/issues.md`
   - Document any remaining issues

3. **Update system tracking**: Add run to `.agent/system-tracking.md` (what worked, issues, suggestions).

4. **Mark work complete**:
   - All phases complete
   - All checks passing
   - System verified
   - Documentation updated

---

## Next Steps

After verification:

- Work is complete and ready
- System is verified and operational
- Documentation is updated
- Issues are tracked
- System tracking updated
