# Technical Debt

**Last Updated**: 2026-02-07

Canonical debt/simplification backlog:

- [Refactoring and Simplification Backlog](REFACTORING_SIMPLIFICATION.md)

Planned work:

- [Roadmap](ROADMAP.md)

Active implementation issues:

- [.agent/issues.md](../.agent/issues.md)

## Current Priority Snapshot

> **Note:** All initial high-priority technical debt items (R-001 through R-008) have been completed as of 2026-02-07. Please refer to `docs/REFACTORING_SIMPLIFICATION.md` for the historical record and any new initiatives.

| Priority | Theme | Canonical Item |
| :--- | :--- | :--- |
| High | CI/CD and runtime correctness | Completed |
| Medium | Context-engine maintainability | Completed |
| Medium | Docs/automation drift control | Completed |
| Low | Cross-platform command duplication | Completed (`R-008`) |

Use `docs/REFACTORING_SIMPLIFICATION.md` for detailed actions and sequencing.

## Debt Management Flow

```mermaid
flowchart LR
    Intake[Debt identified] --> Classify[Classify by risk/theme]
    Classify --> Prioritize[Map to R-item and priority]
    Prioritize --> Implement[Implement and validate]
    Implement --> Verify[Update docs/backlog status]
    Verify --> Closed[Closed + archived context]
```

## Theme Map

```mermaid
flowchart TD
    High[High priority] --> T1[CI/CD and runtime correctness]
    Medium1[Medium priority] --> T2[Context-engine maintainability]
    Medium2[Medium priority] --> T3[Docs and automation drift control]
    Low[Low priority] --> T4[Cross-platform command duplication]
```
