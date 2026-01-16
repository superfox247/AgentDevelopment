# Project Tracker & Feedback Loop

**This document represents the shared state between USER (Aaron) and AGENT (Antigravity).**
It serves as the top-down feedback mechanism.

## 🟢 Active Directives (User Intent)
*(User: Update this section to change my priorities)*

> "The project tracker to be used as a top down feedback loop from me to you."
> "Reorganise and consolidate docs, remove old parts."
> "Report problems encountered in the project tracker... we want a process that is fully automated and doesn't error or show warnings."
> "Issues found during development must be logged here as well."

## 🔴 Issue Log & Friction Points
*Automated log of strict deviations, errors, and warnings. All items here trigger a mandatory refactor or fix.*

| Date | Severity | Description | Status |
| :--- | :--- | :--- | :--- |
| **Jan 16** | 🔴 **High** | `make` command missing on Windows. Replaced with `reset_dev_env.ps1`. | **Resolved** |
| **Jan 16** | 🟡 **Medium** | Linting violations: 91 `ruff` errors + 36 `mypy` errors. Violation of "Zero Tolerance". | **Resolved** |
| **Jan 16** | 🟡 **Medium** | UI/Agent Coupling. Orchestrator was serving HTML. Separated into `apps/web`. | **Resolved** |
| **Jan 16** | 🔴 **High** | Broken Dependency: `google-adk==1.18.0` required non-existent `a2a-sdk`. Upgraded to `1.22.1`. | **Resolved** |

## 🔵 Agent Focus (Current Status)
**Status:** `QUALITY_ASSURANCE`
**Current Task:** Enforcing "Zero Tolerance" via automated checks.

**Recent Accomplishments:**
-   [x] **Monorepo Structure**: Established `apps/`, `domains/`, `agent_platform/`, and `registry/`.
-   [x] **UI Decoupling**: Moved Frontend to `apps/web` (Nginx), decoupled from Orchestrator (API).
-   [x] **Agent Debug Dashboard**: Created a timeline-based internal tool for debugging agent flows.
-   [x] **Architecture codified**: Rewrote [`ARCHITECTURE.md`](file:///c:/Users/Aaron/Workspace2/course-creation-ai-agent-architecture/ARCHITECTURE.md) to explain the platform shift.
-   [x] **Constitution affirmed**: `GEMINI.md` is the immutable law for the factory.
- [x] **Artifact Persistence**: Enabled `FileArtifactService` to save agent outputs to `./artifacts`.
- [x] **Tooling Upgrade**: Upgraded `google-adk` to v1.22.1 (Latest) and fixed dependencies.

## 🗺️ Roadmap

### Immediate Focus: Platform Hardening
-   [ ] **Prompt Governance**: Move prompts from code to `.agent/prompts/`.
-   [ ] **Schema Enforcement**: Implement `registry/models/protocol.py` for strict A2A typing.
-   [ ] **Secret Management Check**: Ensure CI enforces `.env.example` parity.

### Future: Expansion
-   [ ] **New Domain**: Create `domains/coding_assistant` (Proof of Multi-Tenancy).
-   [ ] **Meta-Agent**: Implement "Factory Overseer".

## 📚 Reference & Standards

| Document | Purpose |
| :--- | :--- |
| **[`GEMINI.md`](file:///c:/Users/Aaron/Workspace2/course-creation-ai-agent-architecture/GEMINI.md)** | **The Constitution.** Immutable rules for the Agent Factory. |
| **[`ARCHITECTURE.md`](file:///c:/Users/Aaron/Workspace2/course-creation-ai-agent-architecture/ARCHITECTURE.md)** | **The Blueprint.** Explains "Platform vs Domain" and the "4 Rules" of development. |
| **[`.agent/workflows/`](file:///c:/Users/Aaron/Workspace2/course-creation-ai-agent-architecture/.agent/workflows)** | **Standard Procedures.** How to build, test, and review. |

## 📜 Complete History (Archived)
**Phase 1: Factory Foundation (Jan 2026)**
-   Transitioned from "Prototype" to "Agent Factory".
-   Centralized `platform/` (Auth, Observability).
-   Migrated all legacy agents to `domains/course_creator`.
-   Established Universal Dockerfile & Makefile.
