# Tech Stack & Patterns Review

**Date**: January 25, 2026  
**Purpose**: Review current tech stack, identify deviations, and recommend simplifications/refactorings

## Quick Action Summary

**Critical Issues** (Fix First):
1. 🔴 **Dockerfile broken** - Agents can't run in Docker (CMD references non-existent module)
2. 🔴 **Dead agent references** - Frontend/API reference 4 non-existent agents
3. 🔴 **Unused YAML pattern** - `base_agent` and `load_agent_from_yaml()` are dead code

**Quick Wins** (Low Risk, High Value):
- Remove `base_agent/` directory (~50 lines)
- Remove `load_agent_from_yaml()` function (~18 lines)
- Remove dead agent references from `dependencies.py` (~60 lines)
- Fix Dockerfile CMD and paths

**Estimated Impact**: Remove ~200 lines of dead code, fix broken Docker deployment

---

## Executive Summary

The codebase shows good architectural patterns but contains **dead code**, **unused patterns**, and **outdated references** that should be cleaned up. The main issues are:

1. **Two agent creation patterns** (YAML vs Python) - only Python pattern is used
2. **base_agent template** - minimal value, can be removed
3. **Dead references** to non-existent agents (customer_service, image_generator, orchestrator, content_builder)
4. **Outdated Dockerfile** paths and references

---

## Current Tech Stack

### Backend
- **Framework**: FastAPI 0.115-0.124
- **Agent Framework**: Google ADK 1.22.1+
- **Python**: 3.10-3.13 (project allows 3.10-3.14, platform requires 3.11-3.13)
- **Observability**: Phoenix/OTEL, OpenInference
- **A2A Protocol**: a2a-sdk 0.3.20+
- **Dependencies**: Pydantic 2.0+, Docker SDK, Google Cloud libraries

### Frontend
- **Framework**: React 19.2.3
- **Build Tool**: Vite 7.3.1
- **Language**: TypeScript 5.9.3
- **Styling**: Tailwind CSS 4.1.18
- **State Management**: TanStack Query 5.90.20
- **Testing**: Vitest, Playwright, Testing Library

### Infrastructure
- **Containerization**: Docker, docker-compose
- **Package Management**: uv (Python), pnpm (Node)
- **Linting**: ruff, ESLint
- **Type Checking**: mypy, TypeScript

---

## Current Patterns

### ✅ Standard Pattern (Active)
**Location**: `agents/researcher_agent/`

```python
# agent.py
from google.adk.agents import LlmAgent
root_agent = LlmAgent(
    name="researcher_agent",
    model="gemini-2.0-flash",
    tools=[google_search],
    planner=PlanReActPlanner(),
    # ... callbacks, etc.
)
```

**Structure**:
- `agent.py` with `root_agent` export
- `__init__.py` exports `root_agent`
- Collocated: `tools/`, `callbacks/`, `memory/`, `artifacts/`, `evaluations/`, `tests/`
- Used by: `create_platform_app(adk_app)` where `adk_app = App(root_agent)`

### ❌ Unused Pattern (Dead Code)
**Location**: `agents/base_agent/`

```yaml
# agent.yaml
agent_class: LlmAgent
name: base_agent
model: models/gemini-2.0-flash
tools:
  - name: agents.base_agent.tools.example_tool
```

**Supporting Code**:
- `agent_platform/server.py::load_agent_from_yaml()` - **NEVER CALLED**
- `base_agent/agent.yaml` - template only
- `base_agent/tools.py` - example tool only

**Status**: This pattern is documented but **not used in production**. The workflow docs reference it as a "minimal template" but `researcher_agent` is the actual reference implementation.

---

## Issues & Deviations

### 🔴 High Priority

#### 1. **Unused YAML Agent Pattern**
**Issue**: Two agent creation patterns exist, but only Python pattern is used.

**Evidence**:
- `load_agent_from_yaml()` in `server.py` is never called
- No agents use YAML config in production
- `base_agent` is only a template, not a real agent
- Workflow docs say "use researcher_agent as reference" (Python pattern)

**Impact**: Confusion, maintenance burden, dead code.

**Recommendation**: 
- **Remove** `base_agent/` directory (or convert to Python pattern)
- **Remove** `load_agent_from_yaml()` function
- **Update** workflow docs to remove YAML pattern references
- **Standardize** on Python pattern only

#### 2. **Dead Agent References**
**Issue**: Code references agents that don't exist: `customer_service`, `image_generator`, `orchestrator`, `content_builder`.

**Locations**:
- `frontend/dependencies.py`: `get_customer_service_runner()`, `get_image_generator_runner()` - raise `NotImplementedError`
- `frontend/routers/agents.py`: Uses these runners (will fail)
- `frontend/routers/system.py`: Checks for these services
- `frontend/constants.py`: `ServiceName` enum includes them
- `frontend/models.py`: `SystemStatus` includes them
- `frontend/src/components/StatusPanel.tsx`: UI displays them
- `docker-compose.yml`: Comments reference removed services

**Impact**: 
- Frontend will show "offline" for non-existent services
- API endpoints will fail if called
- Confusion about what agents actually exist

**Recommendation**:
- **Remove** all references to non-existent agents
- **Keep** only `researcher_agent` references
- **Add** new agents only when implemented
- **Update** UI to dynamically discover agents

#### 3. **Broken Dockerfile**
**Issue**: `agent_platform/Dockerfile.agent` has multiple problems:
1. Copies agent to `/app/orchestrator` (hardcoded name)
2. CMD references `orchestrator.server:app` which doesn't exist
3. Agents don't have `server.py` files - they need to be created

**Evidence**:
```dockerfile
# Line 37-40: Hardcoded destination path
COPY ${AGENT_PATH} /app/orchestrator

# Line 48: Comment mentions 'orchestrator' 
# Add /app to PYTHONPATH so we can import 'agent_platform', 'registry', and 'orchestrator'

# Line 61: References non-existent module
CMD ["uvicorn", "orchestrator.server:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Current Agent Pattern**:
- Agents have `agent.py` with `root_agent`
- Agents use `create_platform_app()` from `agent_platform.server`
- **Missing**: Agents don't have `server.py` entry points

**Impact**: 
- Dockerfile **will not work** - container will fail to start
- No way to run agents in Docker currently

**Recommendation**:
- **Option A**: Each agent needs a `server.py` that creates the app:
  ```python
  # agents/<agent_name>/server.py
  from google.adk.apps import App
  from agent_platform.server import create_platform_app
  from .agent import root_agent
  
  adk_app = App(root_agent=root_agent)
  app = create_platform_app(adk_app, description="...")
  ```
- **Option B**: Create a generic entry point that discovers the agent dynamically
- **Update** Dockerfile to use correct path and module
- **Fix** CMD to reference actual entry point

### 🟡 Medium Priority

#### 4. **Python Version Mismatch**
**Issue**: Root `pyproject.toml` allows Python 3.10-3.14, but `agent_platform/pyproject.toml` requires 3.11-3.13.

**Impact**: Potential confusion about supported versions.

**Recommendation**: Align versions or document why they differ.

#### 5. **Architecture Docs Outdated**
**Issue**: `docs/ARCHITECTURE.md` references "Base Agent" and old service names.

**Evidence**:
- Diagram shows "Base Agent" in agent fleet
- Mentions services that don't exist
- References "domains/" structure (migrated to "agents/")

**Recommendation**: Update architecture docs to reflect current state.

#### 6. **Test Files Reference base_agent**
**Issue**: `agents/base_agent/test_*.py` tests a template, not production code.

**Impact**: Tests run but test non-functional code.

**Recommendation**: Remove if `base_agent` is removed, or convert to Python pattern.

### 🟢 Low Priority

#### 7. **Inconsistent Agent Discovery**
**Issue**: No dynamic agent discovery - hardcoded lists everywhere.

**Impact**: Must manually update multiple files when adding agents.

**Recommendation**: Create agent registry/discovery mechanism.

#### 8. **Duplicate Exception Handlers**
**Issue**: Same exception handlers in `agent_platform/server.py` and `frontend/server.py`.

**Impact**: Code duplication (minor).

**Recommendation**: Extract to shared middleware (if not already done - check `middleware.py`).

---

## Simplification Opportunities

### 1. **Remove base_agent Template**
**Rationale**: 
- Not used in production
- `researcher_agent` is the actual reference
- YAML pattern is unused

**Action**:
```bash
# Remove base_agent directory
rm -rf agents/base_agent/

# Remove load_agent_from_yaml() from server.py
# Update workflow docs
```

**Files to Update**:
- `agents/base_agent/` (delete)
- `agent_platform/server.py` (remove function)
- `.agent/workflows/agent-development.md` (update references)
- `docs/ARCHITECTURE.md` (remove mentions)

### 2. **Clean Up Dead Agent References**
**Rationale**: 
- Prevents confusion
- Reduces maintenance burden
- Makes actual agents clear

**Action**:
- Remove `get_customer_service_runner()` and `get_image_generator_runner()` from `dependencies.py`
- Remove endpoints that use them from `routers/agents.py`
- Remove from `ServiceName` enum
- Remove from `SystemStatus` model
- Update UI components to not display them
- Update `system.py` to not check for them

**Files to Update**:
- `frontend/dependencies.py`
- `frontend/routers/agents.py`
- `frontend/routers/system.py`
- `frontend/constants.py`
- `frontend/models.py`
- `frontend/src/components/StatusPanel.tsx`
- `frontend/src/api/schemas.ts`

### 3. **Fix Dockerfile**
**Rationale**: 
- Won't work with current structure
- Blocks deployment

**Action**:
- Update to use agent entry point pattern
- Fix paths and CMD
- Document expected structure

**Files to Update**:
- `agent_platform/Dockerfile.agent`

### 4. **Standardize Agent Pattern**
**Rationale**: 
- Single pattern is easier to maintain
- Clearer for new developers

**Action**:
- Document Python pattern as the only pattern
- Remove YAML pattern references
- Update all docs

---

## Recommended Refactoring Order

### Phase 1: Remove Dead Code (Low Risk)
1. ✅ Remove `base_agent/` directory
2. ✅ Remove `load_agent_from_yaml()` function
3. ✅ Remove dead agent references from dependencies/routers
4. ✅ Update workflow docs

### Phase 2: Fix Infrastructure (Medium Risk)
5. ✅ Fix Dockerfile paths and CMD
6. ✅ Update architecture docs
7. ✅ Align Python version requirements

### Phase 3: Improve Architecture (Higher Risk)
8. ⚠️ Add dynamic agent discovery
9. ⚠️ Refactor UI to discover agents dynamically
10. ⚠️ Create agent registry

---

## Current State Summary

### What Exists
- ✅ `researcher_agent` - Full Python-based agent (reference implementation)
- ✅ `agent_platform/` - Shared platform code
- ✅ `frontend/` - React dashboard
- ✅ Docker infrastructure
- ✅ Observability stack

### What Doesn't Exist (But Referenced)
- ❌ `customer_service` agent
- ❌ `image_generator` agent  
- ❌ `orchestrator` agent
- ❌ `content_builder` agent
- ❌ YAML-based agents (pattern exists but unused)

### Patterns in Use
- ✅ Python-based agent creation (`agent.py` with `root_agent`)
- ✅ Collocated structure (tools, callbacks, memory, etc.)
- ✅ FastAPI + ADK Runner pattern
- ✅ A2A protocol integration

### Patterns Not in Use
- ❌ YAML-based agent creation
- ❌ `load_agent_from_yaml()` function
- ❌ `base_agent` template (only for reference)

---

## Metrics

- **Dead Code**: ~200 lines (base_agent, load_agent_from_yaml, dead references)
- **Outdated References**: ~50 locations across 15+ files
- **Pattern Confusion**: 2 patterns (1 unused)
- **Maintenance Burden**: High (must update multiple files for new agents)

---

## Next Steps

1. **Review this document** with team
2. **Prioritize** which refactorings to do first
3. **Create tickets** for each phase
4. **Start with Phase 1** (low risk, high value)
5. **Test thoroughly** after each phase

---

## Questions Resolved ✅

1. **Should we keep `base_agent` as a minimal template, or remove it entirely?**
   - ✅ **Decision**: Remove it entirely
   - ✅ **Status**: Completed - `base_agent/` directory removed
   - **Rationale**: `researcher_agent` serves as the reference implementation

2. **Do we want to support YAML-based agents in the future, or standardize on Python?**
   - ✅ **Decision**: Standardize on Python only
   - ✅ **Status**: Completed - YAML pattern removed, all docs updated
   - **Rationale**: YAML pattern misses functionality, Python pattern is more flexible and feature-complete

3. **Should we implement dynamic agent discovery now, or wait?**
   - ✅ **Decision**: Implement now
   - ✅ **Status**: Completed - Agent registry system created
   - **Rationale**: Will have many agents in the future, need scalable discovery
   - **Implementation**: Created `frontend/utils/agent_registry.py` with AST-based metadata extraction

4. **What's the timeline for implementing the missing agents (customer_service, etc.)?**
   - ✅ **Decision**: After research agent works and codebase is documented/working to enterprise standards
   - **Status**: All dead references removed, ready for future agents
   - **Next Steps**: Focus on researcher_agent stability and documentation

---

## Implementation Summary

### ✅ Phase 1: Dead Code Removal (Complete)
- Removed `base_agent/` directory
- Removed `load_agent_from_yaml()` function
- Removed all dead agent references
- Updated all documentation

### ✅ Phase 2: Infrastructure Fixes (Complete)
- Fixed Dockerfile paths and CMD
- Created `server.py` entry point pattern for agents
- Updated architecture docs

### ✅ Phase 3: Dynamic Agent Discovery (Complete)
- Created `AgentRegistry` utility class
- Implemented AST-based metadata extraction from `agent.py`
- Updated `/api/agents` endpoint to use registry
- Added backward-compatible legacy endpoint
- System now automatically discovers agents without manual updates

### 📋 Remaining Work
- Test agent registry with multiple agents
- Add agent metadata endpoint (description, model, etc.)
- Update frontend to display richer agent metadata
- Document agent registry usage in workflow docs
