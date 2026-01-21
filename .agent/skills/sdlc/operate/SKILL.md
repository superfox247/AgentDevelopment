---
name: Operate Branch
description: Monitoring, debugging, incident response
---

# Operate Skills

## Sub-Skills
- `monitor/` - Logs, metrics, alerts
- `debug/` - Root cause analysis, fixes
- `incident/` - Outage response, postmortems

---

## Debug Protocol

### 1. Gather Information
```bash
# Check container status
docker ps -a

# View logs for all containers  
docker compose logs --tail=50

# View specific container logs
docker logs <container_name> --tail=100
```

This collects:
- Recent logs (all containers)
- System resource usage
- Service health status

### 2. Identify Error Pattern
Look for:
- Stack traces in logs
- Repeated error messages
- Timing correlations

### 3. Trace to Source
```bash
# Search for error in codebase
rg "ErrorClassName" --type py

# Check recent changes
git log --oneline -20
```

### 4. Fix and Verify
1. Make the fix
2. Run targeted tests
3. Verify in logs

### 5. Document
Update knowledge base with:
- Root cause
- Solution applied
- Prevention measures

---

## Log Analysis Patterns

### Finding Errors
```bash
# Docker logs for errors
docker logs <container> 2>&1 | Select-String -Pattern "ERROR|WARN"

# Python exceptions
docker logs <container> 2>&1 | Select-String -Pattern "Traceback"
```

### Common Log Patterns

| Pattern | Meaning | Action |
|---------|---------|--------|
| `ConnectionRefused` | Service not running | Check docker-compose |
| `TimeoutError` | Slow dependency | Check network/load |
| `ValidationError` | Bad input data | Check request format |
| `PermissionDenied` | Auth issue | Check credentials |

---

## Incident Response Checklist

### Immediate (0-5 min)
- [ ] Acknowledge incident
- [ ] Assess impact (users affected?)
- [ ] Start incident log

### Triage (5-15 min)
- [ ] Identify failing component
- [ ] Check recent deployments
- [ ] Review error logs
- [ ] Attempt quick mitigations

### Resolution (15+ min)
- [ ] Apply fix
- [ ] Verify fix in production
- [ ] Monitor for recurrence

### Postmortem
- [ ] Timeline of events
- [ ] Root cause analysis
- [ ] Action items to prevent recurrence

---

## Postmortem Template

```markdown
# Incident Report: [YYYY-MM-DD] [Brief Title]

## Summary
What happened, when, and impact.

## Timeline
- HH:MM - Incident detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix deployed
- HH:MM - Incident resolved

## Root Cause
Technical explanation of what failed.

## Resolution
What was done to fix it.

## Action Items
- [ ] [Preventive measure 1]
- [ ] [Preventive measure 2]

## Lessons Learned
What can we do better next time?
```
