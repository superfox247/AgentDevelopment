# Improvement Organization

**Last Updated**: 2026-01-25

How we track improvements, debt, and changes. Single source per topic.

## Systems

| System | Location | Purpose |
| :--- | :--- | :--- |
| **ROADMAP** | [ROADMAP.md](ROADMAP.md) | Planned work, priorities |
| **Issues** | [.agent/issues.md](../.agent/issues.md) | Active bugs, blockers |
| **Technical debt** | [TECHNICAL_DEBT.md](TECHNICAL_DEBT.md) | Refactors, known debt |
| **CHANGELOG** | [../CHANGELOG.md](../CHANGELOG.md) | Completed changes |
| **ADRs** | [adr/](adr/) | Architecture decisions |
| **System tracking & lessons** | [.agent/system-tracking.md](../.agent/system-tracking.md) | Runs, what worked, durable lessons |
| **Archive** | [archive/](archive/) | Completed summaries |

## Lifecycle

`Identified` → `Prioritized` (ROADMAP) → `In progress` (issues) → `Done` (CHANGELOG) → `Archived`

- **Identify**: Add to issues or TECHNICAL_DEBT.
- **Prioritize**: Add to ROADMAP with priority.
- **Complete**: Update CHANGELOG; archive summaries.
- **Decisions**: Record in `docs/adr/` when they affect architecture.
- **Lessons**: Capture per-run in [system-tracking](../.agent/system-tracking.md); extract durable lessons when appropriate.

## Categories

Code quality · Architecture · Documentation · Process · Infrastructure · UX

## Related

[DOCUMENTATION_MAINTENANCE.md](DOCUMENTATION_MAINTENANCE.md) · [.agent/system-tracking.md](../.agent/system-tracking.md)
