# Technical Debt

**Last Updated**: 2026-02-07

Canonical debt/simplification backlog:

- [Refactoring and Simplification Backlog](REFACTORING_SIMPLIFICATION.md)

Planned work:

- [Roadmap](ROADMAP.md)

Active implementation issues:

- [.agent/issues.md](../.agent/issues.md)

## Current Priority Snapshot

| Priority | Theme | Canonical Item |
| :--- | :--- | :--- |
| High | CI/CD and runtime correctness | `R-001`, `R-002`, `R-003`, `R-004` |
| Medium | Context-engine maintainability | `R-005`, `R-006` |
| Medium | Docs/automation drift control | `R-007` |
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
