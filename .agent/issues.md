# Development Issues Tracking

This document tracks issues encountered during development work. Issues are categorized by type and status.

## Issue Status

- **Open**: Issue identified, not yet addressed
- **In Progress**: Issue being worked on
- **Resolved**: Issue fixed and verified
- **Deferred**: Issue acknowledged but deferred for later
- **Refactor Needed**: Issue indicates need for architectural refactor

## Issue Template

```markdown
### Issue #[NUMBER]: [Brief Description]

**Status**: [Open/In Progress/Resolved/Deferred/Refactor Needed]
**Phase**: [Discovery/Research/Planning/Implementation/Quality/Testing/Verification]
**Date**: [YYYY-MM-DD]

**Description**:
[Detailed description of the issue]

**Impact**:
[What is affected by this issue]

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Logs/Output**:
```
[Relevant logs or error messages]
```

**Proposed Solution**:
[How to fix this issue]

**Related Issues**:
- Issue #X
- Issue #Y

**Notes**:
[Additional notes or context]
```

---

## Current Issues

### Issue #1: Dead Agent References Still Exist

**Status**: Open
**Phase**: Discovery
**Date**: 2026-01-25

**Description**:
Dead references to non-existent agents (customer_service, image_generator, orchestrator, content_builder) still exist in multiple files despite TECH_STACK_REVIEW indicating they should be removed.

**Impact**:
- Frontend may show "offline" status for non-existent services
- API endpoints may fail if called
- Confusion about what agents actually exist
- Test files reference non-existent agents (may be intentional for testing)

**Locations Found**:
1. `dashboard_api/services.py:58` - Hardcoded `app_name="image_generator"`
2. `frontend/src/api/schemas.ts:6-9` - SystemStatusSchema includes orchestrator, content_builder, image_generator, customer_service
3. `frontend/src/components/StatusPanel.tsx:28-31` - Hardcoded container name mappings
4. `frontend/src/components/GeneratorView.tsx:135` - References `customer_service` agent
5. Test files - Multiple test files reference these agents (may be intentional)

**Expected Behavior**:
- Only existing agents (base_agent, researcher_agent) should be referenced
- UI should dynamically discover agents via API
- No hardcoded agent lists

**Actual Behavior**:
- Dead agent references still exist in frontend code
- StatusPanel has hardcoded mappings for non-existent agents

**Proposed Solution**:
1. Remove dead agent references from `services.py` (or make it dynamic)
2. Update `SystemStatusSchema` to remove dead agent fields (or make dynamic)
3. Update `StatusPanel.tsx` to use dynamic agent discovery
4. Update `GeneratorView.tsx` to use available agents dynamically
5. Review test files - decide if references are needed for testing

**Related Issues**:
- TECH_STACK_REVIEW.md Phase 1: Dead Code Removal

---

### Issue #2: Verification of TECH_STACK_REVIEW Status

**Status**: Resolved
**Phase**: Discovery
**Date**: 2026-01-25
**Resolved Date**: 2026-01-25

**Description**:
Verifying status of items marked as complete in TECH_STACK_REVIEW.md

**Findings**:

✅ **Completed**:
- `load_agent_from_yaml()` function - ✅ REMOVED (no function definition found)
- Dockerfile.agent - ✅ FIXED (uses correct `agent.server:app` entry point)
- Agent discovery - ✅ VERIFIED (API uses AgentRegistry, frontend uses API discovery)

⚠️ **Needs Work**:
- Dead agent references - ⚠️ STILL EXIST (see Issue #1)
- UI dynamic discovery - ⚠️ PARTIAL (AgentsView uses API, but StatusPanel has hardcoded references)

**Impact**:
- Some cleanup work remains
- Documentation may be misleading about completion status

**Proposed Solution**:
- Complete removal of dead agent references (Issue #1) - ⏭️ **PENDING: Still needs work**
- Update TECH_STACK_REVIEW.md with actual verification status ✅ **COMPLETED**
- Mark items as "Verified Complete" or "Needs Work" based on findings ✅ **COMPLETED**

**Resolution**:
- TECH_STACK_REVIEW.md updated with verification results and status
- Documentation updated with "Last verified: 2026-01-25" dates in ARCHITECTURE.md and DEVELOPMENT.md
- ARCHITECTURE.md clarified base_agent vs researcher_agent purpose
- All verifiable items have been checked and documented
- Remaining work: Dead agent references cleanup (tracked in Issue #1)

---

## Resolved Issues

### Issue #2: Verification of TECH_STACK_REVIEW Status

**Status**: Resolved
**Resolved Date**: 2026-01-25
**Resolution**: Completed verification of all items in TECH_STACK_REVIEW.md, updated documentation with verification status, added "Last verified" dates to key docs, and clarified base_agent purpose. Remaining dead agent references tracked in Issue #1.

---

## Refactoring Needed

### Issue #[NUMBER]: [Brief Description]

**Status**: Refactor Needed
**Phase**: [Phase where identified]
**Date**: [YYYY-MM-DD]

**Description**:
[Issue that indicates need for architectural refactor]

**Refactoring Plan**:
[Plan for refactoring]

**Priority**: [High/Medium/Low]

---

## Notes

- Issues should be documented as soon as they are encountered
- If an issue indicates a wider architectural problem, mark as "Refactor Needed"
- Resolved issues should be moved to "Resolved Issues" section
- Review this document regularly to track progress

---

### Issue #3: Chat API Contract Mismatch (Streaming vs JSON)

**Status**: Resolved
**Phase**: Implementation
**Date**: 2026-02-06
**Resolved Date**: 2026-02-06

**Description**:
Frontend chat client expected newline-delimited streaming events, but backend `/api/chat/{name}` returned a single JSON response after runner completion.

**Impact**:
- Inconsistent UX (partial events could not render as intended)
- Contract confusion across frontend/backend

**Resolution**:
- Backend now emits NDJSON streaming events from `/api/chat/{name}`.
- Frontend parser now handles `agent_thought` events, so agent responses render in chat history.
- Router tests updated to assert streaming payload shape.

**Follow-ups**:
- Add cancellation support from frontend to backend stream.
- Add endpoint-level OpenAPI examples for event payloads.

---

## Discovery Backlog (Iterative)

Items discovered during implementation/review to iterate on next.

1. **P0**: Add auth dependency enforcement to sensitive dashboard routes (docker/system operations currently appear open).
2. **P1**: Replace static baseline agent list in frontend with dynamic `/api/agents` discovery.
3. **P1**: Add integration test for end-to-end chat stream behavior (router + frontend parser contract).
4. **P2**: Introduce request cancellation/abort handling for chat stream in `useAgentChat`.
5. **P2**: Add telemetry event for stream errors to improve observability.

### Issue #4: Codex Environment Gaps Block Full Dev Loop

**Status**: Resolved
**Phase**: Verification
**Date**: 2026-02-06
**Resolved Date**: 2026-02-06

**Description**:
Developers needed a repeatable way to identify whether Docker/Playwright/tooling prerequisites are present in Codex-style environments.

**Resolution**:
- Added `scripts/codex_preflight.sh` to validate local prerequisites and surface actionable fixes.
- Added `make codex-preflight` target.
- Added `docs/CODEX_DEVELOPMENT.md` with full-stack and constrained-environment workflows.

**Follow-ups**:
- Add CI preflight stage that mirrors `codex_preflight.sh` checks.

### Issue #5: Preflight Needed Strict Mode for Full-Stack Codex Development

**Status**: Resolved
**Phase**: Verification
**Date**: 2026-02-06
**Resolved Date**: 2026-02-06

**Description**:
The original preflight command surfaced warnings but could still pass when Docker or Playwright were missing, which was confusing when users specifically wanted full-stack development readiness.

**Resolution**:
- Added strict flags (`--require-docker`, `--require-playwright`) in `scripts/codex_preflight.sh`.
- Added `make codex-preflight-full` target for strict full-stack checks.
- Updated Codex development docs to clarify quick-check vs strict-check behavior.

**Follow-ups**:
- Mirror strict preflight in a dedicated CI job for reproducible environment gating.
