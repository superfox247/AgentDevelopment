# Changelog

Notable changes. [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

- Planned: [ROADMAP.md](docs/ROADMAP.md)

---

## [2026-01-25]

### Added

- Agent Registry (AST metadata, `GET /api/agents/{name}/metadata`), AgentsView metadata
- Smart test runner `run_tests.py` (early exit, agent-specific, `--skip-evals`)
- Improvement tracking: IMPROVEMENT_ORGANIZATION, TECHNICAL_DEBT, CHANGELOG, [adr/](docs/adr/)

### Changed

- Doc maintenance: root = `README.md` only; immediate cleanup after work
- System review workflow, `.agent/issues.md` tracking
- **System tracking & lessons**: Combined into [.agent/system-tracking.md](.agent/system-tracking.md); runs, what worked, durable lessons in one place. Removed `docs/LESSONS_LEARNED.md`.
- **Workflows**: Aligned main-development, verification, discovery, workflows README—all point to system-tracking for runs + lessons; shortened tracking steps.
- IMPROVEMENT_ORGANIZATION, README: updated for combined system-tracking.

### Fixed

- Doc cleanup: removed 7 duplicate root files (already in archive)
- Dead agent refs: tracked (Issue #1), locations documented

### Removed

- Root duplicates: AUTOMATION_*, IMPLEMENTATION_SUMMARY, TECH_STACK_REVIEW, TEST_* (archived or merged into TESTING.md)
- `docs/LESSONS_LEARNED.md` (merged into system-tracking)

---

## Previous

- `docs/archive/2026-01/` · `.agent/SYSTEM_REVIEW_2026-01-25.md`

---

Update: Add under `[Unreleased]`; use Added, Changed, Fixed, Removed, Security; link issues when possible.
